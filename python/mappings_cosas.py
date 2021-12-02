#'////////////////////////////////////////////////////////////////////////////
#' FILE: mappings_cosas.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-10-05
#' MODIFIED: 2021-12-01
#' PURPOSE: primary mapping script for COSAS
#' STATUS: working
#' PACKAGES: **see below**
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

import molgenis.client as molgenis
from datatable import dt, f, as_type, first
from urllib.parse import quote_plus
from datetime import datetime
import json
import requests
import re
import numpy as np

# extend molgenis.Session class
class molgenis(molgenis.Session):
    """molgenis
    An extension of the molgenis.client class
    """
    
    # update_table
    def update_table(self, entity: str, data: list):
        """Update Table
        
        When importing data into a new table using the client, there is a 1000
        row limit. This method allows you push data without having to worry
        about the limits.
        
        @param entity (str) : name of the entity to import data into
        @param data (list) : data to import
        
        @return a status message
        """
        props = list(self.__dict__.keys())
        if '_url' in props: url = self._url
        if '_api_url' in props: url = self._api_url
        url = f'{url}v2/{quote_plus(entity)}'
        
        # single push
        if len(data) < 1000:
            try:
                response = self._session.post(
                    url = url,
                    headers = self._get_token_header_with_content_type(),
                    data = json.dumps({'entities' : data})
                )
                if not response.status_code // 100 == 2:
                    return f'Error: unable to import data({response.status_code}): {response.content}'
                
                return f'Imported {len(data)} entities into {str(entity)}'
            except requests.exceptions.HTTPError as err:
                raise SystemError(err)
        
        # batch push
        if len(data) >= 1000:    
            for d in range(0, len(data), 1000):
                try:
                    response = self._session.post(
                        url = url,
                        headers = self._get_token_header_with_content_type(),
                        data = json.dumps({'entities': data[d:d+1000] })
                    )
                    if not response.status_code // 100 == 2:
                        raise response.raise_for_status()

                    return f'Batch {d}: Imported {len(data)} entities into {str(entity)}'
                except requests.exceptions.HTTPError as err:
                    raise SystemError(f'Batch {d} Error: unable to import data:\n{str(err)}')

    # batch_update_one_attr
    def batch_update_one_attr(self, entity: str, attr: str, data: list):
        """Batch Update One Attribute
        
        Import data for an attribute in batches (i.e., into groups of 1000 entities).
        Data should be a list of dictionaries with two keys: `id` and <attr> where
        attr is the name of the attribute that you would like to update
        
        @param data (list) : data to import
        @param attr (str) : name of the attribute to update
        @param entity (str) : name of the entity to import data into
        
        @return a response code
        """
        props = self.__dict__.keys()
        if '_url' in props: url = self._url
        if '_api_url' in props: url = self._api_url
        url = f'{url}v2/{quote_plus(entity)}/{attr}'
        
        for d in range(0, len(data), 1000):
            try:
                response = self._session.put(
                    url = url,
                    headers = self._get_token_header_with_content_type(),
                    data = json.dumps({'entities': data[d:d+1000] })
                )
                
                if not response.status_code // 100 == 2:
                    raise response.raise_for_status()
                
                return f'Batch {d}: Imported {len(data)} entities into {str(entity)}' 
            except requests.exceptions.HTTPError as err:
                raise SystemError(f'Batch {d} Error: unable to import data:\n{str(err)}')

# create status message
def status_msg(*args):
    """Status Message
    
    Prints a message with a timestamp
    
    @param *args : message to write 
    
    @example
    status_msg('hello world')
    
    """
    msg = ' '.join(map(str, args))
    t = datetime.utcnow().strftime('%H:%M:%S.%f')[:-3]
    print('\033[94m[' + t + '] \033[0m' + msg)
    
# create class of methods used in the mappings
class cosasUtils:
    def calculate_age(earliest = None, recent = None):
        """Calculate Years of Age between two dates
        
        @param earliest : the earliest date (datetime: yyyy-mm-dd)
        @param recent : the most recent date (datetime: yyyy-mm-dd)
        
        @return int; years of age
        """
        if earliest is None or recent is None:
            return None

        return round(int((recent - earliest).days) / 365.25, 4)
    
    def extract_phenotypicCodes(id, column):
        """Extract Phenotypic Codes
        
        In the COSAS Clinical table, we need to extract the phenotypic codes from
        a list of unique phenotypic codes by column name.
        
        @param     id : identifier to search for
        @param column : name of the column to search for (datatable f-expression)
        
        @example
        extract_phenotypicCodes('00000', f.mycolumn)
        """
        values = list(filter(None, clinical[f.belongsToSubject == id, column].to_list()[0]))
        unique = list(set(values))
        return ','.join(unique)
    
    def extract_testCodes(subjectID, sampleID, requestID, column):
        """Extract and collapse test codes from the column `alternativeIdentifers`
        
        @param subjectId (str) : subject ID to locate
        @param sampleId  (str) : sample ID to locate
        @param requestId (str) : specific request associated with a sample
        @param column    (str) : name of the column where the codes are stored
        """
        values = list(
            filter(
                None, 
                samples[
                    (f.belongsToSubject == subjectID) &
                    (f.sampleID == sampleID) &
                    (f.belongsToRequest == requestID),
                    column
                ]
            )
        )
        unique = list(set(values))
        return ','.join(unique)
        
    def format_asYear(date: datetime.date = None):
        """Format Date as Year"""
        if date is None or str(date) == 'nan':
            return None

        return date.strftime('%Y')

    def format_date(date: str, pattern = '%Y-%m-%d %H:%M:%S', asString = False) -> str:
        """Format Date String
        
        Format date string to yyyy-mm-dd format
        
        @param string : date string
        @param pattern : date format, default: %Y-%m-%d %H:%M:%S
        @param asString : If True, the result will be returned as string
        
        @return date
        """
        if not date or str(date) == 'nan':
            return None
            
        x = date
        if re.search(r'(T00:00)$', x):
            x = re.sub(r'(T00:00)$', ' 00:00:00', x)
        value = datetime.strptime(x, pattern).date()
        if asString: value = str(value)
        
        return value
        
    def format_familyMemberIDs(id: str, value: str, idList: list):
        """Format Family Member IDs
        Remove family IDs that aren't in the data export and reformat string
        
        @param value (str) : comma-separated string containing family IDs
        @param idist (list) : reference list of IDs to compare in the value
        
        @param comma separated string
        """
        if value is None or str(value) == 'nan' or value == '-':
            return None
            
        values = [v for v in value.split(',') if (v in idList) and not (v == id)]
        ','.join(values)
      
    def recode_biospecimenType(value):
        mappings = {
            'DNA': 'Blood DNA',
            'DNA reeds aanwezig': 'DNA Library',
            'beenmerg': 'Bone Marrow Sample',
            'bloed': 'Whole Blood',
            'fibroblastenkweek': 'Bone Marrow-Derived Fibroblasts',
            # 'foetus': None,  # not enough information
            'gekweekt foetaal weefsel': 'Human Fetal Tissue',
            'gekweekt weefsel': 'Tissue Sample',
            'gekweekte Amnion cellen': 'Amnion',
            'gekweekte Chorion villi': 'Chorionic Villus', 
            'gekweekte amnion cellen': 'Amnion',
            'huidbiopt': 'Skin/Subcutaneous Tissue',
            'navelstrengbloed': 'Umbilical Cord Blood',
            'ongekweekt foetaal weefsel': 'Human Fetal Tissue',
            'ongekweekt weefsel': 'Tissue Sample',
            'ongekweekte amnion cellen': 'Amnion',
            'ongekweekte chorion villi': 'Chorionic Villus',
            'overig': 'Tissue Sample',  # generic term
            # 'paraffine normaal': None, # these are storage conditions
            # 'paraffine tumor': None, # these are storage conditions
            'plasmacellen': 'Serum or Plasma',
            'speeksel': 'Saliva Sample',
            'suspensie': 'Mixed Adherent Cells in Suspension',
            # 'toegestuurd DNA foetaal': None  # mix of 'fetal tissue' and 'DNA'
        }
        try:
            return mappings[value]
        except KeyError:
            if bool(value):
                status_msg('Error in biospecimentType mappings: {} does not exist'.format(value))
            return None
    
    def recode_cineasToHpo(value: str, refData):
        """Recode Cineas Code to HPO
        Find the HPO term to a corresponding Cineas
        
        @param value : a string containing a cineas code
        @param refData : datatable object containing Cineas to HPO mappings
        """
        if value is None:
            return None
            
        refData[f.value == value, f.hpo][0][0]
                    
    def recode_phenotypicSex(value: str = None):
        """Recode Phenotypic Sex
        
        Standarize values to Fair Genomes/Harmonized model values
        
        @param value (str) : a value containing a phenotypic sex code (in Dutch)
        
        @return string
        """
        mappings = {'vrouw': 'female', 'man': 'male'}
        try:
            return mappings[value.lower()]
        except KeyError:
            if bool(value):
                status_msg('Error in phenotypicSex mappings: {} does not exist'.format(value))
            return None

    def recode_samplingReason(value: str):
        mappings = {
            'Diagnostisch': 'Diagnostic',
            'Dragerschap': 'Carrier Status',
            'Hematologische maligniteiten': 'Diagnostic',
            'Informativiteit': 'Informative',
            'Presymptomatisch': 'Presymptomatic Testing'
        }
        try:
            return mappings[value]
        except KeyError:
            if bool(value):
                status_msg('Error in samplingReason mapping: {} does not exist'.format(value))
            return None
    
    def recode_sequencingInfo(value: str, type: str):
        mappings = {
            'HiSeq' : {
                'platform': 'Illumina platform',
                'model': 'Illumina HiSeq Sequencer'
            },
            'MiSeq sequencer 1' : {
                'platform': 'Illumina platform',
                'model': 'MiSeq'
            },
            'MiSeq sequencer 2' : {
                'platform': 'Illumina platform',
                'model': 'MiSeq'
            },
            'NextSeq sequencer 1' : {
                'platform': 'Illumina platform',
                'model': 'Illumina NextSeq 1000'
            },
            'NextSeq sequencer 2' : {
                'platform': 'Illumina platform',
                'model': 'Illumina NextSeq 2000'
            },
            'NextSeq sequencer 3' : {
                'platform': 'Illumina platform',
                'model': None
            }
        }
        if not (type in ['platform','model']):
            raise ValueError('Error in Sequencing Info recode: type {} unknown'.format(str(type)))
        try:
            return mappings[value].get(type)
        except KeyError:
            if bool(value):
                status_msg('Error in sequencingPlatform mappings: {} does not exist'.format(value))
            return None
    def recode_subjectStatus(date):
        """Recode Subject Status
        
        Using the values in the column `dateOfDeath`, determine the current
        status of the subject. The values are either 'deceased' or 'alive'.
        
        @param date (str) : a date string
        
        @return string
        """
        if date is None or str(date) == 'nan':
            'Alive'
        else:
            'Deceased'
        
    # timestamp
    def timestamp():
        """Return Generic timestamp as yyyy-mm-ddThh:mm:ssZ"""
        return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        
    # to_dict
    def as_records(data = None):
        """Convert a datatable object to list of dictionaries (i.e., records)
        
        @param data (datatable) : datatable object to convert
        
        @return list of dictionaries
        """
        return data.to_pandas().replace({np.nan:None}).to_dict('records')

#//////////////////////////////////////////////////////////////////////////////

# Read Portal Data
status_msg('Reading data from the portal...')
cosas = molgenis(url = 'http://localhost/api/', token = '${molgenisToken}')


import pandas as pd
raw_subjects = dt.Frame(pd.read_excel('_raw/cosasportal_patients.xlsx',dtype=str))
raw_clinical = dt.Frame(pd.read_excel('_raw/cosasportal_diagnoses.xlsx',dtype=str))
raw_bench_cnv = dt.Frame(pd.read_excel('_raw/cosasportal_bench_cnv.xlsx',dtype=str))
raw_samples = dt.Frame(pd.read_excel('_raw/cosasportal_samples.xlsx',dtype=str))
raw_array_adlas = dt.Frame(pd.read_excel('_raw/cosasportal_array_adlas.xlsx',dtype=str))
raw_array_darwin = dt.Frame(pd.read_excel('_raw/cosasportal_array_darwin.xlsx',dtype=str))
raw_ngs_adlas = dt.Frame(pd.read_excel('_raw/cosasportal_ngs_adlas.xlsx',dtype=str))
raw_ngs_darwin = dt.Frame(pd.read_excel('_raw/cosasportal_ngs_darwin.xlsx',dtype=str))
cineasHpoMappings = dt.Frame(pd.read_csv('emx/lookups/cosasrefs_cineasHpoMappings.csv',dtype=str))

# pull list of subjects from COSAS and merge with new subject ID list
cosasSubjectIdList = raw_subjects[:, 'UMCG_NUMBER'].to_list()[0]
# subjectIdList = dt.Frame(
#   cosas.get('cosas_subjects',attributes='subjectID',batch_size=10000)
# )['subjectID'].to_list()[0]
# cosasSubjectIdList = list(set(cosasSubjectIdList.append(subjectIdList)))

#//////////////////////////////////////////////////////////////////////////////

# Build Phenotypic Data from workbench export
#
# This dataset provides historical records on observedPhenotypes for older cases.
# This allows us to populate the COSAS Clinical table with extra information. 

# Process data from external provider
confirmedHpoDF = raw_bench_cnv[:, {'clinicalID': f.primid, 'observedPhenotype': f.Phenotype}]
confirmedHpoDF['flag'] = dt.Frame([
    True if d in cosasSubjectIdList else False for d in confirmedHpoDF['clinicalID'].to_list()[0]
])
confirmedHpoDF = confirmedHpoDF[f.flag == True, :]
confirmedHpoDF['observedPhenotype'] = dt.Frame([
    ','.join(list(set(d.strip().split()))) for d in confirmedHpoDF['observedPhenotype'].to_list()[0]
])
confirmedHpoDF.key = 'clinicalID'
del confirmedHpoDF['flag']

#//////////////////////////////////////////////////////////////////////////////

# Build Subjects Table
#
# Map COSAS portal data into harmonized model structure for subject metadata.
# For COSAS, we will be populating the columns of interest these are listed
# below. All personal identifier columns will be validated against `subjectID`
# Therefore, any ID that does not exist in the export should not be referenced
# in this export.
#
# Row level metadata will be applied at the end of the script.
#
status_msg('Mapping COSAS Patients...')

# pull variables of interest from portal table
subjects = raw_subjects[
    :,{
        'subjectID': f.UMCG_NUMBER,
        'belongsToFamily': f.FAMILIENUMMER,
        'belongsToMother': f.UMCG_MOEDER,
        'belongsToFather': f.UMCG_VADER,
        'belongsWithFamilyMembers': f.FAMILIELEDEN,
        'subjectStatus': None,
        'dateOfBirth': f.GEBOORTEDATUM,
        'yearOfBirth': None,
        'dateOfDeath': f.OVERLIJDENSDATUM,
        'yearOfDeath': None,
        'ageAtDeath': None,
        'phenotypicSex': f.GESLACHT,
        'ageAtDeath': None,
        'primaryOrganization': 'UMCG'
    }
][:, :, dt.sort(as_type(f.subjectID, int))]

# validate `belongsToMother`
subjects['belongsToMother'] = dt.Frame([
    d if d in cosasSubjectIdList else None for d in subjects['belongsToMother'].to_list()[0]
])

# validate `belongsToFather`
subjects['belongsToMother'] = dt.Frame([
    d if d in cosasSubjectIdList else None for d in subjects['belongsToMother'].to_list()[0]
])

# format linked family IDs: remove spaces and IDs that aren't included in the export
subjects['belongsWithFamilyMembers'] = dt.Frame([
    cosasUtils.format_familyMemberIDs(
        id = d[0],
        value = d[1],
        idList = cosasSubjectIdList
    ) for d in subjects[
        :, (f.subjectID, f.belongsWithFamilyMembers)
    ].to_tuples()
])

# format dateOfBirth: as yyyy-mm-dd
subjects['dateOfBirth'] = dt.Frame([
    cosasUtils.format_date(
        date = d
    ) for d in subjects['dateOfBirth'].to_list()[0]
])

# extract yearOfBirth from dateOfBirth
subjects['yearOfBirth'] = dt.Frame([
    cosasUtils.format_asYear(d) for d in subjects['dateOfBirth'].to_list()[0]
])

# format dateOfDeath: as yyyy-mm-dd
subjects['dateOfDeath'] = dt.Frame([
    cosasUtils.format_date(d) for d in subjects['dateOfDeath'].to_list()[0]
])

# extract yearOfDeath from dateOfDeath
subjects['yearOfDeath'] = dt.Frame([
    cosasUtils.format_asYear(d) for d in subjects['dateOfDeath'].to_list()[0]
])

# format biological sex: lower values
subjects['phenotypicSex'] = dt.Frame([
    cosasUtils.recode_phenotypicSex(d) for d in subjects['phenotypicSex'].to_list()[0]
])

# recode subject status: based on `dateOfDeath`
subjects['subjectStatus'] = dt.Frame([
    cosasUtils.recode_subjectStatus(d) for d in subjects['dateOfDeath'].to_list()[0]
])

# calculate `ageAtDeath`: using `dateofBirth` and `dateOfDeath`
subjects['ageAtDeath'] = dt.Frame([
    cosasUtils.calculate_age(
        earliest = d[0],
        recent = d[1]
    ) for d in subjects[:, (f.dateOfBirth, f.dateOfDeath)].to_tuples()
])

# format variables post-mapping
subjects['dateOfBirth'] = dt.Frame([
    str(d) if bool(d) else None for d in subjects['dateOfBirth'].to_list()[0]
])

subjects['dateOfDeath'] = dt.Frame([
    str(d) if bool(d) else None for d in subjects['dateOfDeath'].to_list()[0]
])

status_msg('Mapped {} new records'.format(subjects.nrows))

#//////////////////////////////////////////////////////////////////////////////

# Build COSAS Clinical Table
#
# Map data from the portal into the preferred structure of the harmonized
# model's (HM) clinical table. The mappings will be largely based on the
# attribute `certainty`. Values will be mapped into one of the phenotype
# allowed in this table (at the moment). Use the reference table,
# columns (observed, unobserved, or provisional).
# 
# Only HPO codes are `cosasrefs_cineaseHpoMappings` to map CINEAS codes to HPO.
# This is was done to clean historical data to new clinical data management
# practices (i.e., HPO integration) whereas data from other -- newer systems --
# has HPO codes built in.
#
# Since we do not have a unique clinical diagnostic identifier, subjectID will
# be used instead.
#

status_msg('Processing new clinical data...')

# restructure dataset: rowbind all diagnoses and certainty ratings
clinical = dt.rbind(
    raw_clinical[:,{
        'clinicalID': f.UMCG_NUMBER,
        'belongsToSubject': f.UMCG_NUMBER,
        'code': f.HOOFDDIAGNOSE,
        'certainty': f.HOOFDDIAGNOSE_ZEKERHEID
    }],
    raw_clinical[:, {
        'clinicalID': f.UMCG_NUMBER,
        'belongsToSubject': f.UMCG_NUMBER,
        'code': f.EXTRA_DIAGNOSE,
        'certainty': f.EXTRA_DIAGNOSE_ZEKERHEID
    }]
)[f.code != '-', :]

# extract CINEAS code for string
clinical['code'] = dt.Frame([
    d.split(':')[0] if d else None for d in clinical['code'].to_list()[0]
])

# map cineas codes to HPO
clinical['hpo'] = dt.Frame([
    cineasHpoMappings[
        f.value == d, f.hpo
    ].to_list()[0][0] for d in clinical['code'].to_list()[0]
])

# format certainty
clinical['certainty'] = dt.Frame([
    d.lower().replace(' ', '-') if (d != '-') and (d) else None for d in clinical['certainty'].to_list()[0]
])

# create `provisionalPhenotype`: uncertain, missing, or certain
clinical['provisionalPhenotype'] = dt.Frame([
    d[0] if d[1] in [
        'zeker',
        'niet-zeker',
        'onzeker',
        None
    ] and (d[0]) else None for d in clinical[
        :, (f.hpo, f.certainty)
    ].to_tuples()
])

# create `excludedPhenotype`: zeker-niet
clinical['unobservedPhenotype'] = dt.Frame([
    d[0] if d[1] in ['zeker-niet'] else None for d in clinical[
        :, (f.hpo, f.certainty)
    ].to_tuples()
])

    
# collapse all provisionalPhenotype codes by ID
clinical['provisionalPhenotype'] = dt.Frame([
    cosasUtils.extract_phenotypicCodes(
        id = d,
        column = f.provisionalPhenotype
    ) for d in clinical['belongsToSubject'].to_list()[0]
])

# collapse all excludedPhenotype codes by ID
clinical['unobservedPhenotype'] = dt.Frame([
    cosasUtils.extract_phenotypicCodes(
        id = d,
        column = f.unobservedPhenotype
    ) for d in clinical['belongsToSubject'].to_list()[0]
])

# drop cols
del clinical[:, ['certainty','code','hpo']]

# pull unique rows only since codes were duplicated
clinical = clinical[:, first(f[1:]), dt.by(f.clinicalID)]
clinical.key = 'clinicalID'
clinical = clinical[:, :, dt.join(confirmedHpoDF)][:, :, dt.sort(as_type(f.clinicalID, int))]

# add ID check
clinical['flag'] = dt.Frame([
    True if d in cosasSubjectIdList else False for d in clinical['belongsToSubject'].to_list()[0]
])

if clinical[f.flag == False,:].nrows > 0:
    raise ValueError(
        'Error in clinical mappings: Excepted 0 flagged cases, but found {}.'
        .format(clinical[f.flag == False,:].nrows)
    )
else:
    del clinical['flag']

#//////////////////////////////////////////////////////////////////////////////

# Build Sample Table
#
# Pull data from `cosasportal_samples` and map to the new samples table.
# Information about the laboratory procedures will be mapped to the 
# samplePreparation, sequencing, and laboratoryProcedures tables. The
# reason for the sampling will be populated from the laboratory data
# exports (ADLAS and Darwin). Row level metadata will be added before import
# into Molgenis.
#
# It is possible to add the test codes in this table. I've included a short
# mapping that collapses testCodes into the `alternativeIdentifers` columns,
# but I am not using it at the moment as it takes a little while. If it is
# decided at a later timepoint that it is necessary, we can add it in.
#
status_msg('Processing new sample data...')

# Pull attributes of interest
samples = raw_samples[:,
    {
        'sampleID': f.DNA_NUMMER,
        'belongsToSubject': f.UMCG_NUMMER,
        'belongsToRequest': f.ADVVRG_ID,
        'dateOfRequest': f.ADVIESVRAAG_DATUM,
        'samplingReason': None,
        'biospecimenType': f.MATERIAAL,
        # 'alternativeIdentifiers': f.TEST_CODE
    }
]

# format `dateOfRequest` as yyyy-mm-dd
samples['dateOfRequest'] = dt.Frame([
    cosasUtils.format_date(d, asString = True) for d in samples['dateOfRequest'].to_list()[0]
])

# recode biospecimentType
samples['biospecimenType'] = dt.Frame([
    cosasUtils.recode_biospecimenType(d) for d in samples['biospecimenType'].to_list()[0]
])

# Create core structure for samples tables 
# coreDataForSamplesTables = samples[:, ['sampleID', 'belongsToSubject', 'alternativeIdentifiers']]

# # Remove altID column, it isn't necessary unless you are mapping testCodes in this table
# del samples['alternativeIdentifiers']

# recode biospecimenType
# samples[:, first(f[1:]), dt.by(f.biospecimenType)]['biospecimenType']

# Get list of unique test codes by sample, subject, and request
# samples['alternativeIdentifiers'] = dt.Frame([  
#     ','.join(
#         list(
#             set(
#                 samples[
#                     (f.sampleID == d[0]) & (f.belongsToSubject == d[1]) & (f.belongsToRequest == d[2]),
#                     'alternativeIdentifiers'
#                 ].to_list()[0]
#             )
#         )
#     ) for d in samples[
#         :,(f.sampleID, f.belongsToSubject, f.belongsToRequest, f.alternativeIdentifiers)
#     ].to_tuples()
# ])

# pull unique rows only since codes were duplicated
samples = samples[
    :, first(f[:]), dt.by(f.sampleID,f.belongsToSubject,f.belongsToRequest)
][
    :, :, dt.sort(as_type(f.belongsToSubject, int))
]


# add ID check
samples['flag'] = dt.Frame([
    True if d in cosasSubjectIdList else False for d in samples['belongsToSubject'].to_list()[0]
])

if samples[f.flag == False,:].nrows > 0:
    raise ValueError(
        'Error in clinical mappings: Excepted 0 flagged cases, but found {}.'
        .format(samples[f.flag == False,:].nrows)
    )
else:
    del samples['flag']


#//////////////////////////////////////////////////////////////////////////////


# Build Sample Prepation and Sequencing Tables
#
# Using the Adlas and Darwin files, map the data into the structure of the
# `samplePreparation` and `sequencing` tables. The column `samplingReason`
# (i.e., `labIndication`) must also be merged with the `samples` table.
#
status_msg('Preparing data for the samplePrepation and sequencing tables...')


# map array adlas data: select vars, pull distinct entries, and sort 
array_adlas = raw_array_adlas[
    :, {
        'belongsToSubject': f.UMCG_NUMBER,
        'belongsToRequest': f.ADVVRG_ID,
        'sampleID': f.DNA_NUMMER,
        'belongsToSamplePreparation': f.DNA_NUMMER,
        'belongsToLabProcedure': f.TEST_CODE
    }
][
    :,
    first(f[:]),
    dt.by(
        f.belongsToSubject,
        f.belongsToRequest,
        f.sampleID,
        f.belongsToLabProcedure
    )
][
    :,
    (f.belongsToSubject, f.belongsToRequest, f.sampleID, f.belongsToLabProcedure),
    dt.sort(as_type(f.belongsToSubject, int))
]


# map array darwin data: select vars, pull distinct entries, and sort
array_darwin = raw_array_darwin[
    :, {
        'belongsToSubject': f.UmcgNr,
        'belongsToLabProcedure': f.TestId, # codes are written into ID
        'sequencingDate': f.TestDatum, # recode date
        'reasonForSampling': f.Indicatie, # format lab indication
        'sequencingMethod': None,
    }
][
    :, first(f[:]), dt.by(f.belongsToSubject, f.belongsToLabProcedure)
][
    :, (f.belongsToSubject, f.belongsToLabProcedure, f.sequencingDate, f.reasonForSampling),
    dt.sort(as_type(f.belongsToSubject, int))
]

# join tables
array_darwin.key = ['belongsToSubject','belongsToLabProcedure']
arrayData = array_adlas[:, :, dt.join(array_darwin)]

# format `sequencingDate` as yyyy-mm-dd
# arrayData['sequencingDate'] = dt.Frame([
#     cosasUtils.format_date(d, asString = True) for d in arrayData['sequencingDate'].to_list()[0]
# ])

# reshape: NGS data from ADLAS
ngs_adlas = raw_ngs_adlas[
    :, {
        'belongsToSubject': f.UMCG_NUMBER,
        'belongsToRequest': f.ADVVRG_ID,
        'sampleID': f.DNA_NUMMER,
        'belongsToSamplePreparation': f.DNA_NUMMER,
        'belongsToLabProcedure': f.TEST_CODE
    }
][
    :,
    first(f[:]),
    dt.by(
        f.belongsToSubject,
        f.belongsToRequest,
        f.sampleID,
        f.belongsToLabProcedure
    )
][
    :,
    (
        f.belongsToSubject,
        f.belongsToRequest,
        f.sampleID,
        f.belongsToLabProcedure
    ),
    dt.sort(as_type(f.belongsToSubject, int))
]

# reshape: NGS data from Darwin
ngs_darwin = raw_ngs_darwin[
    :, {
        'belongsToSubject': f.UmcgNr,
        'belongsToLabProcedure': f.TestId,
        'sequencingDate': f.TestDatum,
        'reasonForSampling': f.Indicatie,
        'sequencingPlatform': f.Sequencer,
        'sequencingInstrumentModel': f.Sequencer,
        'sequencingMethod': None,
        'belongsToBatch': f.BatchNaam,
        'genomeBuild': f.GenomeBuild
    }
][
    :, first(f[:]), dt.by(f.belongsToSubject, f.belongsToLabProcedure)
][
    :, :, dt.sort(as_type(f.belongsToSubject, int))
]


# join tables
ngs_darwin.key = ['belongsToSubject', 'belongsToLabProcedure']
ngsData = ngs_adlas[:, :, dt.join(ngs_darwin)]

# bind array and ngs datasets
sampleSequencingData = dt.rbind(arrayData, ngsData, force=True)

# format `sequencingDate` as yyyy-mm-dd
sampleSequencingData['sequencingDate'] = dt.Frame([
    cosasUtils.format_date(d, asString = True) for d in sampleSequencingData['sequencingDate'].to_list()[0]
])

# format `labIndication`: use urdm_lookups_samplingReason
sampleSequencingData['reasonForSampling'] = dt.Frame([
    cosasUtils.recode_samplingReason(d) for d in sampleSequencingData['reasonForSampling'].to_list()[0]
])

# recode `sequencingPlatform`
sampleSequencingData['sequencingPlatform'] = dt.Frame([
    cosasUtils.recode_sequencingInfo(
        value = d,
        type = 'platform'
    ) for d in sampleSequencingData['sequencingPlatform'].to_list()[0]
])

# recode `sequencingInstrumentModel`
sampleSequencingData['sequencingInstrumentModel'] = dt.Frame([
    cosasUtils.recode_sequencingInfo(
        value = d,
        type = 'model'
    ) for d in sampleSequencingData['sequencingInstrumentModel'].to_list()[0]
])

#//////////////////////////////////////////////////////////////////////////////

# Finalize Samples
# Merge data from Lab tables

vars = [f.umcgID, f.requestID, f.dnaID, f.testCode, f.testDate, f.labIndication]
keys = ['umcgID', 'requestID', 'dnaID', 'testCode']

lab_subset = dt.rbind(lab_ngs[:, (vars)], lab_array[:, (vars)])
lab_subset.key = keys

samples = samples[:, :, dt.join(lab_subset)][:, :, dt.join(subjectFamilyIDs)]


#//////////////////////////////////////////////////////////////////////////////

# IMPORT DATA

status_msg('Preparing data for import into COSAS...')

# set timestamps
subjects[:, dt.update(dateLastUpdated = cosasUtils.timestamp())]
clinical[:, dt.update(dateLastUpdated = cosasUtils.timestamp())]
samples[:, dt.update(dateLastUpdated = cosasUtils.timestamp())]
lab_array[:, dt.update(dateLastUpdated = cosasUtils.timestamp())]
lab_ngs[:, dt.update(dateLastUpdated = cosasUtils.timestamp())]

# convert to list of dictionaries (make sure all nan's are recoded!)
cosas_subjects = cosasUtils.as_records(subjects)
cosas_clinical = cosasUtils.as_records(clinical)
cosas_samples = cosasUtils.as_records(samples)
cosas_labs_array = cosasUtils.as_records(lab_array)
cosas_labs_ngs = cosasUtils.as_records(lab_ngs)

status_msg('Importing mapping COSAS data...')
cosas.update_table(entity = 'cosas_patients', data = cosas_subjects)
cosas.update_table(entity = 'cosas_clinical', data = cosas_clinical)
cosas.update_table(entity = 'cosas_samples', data = cosas_samples)
cosas.update_table(entity = 'cosas_labs_array', data = cosas_labs_array)
cosas.update_table(entity = 'cosas_labs_ngs', data = cosas_labs_ngs)

# delete tables (useful for debugging)
# [cosas.delete(x) for x in ['cosas_labs_array','cosas_labs_ngs', 'cosas_samples', 'cosas_clinical','cosas_patients']]