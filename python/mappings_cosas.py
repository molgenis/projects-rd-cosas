#'////////////////////////////////////////////////////////////////////////////
#' FILE: mappings_cosas.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-10-05
#' MODIFIED: 2021-12-06
#' PURPOSE: primary mapping script for COSAS
#' STATUS: stable
#' PACKAGES: **see below**
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

from utils_cosas import status_msg #, molgenis
from datatable import dt, f, as_type, first
from datetime import datetime
import pandas as pd
import numpy as np
import yaml
import re

starttime = datetime.now()

def __readConfig__(path):
    with open(path, 'r') as stream:
        contents = yaml.safe_load(stream)
    stream.close()
    return contents

def to_csv(data, path: str):
    return data.to_pandas().replace({np.nan:None}).to_csv(path,index=False)

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
    def format_date(date: str, pattern = '%Y-%m-%d %H:%M:%S', asString = False):
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
    def format_idString(idString: str, idToRemove: str):
        if (str(idString) in ['nan','-','']) or (idString is None):
            return None
        newString=re.sub(re.compile(f'((,)?({idToRemove})(,)?)'), '', idString).strip()
        return re.sub(r'([,]$)', '',newString)
    def recode_biospecimenType(value):
        mappings = {
            'DNA': 'Blood DNA',
            'DNA reeds aanwezig': 'DNA Library',
            'beenmerg': 'Bone Marrow Sample',
            'bloed': 'Whole Blood',
            'fibroblastenkweek': 'Bone Marrow-Derived Fibroblasts',
            'foetus': None,  # not enough information to make a specific mapping
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
            'paraffine normaal': None, # these are storage conditions
            'paraffine tumor': None, # these are storage conditions
            'plasmacellen': 'Serum or Plasma',
            'speeksel': 'Saliva Sample',
            'suspensie': 'Mixed Adherent Cells in Suspension',
            'toegestuurd DNA foetaal': None  # mix of 'fetal tissue' and 'DNA'
        }
        try:
            return mappings[value]
        except KeyError:
            if bool(value):
                status_msg('Error in biospecimenType mappings: {} does not exist'.format(value))
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
    def recode_genomeBuild(value: str):        
        if value == 'Feb. 2009 (GRCh37/hg19)':
            return 'GRCh37'
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
        except AttributeError:
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
        except AttributeError:
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
            # for NextSeq sequencers, I'm using model None. Numbers 1:3 likely
            # represents machine number not model number.
            'NextSeq sequencer 1' : {
                'platform': 'Illumina platform',
                'model': None #'Illumina NextSeq 1000'
            },
            'NextSeq sequencer 2' : {
                'platform': 'Illumina platform',
                'model': None # 'Illumina NextSeq 2000'
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
        if not bool(date):
            return 'Presumed Alive'
        return 'Dead'
    def timestamp():
        """Return Generic timestamp as yyyy-mm-ddThh:mm:ssZ"""
        return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
# load cosas mapping config
cosasConfig = __readConfig__('data/mappings_cosas_config.yaml')
    
#//////////////////////////////////////////////////////////////////////////////

# Read Portal Data
# cosas = molgenis(url = 'http://localhost/api/', token = '${molgenisToken}')

status_msg('Loading the latest data exports...')
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
cosasSubjectIdList = list(set(raw_subjects[:, 'UMCG_NUMBER'].to_list()[0]))
# subjectIdList = dt.Frame(
#   cosas.get('cosas_subjects',attributes='subjectID',batch_size=10000)
# )['subjectID'].to_list()[0]
# cosasSubjectIdList = list(set(cosasSubjectIdList.append(subjectIdList)))

#//////////////////////////////////////////////////////////////////////////////

status_msg('')
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
status_msg('==== Building COSAS Patients ====')

# pull variables of interest from portal table
subjects = raw_subjects[
    :,{
        'subjectID': f.UMCG_NUMBER,
        'belongsToFamily': f.FAMILIENUMMER,
        'belongsToMother': f.UMCG_MOEDER,
        'belongsToFather': f.UMCG_VADER,
        'belongsWithFamilyMembers': f.FAMILIELEDEN,
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


# find new subjects to register
# `belongsToMother`, `belongsToFather`, and `belongsWithFamilyMembers`
status_msg('Identifying unregistered subjects...')
maternalIDs = subjects['belongsToMother'].to_list()[0]
paternalIDs = subjects['belongsToFather'].to_list()[0]
belongsWithFamilyMembers = []
for entity in subjects[:, (
    f.belongsWithFamilyMembers,
    f.belongsToFamily,
    f.subjectID
)].to_tuples():
    if not (entity[0] is None):
        ids = [d.strip() for d in entity[0].split(',') if not (d is None) or (d != '')]
        for el in ids:
            if (
                (el != '') and 
                (el != entity[2]) and
                not (el in paternalIDs) and
                not (el in maternalIDs) and
                not (el in cosasSubjectIdList) 
            ):
                belongsWithFamilyMembers.append({
                    'subjectID': el,
                    'belongsToFamily': entity[1],
                    'comments': 'manually registered in COSAS'
                })

# convert to datatable object and select unique subjects only
belongsWithFamilyMembers = dt.Frame(belongsWithFamilyMembers)[
    :, first(f[:]), dt.by('subjectID')
][:, :, dt.sort(as_type(f.subjectID, int))]

# bind new subject objects
status_msg('Creating new subjects to register dataset...')
subjectsToRegister = dt.rbind(
    dt.Frame([
        {
            'subjectID': d[0],
            'belongsToFamily': d[1],
            'phenotypicSex': 'Vrouw',
            'comments': 'manually registered in COSAS'
        } for d in subjects[:, (f.belongsToMother, f.belongsToFamily)].to_tuples()
        if not (d[0] is None) and not (d[0] in cosasSubjectIdList)
    ]),
    dt.Frame([
        {
            'subjectID': d[0],
            'belongsToFamily': d[1],
            'comments': 'manually registered in COSAS'
        } for d in subjects[:, (f.belongsToFather, f.belongsToFamily)].to_tuples()
        if not (d[0] is None) and not (d[0] in cosasSubjectIdList)
    ]),
    belongsWithFamilyMembers,
    force = True
)

status_msg('Registering {} new subjects'.format(subjectsToRegister.nrows))

#//////////////////////////////////////

# format belongsWithFamilyMembers in base subjects object before joining new subjects
status_msg('Formating linked Family IDs...')
subjects['belongsWithFamilyMembers'] = dt.Frame([
    cosasUtils.format_idString(d[0],d[1])
    for d in subjects[:, (f.belongsWithFamilyMembers, f.subjectID)].to_tuples()
])


# bind
status_msg('Binding subjects with new subjects...')
subjects = dt.rbind(subjects, subjectsToRegister, force = True)[:, first(f[:]), dt.by(f.subjectID)][:, :, dt.sort(as_type(f.subjectID, int))]

status_msg('Transforming variables...')

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

# format dates as string now that age calcuations are complete
subjects['dateOfBirth'] = dt.Frame([
    str(d) if bool(d) else None for d in subjects['dateOfBirth'].to_list()[0]
])

subjects['dateOfDeath'] = dt.Frame([
    str(d) if bool(d) else None for d in subjects['dateOfDeath'].to_list()[0]
])

status_msg('Mapped {} new records'.format(subjects.nrows))
del maternalIDs, paternalIDs, belongsWithFamilyMembers, subjectsToRegister

#//////////////////////////////////////////////////////////////////////////////

status_msg('')
status_msg('==== Building COSAS Clinical ====')

# Build Phenotypic Data from workbench export
#
# This dataset provides historical records on observedPhenotypes for older cases.
# This allows us to populate the COSAS Clinical table with extra information. 
status_msg('Mapping historical phenotypic data...')

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

status_msg('Transforming variables...')

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
    d in cosasSubjectIdList for d in clinical['belongsToSubject'].to_list()[0]
])

if clinical[f.flag == False,:].nrows > 0:
    raise ValueError(
        'Error in clinical mappings: Excepted 0 flagged cases, but found {}.'
        .format(clinical[f.flag == False,:].nrows)
    )
else:
    del clinical['flag']
    
status_msg('Processing {} new records for the clinical table'.format(clinical.nrows))
del confirmedHpoDF

#//////////////////////////////////////////////////////////////////////////////

status_msg('')
status_msg('==== Building COSAS Samples ====')

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
        # 'dateOfRequest': f.ADVIESVRAAG_DATUM,
        'biospecimenType': f.MATERIAAL,
        # 'alternativeIdentifiers': f.TEST_CODE
    }
]

status_msg('Transforming variables...')

# collapse request by sampleID into a comma seperated string
samples['belongsToRequest'] = dt.Frame([
    ', '.join(
        list(
            set(
                samples[
                    f.sampleID == d[0], 'belongsToRequest'
                ].to_list()[0]
            )
        )
    ) for d in samples[:, (f.sampleID, f.belongsToRequest)].to_tuples()
])

# format `dateOfRequest` as yyyy-mm-dd
# samples['dateOfRequest'] = dt.Frame([
#     cosasUtils.format_date(d, asString = True) for d in samples['dateOfRequest'].to_list()[0]
# ])

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
    :, first(f[:]), dt.by(f.sampleID)
][
    :, :, dt.sort(as_type(f.belongsToSubject, int))
]

# recode biospecimenType
samples['biospecimenType'] = dt.Frame([
    cosasUtils.recode_biospecimenType(d) for d in samples['biospecimenType'].to_list()[0]
])


# add ID check
samples['flag'] = dt.Frame([
    d in cosasSubjectIdList for d in samples['belongsToSubject'].to_list()[0]
])

if samples[f.flag == False,:].nrows > 0:
    raise ValueError(
        'Error in clinical mappings: Excepted 0 flagged cases, but found {}.'
        .format(samples[f.flag == False,:].nrows)
    )
else:
    del samples['flag']

status_msg('Processing {} new records for the samples table'.format(samples.nrows))

#//////////////////////////////////////////////////////////////////////////////

status_msg('')
status_msg('==== Building COSAS SamplePreparation and Sequencing ====')

# Build Sample Prepation and Sequencing Tables
#
# Using the Adlas and Darwin files, map the data into the structure of the
# `samplePreparation` and `sequencing` tables. The column `samplingReason`
# (i.e., `labIndication`) must also be merged with the `samples` table.
#
# In this section, combine the ADLAS and Darwin exports for each test type
# indepently, and then bind them into one object.
#
status_msg('Building Array dataset...')

# map array adlas data: select vars, pull distinct entries, and sort 
status_msg('Processing ADLAS data...')
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
status_msg('Processing Darwin data...')
array_darwin = raw_array_darwin[
    :, {
        'belongsToSubject': f.UmcgNr,
        'belongsToLabProcedure': f.TestId, # codes are written into ID
        'sequencingDate': f.TestDatum, # recode date
        'reasonForSequencing': f.Indicatie, # format lab indication
        'sequencingMethod': None,
    }
][
    :, first(f[:]), dt.by(f.belongsToSubject, f.belongsToLabProcedure)
][
    :, (f.belongsToSubject, f.belongsToLabProcedure, f.sequencingDate, f.reasonForSequencing),
    dt.sort(as_type(f.belongsToSubject, int))
]

# join tables
array_darwin.key = ['belongsToSubject','belongsToLabProcedure']
arrayData = array_adlas[:, :, dt.join(array_darwin)]

#//////////////////////////////////////

# reshape: NGS data from ADLAS
status_msg('Building NGS dataset...')

status_msg('Processing ADLAS data...')
ngs_adlas = raw_ngs_adlas[
    :, {
        'belongsToSubject': f.UMCG_NUMBER,
        'belongsToRequest': f.ADVVRG_ID,
        'sampleID': f.DNA_NUMMER,
        'belongsToSamplePreparation': f.DNA_NUMMER,
        'belongsToLabProcedure': f.TEST_CODE
    }
][
    :, first(f[:]),
    dt.by(f.belongsToSubject,f.belongsToRequest, f.sampleID, f.belongsToLabProcedure)
][
    :,
    (f.belongsToSubject,f.belongsToRequest,f.sampleID,f.belongsToLabProcedure),
    dt.sort(as_type(f.belongsToSubject, int))
]

# reshape: NGS data from Darwin
status_msg('Processing Darwin data...')
ngs_darwin = raw_ngs_darwin[
    :, {
        'belongsToSubject': f.UmcgNr,
        'belongsToLabProcedure': f.TestId,
        'sequencingDate': f.TestDatum,
        'reasonForSequencing': f.Indicatie,
        'sequencingPlatform': f.Sequencer,
        'sequencingInstrumentModel': f.Sequencer,
        'sequencingMethod': None,
        'belongsToBatch': f.BatchNaam,
        'referenceGenomeUsed': f.GenomeBuild
    }
][
    :, first(f[:]), dt.by(f.belongsToSubject, f.belongsToLabProcedure)
][
    :, :, dt.sort(as_type(f.belongsToSubject, int))
]


# join tables
ngs_darwin.key = ['belongsToSubject', 'belongsToLabProcedure']
ngsData = ngs_adlas[:, :, dt.join(ngs_darwin)]

#//////////////////////////////////////

status_msg('Combining array and ngs dataset...')

# bind array and ngs datasets; create additional attributes
sampleSequencingData = dt.rbind(arrayData, ngsData, force=True)
sampleSequencingData[
    :, dt.update(
        belongsToSample = f.sampleID,
        belongsToSamplePreparation = f.sampleID
    )
]

# removing entries that aren't registered in samples table
# This can happen for a number of reasons!
status_msg('Identifying unregistered samples...')
registeredSamples = samples['sampleID'].to_list()[0]

sampleSequencingData['flag'] = dt.Frame([
    d in registeredSamples for d in sampleSequencingData['belongsToSample'].to_list()[0]
])

unregisteredSamples = sampleSequencingData[f.flag == False, :]
unregisteredSamples.to_csv('data/cosas/unregistered_samples.csv')
status_msg('Found {} unregistered samples'.format(unregisteredSamples.nrows))

sampleSequencingData = sampleSequencingData[f.flag == True, :]

status_msg('Transforming variables...')

# create sequencingID a combination of sampleID + belongsToLabProcedure
sampleSequencingData['belongsToSamplePreparation'] = dt.Frame([
    f'{d[0]}_{d[1]}_{d[2]}' for d in sampleSequencingData[
        :, (f.belongsToSample,f.belongsToRequest, f.belongsToLabProcedure)
    ].to_tuples()
])

sampleSequencingData['sequencingID'] = dt.Frame([
    f'{d[0]}_{d[1]}_{d[2]}' for d in sampleSequencingData[
        :, (f.belongsToSample,f.belongsToRequest, f.belongsToLabProcedure)
    ].to_tuples()
])


# format `sequencingDate` as yyyy-mm-dd
sampleSequencingData['sequencingDate'] = dt.Frame([
    cosasUtils.format_date(d, asString = True) for d in sampleSequencingData['sequencingDate'].to_list()[0]
])

# format `labIndication`: use urdm_lookups_samplingReason
sampleSequencingData['reasonForSequencing'] = dt.Frame([
    cosasUtils.recode_samplingReason(d) for d in sampleSequencingData['reasonForSequencing'].to_list()[0]
])

# recode `sequencingPlatform`
sampleSequencingData['sequencingPlatform'] = dt.Frame([
    cosasUtils.recode_sequencingInfo(
        value = d, type = 'platform'
    ) for d in sampleSequencingData['sequencingPlatform'].to_list()[0]
])

# recode `sequencingInstrumentModel`
sampleSequencingData['sequencingInstrumentModel'] = dt.Frame([
    cosasUtils.recode_sequencingInfo(
        value = d,
        type = 'model'
    ) for d in sampleSequencingData['sequencingInstrumentModel'].to_list()[0]
])

# recode `genomeBuild`
sampleSequencingData['referenceGenomeUsed'] = dt.Frame([
    cosasUtils.recode_genomeBuild(d) for d in sampleSequencingData['referenceGenomeUsed'].to_list()[0]
])

#//////////////////////////////////////

# Create SamplePreparation and Sequencing tables
#
# Using the main dataset `sampleSequencingData` that we have created above,
# create the `samplePrepation` and `sequencingData` tables.
#
# We will have to add, at some point, the mappings for `libraryPreparationKit`
# and `targetEnrichmentKit`. This information should be stored in the
# `samplePreparation` table. See commented lines below.
#
# In addition, we will also need to add `sequencingMethod`. I'm not sure what
# mappings should be used. This will require further discussion.
#
status_msg('Pull attributes for the samplePreparation table...')
samplePreparation = sampleSequencingData[
    :, (
        f.sequencingID,
        f.belongsToLabProcedure,
        f.belongsToSample,
        f.belongsToRequest,
        # f.libraryPreparationKit,
        # f.targetEnrichmentKit,
        f.belongsToBatch
    )
]

samplePreparation.names={'sequencingID': 'sampleID'}
samplePreparation = samplePreparation[:, first(f[:]), dt.by(f.sampleID)]
status_msg('Processed {} new records for the samplePreparation table'.format(samplePreparation.nrows))

 
status_msg('Pulling attributes for the sequencing table...')
sequencing = sampleSequencingData[
    :, (
        f.sequencingID,
        f.belongsToLabProcedure,
        f.belongsToSamplePreparation,
        f.reasonForSequencing,
        f.sequencingDate,
        # f.sequencingFacilityOrganization,
        f.sequencingPlatform,
        f.sequencingInstrumentModel,
        # f.sequencingMethod,
        f.referenceGenomeUsed
    )
]

status_msg('Processed {} new records for the sequencing table'.format(sequencing.nrows))

#//////////////////////////////////////////////////////////////////////////////

# Prep data for import
#
# All primary data tables will be written to csv, and then import via a
# secondary script. Before writing to files, we will need to set a few
# of the row-level metadata attributes.
# 
status_msg('')
status_msg('Updating row-level metadata...')

createdBy = [x['data']['createdBy'] for x in cosasConfig['options'] if x['name'] == 'recordMetadata'][0]

# set record-level metadata
subjects[:, dt.update(
    dateRecordCreated=cosasUtils.timestamp(),
    recordCreatedBy=createdBy
)]

clinical[:, dt.update(
    dateRecordCreated=cosasUtils.timestamp(),
    recordCreatedBy=createdBy
)]

samples[:, dt.update(
    dateRecordCreated=cosasUtils.timestamp(),
    recordCreatedBy=createdBy
)]

samplePreparation[:, dt.update(
    dateRecordCreated = cosasUtils.timestamp(),
    recordCreatedBy=createdBy
)]

sequencing[:, dt.update(
    dateRecordCreated=cosasUtils.timestamp(),
    recordCreatedBy=createdBy
)]

# convert to list of dictionaries (make sure all nan's are recoded!), and save
status_msg('Writing data to file...')
to_csv(subjects,'data/cosas/subjects.csv')
to_csv(clinical,'data/cosas/clinical.csv')
to_csv(samples,'data/cosas/samples.csv')
to_csv(samplePreparation,'data/cosas/samplePreparation.csv')
to_csv(sequencing,'data/cosas/sequencing.csv')

endtime = datetime.now()
totaltime = endtime - starttime
status_msg('Completed job in {} seconds'.format(totaltime.total_seconds()))
