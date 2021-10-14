#'////////////////////////////////////////////////////////////////////////////
#' FILE: mappings_cosas.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-10-05
#' MODIFIED: 2021-10-14
#' PURPOSE: primary mapping script for COSAS
#' STATUS: working
#' PACKAGES: **see below**
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

# imports
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
      # calculate age (in years) based on two dates
    def calculate_age(earliest = None, recent = None):
        """Calculate Years of Age between two dates
        
        @param earliest : the earliest date (datetime: yyyy-mm-dd)
        @param recent : the most recent date (datetime: yyyy-mm-dd)
        
        @return int; years of age
        """
        if earliest is None or recent is None:
            return None

        return round(int((recent - earliest).days) / 365.25, 4)
    
    # parse string
    def extract_phenotypic_codes(id, column):
        """Extract Phenotypic Codes
        
        In the COSAS Clinical table, we need to extract the phenotypic codes from
        a list of unique phenotypic codes by column name.
        
        @param     id : identifier to search for
        @param column : name of the column to search for (datatable f-expression)
        
        @example
        extract_phenotypic_codes('00000', f.mycolumn)
        """
        values = list(filter(None, clinical[f.umcgID == id, column].to_list()[0]))
        unique = list(set(values))
        return ','.join(unique)

    # Create function for formating datetime value to yyyy-mm-dd
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

    # set inclusion status based on date deceased
    def recode_inclusion_status(date):
        """Recode Inclusion Status
        
        Using the values in the column `dateOfDeath`, determine the inclusion
        status. The values are either 'deceased' or 'alive'.
        
        @param data : a date string
        
        @return string
        """
        if date is None or str(date) == 'nan':
            return 'alive'
        else:
            return 'deceased'
        
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

# cosas = molgenis('')
# cosas.login('', '')


raw_patients = dt.Frame(cosas.get('cosasportal_patients', batch_size = 10000))
raw_clinical = dt.Frame(cosas.get('cosasportal_diagnoses', batch_size = 10000))
raw_samples = dt.Frame(cosas.get('cosasportal_samples', batch_size = 10000))
raw_array_adlas = dt.Frame(cosas.get('cosasportal_labs_array_adlas', batch_size = 10000))
raw_array_darwin = dt.Frame(cosas.get('cosasportal_labs_array_darwin', batch_size = 10000))
raw_ngs_adlas = dt.Frame(cosas.get('cosasportal_labs_ngs_adlas', batch_size = 10000))
raw_ngs_darwin = dt.Frame(cosas.get('cosasportal_labs_ngs_darwin', batch_size = 10000))

#//////////////////////////////////////////////////////////////////////////////

# CREATE COSAS PATIENTS
# Map the data from cosasportal_patients into COSAS terminology and structure
# of the table: `cosas_patients`. Select variables of interest and apply
# additional transformations (where applicable).

status_msg('Mapping COSAS Patients...')

# pull variables of interest from the portal
patients = raw_patients[
    :,{
        'umcgID': f.UMCG_NUMBER,
        'familyID': f.FAMILIENUMMER,
        'dateOfBirth': f.GEBOORTEDATUM,
        'biologicalSex': f.GESLACHT,
        'maternalID': f.UMCG_MOEDER,
        'paternalID': f.UMCG_VADER,
        'linkedFamilyIDs': f.FAMILIELEDEN,
        'dateOfDeath': f.OVERLIJDENSDATUM,
        'inclusionStatus': None,
        'ageAtDeath': None
    }
][:, :, dt.sort(as_type(f.umcgID, int))]


# format date: as yyyy-mm-dd
patients['dateOfBirth'] = dt.Frame([
    cosasUtils.format_date(
        date = d
    ) for d in patients['dateOfBirth'].to_list()[0]
])

# format linked family IDs: remove spaces
patients['linkedFamilyIDs'] = dt.Frame([
    re.sub(r'(\s+)?[,]\s+', ',', d) for d in patients['linkedFamilyIDs'].to_list()[0] 
])

# format biological sex: lower values
patients['biologicalSex'] = dt.Frame([
    d.lower() for d in patients['biologicalSex'].to_list()[0]
])

# format date of death: as yyyy-mm-dd
patients['dateOfDeath'] = dt.Frame([
    cosasUtils.format_date(d) for d in patients['dateOfDeath'].to_list()[0]
])

# recode inclusion status: based on `dateOfDeath`
patients['inclusionStatus'] = dt.Frame([
    cosasUtils.recode_inclusion_status(d) for d in patients['dateOfDeath'].to_list()[0]
])

# calculate `ageAtDeath`: using `dateofBirth` and `dateOfDeath`
patients['ageAtDeath'] = dt.Frame([
    cosasUtils.calculate_age(
        earliest = d[0],
        recent = d[1]
    ) for d in patients[:, (f.dateOfBirth, f.dateOfDeath)].to_tuples()
])

# format variables post-mapping
patients['dateOfBirth'] = dt.Frame([
    str(d) if bool(d) else None for d in patients['dateOfBirth'].to_list()[0]
])

patients['dateOfDeath'] = dt.Frame([
    str(d) if bool(d) else None for d in patients['dateOfBirth'].to_list()[0]
])


#//////////////////////////////////////

# Create Subset of Patients

patientFamilyIDs = patients[:, (f.umcgID, f.familyID)]
patientFamilyIDs.key = 'umcgID'

#//////////////////////////////////////////////////////////////////////////////

# CREATE COSAS CLINICAL

status_msg('Mapping COSAS Clinical...')

# restructure dataset: rowbind all diagnoses and certainty ratings
clinical = dt.rbind(
    raw_clinical[:,{
        'umcgID': f.UMCG_NUMBER,
        'code': f.HOOFDDIAGNOSE,
        'certainty': f.HOOFDDIAGNOSE_ZEKERHEID
    }],
    raw_clinical[:, {
        'umcgID': f.UMCG_NUMBER,
        'code': f.EXTRA_DIAGNOSE,
        'certainty': f.EXTRA_DIAGNOSE_ZEKERHEID
    }]
)[f.code != '-', :]

# format code: 'dx_<code>'
clinical['code'] = dt.Frame([
    d.split(':')[0] if d else None for d in clinical['code'].to_list()[0]
])

# format certainty
clinical['certainty'] = dt.Frame([
    d.lower().replace(' ', '-') if (d != '-') and (d) else None for d in clinical['certainty'].to_list()[0]
])


# create `provisionalPhenotype`: uncertain, missing, or certain
clinical['provisionalPhenotypeCodes'] = dt.Frame([
    d[0] if d[1] in ['zeker', 'niet-zeker', 'onzeker', None] and (d[0]) else None for d in clinical[
        :, (f.code, f.certainty)
    ].to_tuples()
])

# create `excludedPhenotype`: zeker-niet
clinical['excludedPhenotypeCodes'] = dt.Frame([
    d[0] if d[1] in ['zeker-niet'] else None for d in clinical[
        :, (f.code, f.certainty)
    ].to_tuples()
])

    
# collapse all provisionalPhenotype codes by ID
clinical['provisionalPhenotype'] = dt.Frame([
    cosasUtils.extract_phenotypic_codes(
        id = d,
        column = f.provisionalPhenotypeCodes
    ) for d in clinical['umcgID'].to_list()[0]
])

# collapse all excludedPhenotype codes by ID
clinical['excludedPhenotype'] = dt.Frame([
    cosasUtils.extract_phenotypic_codes(
        id = d,
        column = f.excludedPhenotypeCodes
    ) for d in clinical['umcgID'].to_list()[0]
])

# drop cols
del clinical[:, ['certainty', 'code', 'provisionalPhenotypeCodes', 'excludedPhenotypeCodes']]

# pull unique rows only since codes were duplicated
clinical = clinical[
    :, first(f[1:]), dt.by(f.umcgID)
][
    :, :, dt.sort(as_type(f.umcgID, int))
]


#//////////////////////////////////////////////////////////////////////////////

# Create COSAS SAMPLES

status_msg('Mapping COSAS Samples...')

samples = raw_samples[:,
    {
        'umcgID': f.UMCG_NUMMER,
        'requestID': f.ADVVRG_ID,
        'requestDate': f.ADVIESVRAAG_DATUM,
        'sampleID': f.MONSTER_ID,
        'testCode': f.TEST_CODE,
        'dnaID': f.DNA_NUMMER,
        'materialType': f.MATERIAAL,
        'result': f.EINDUITSLAGTEKST,
        'resultDate': f.EINDUITSLAG_DATUM,
        'requestResultID': f.ADVIESVRAAGUITSLAG_ID,
        'disorderCode': f.AANDOENING_CODE,
        'labResult': f.LABUITSLAGTEKST,
        'labResultComment': f.LABUITSLAG_COMMENTAAR,
        'labResultDate': f.LABUITSLAG_DATUM,
        'labResultID': f.LABUITSLAG_ID,
        'labResultAvailability': f.LABRESULTS,
        'authorizationStatus': f.AUTHORISED
    }
]

# recode dates
samples['requestDate'] = dt.Frame([
    cosasUtils.format_date(d, asString = True) for d in samples['requestDate'].to_list()[0]
])
samples['resultDate'] = dt.Frame([
    cosasUtils.format_date(d, asString = True) for d in samples['resultDate'].to_list()[0]
])
samples['labResultDate'] = dt.Frame([
    cosasUtils.format_date(d, asString = True) for d in samples['labResultDate'].to_list()[0]
])

# format testCode: to lower
samples['testCode'] = dt.Frame([
    d.lower() for d in samples['testCode'].to_list()[0]
])

#//////////////////////////////////////////////////////////////////////////////

# CREATE LABS ARRAY
# map and merge both array datasets

status_msg('Mapping COSAS Labs Array...')

# map array adlas data
array_adlas = raw_array_adlas[
    # select variables of interest
    :, {
        'umcgID': f.UMCG_NUMBER,
        'requestID': f.ADVVRG_ID,
        'dnaID': f.DNA_NUMMER,
        'testCode': f.TEST_CODE
    }
][
    # find distinct cases
    :, first(f[1:]), dt.by('umcgID', 'requestID', 'dnaID', 'testCode')
][
    # drop vars and sort
    :, (f.umcgID, f.requestID, f.dnaID, f.testCode),
    dt.sort(as_type(f.umcgID, int))
]


# map array darwin data
array_darwin = raw_array_darwin[
    # map variables of intest
    :, {
        'umcgID': f.UmcgNr,
        'testCode': f.TestId, # codes are written into ID
        'testDate': f.TestDatum, # recode date
        'labIndication': f.Indicatie # format lab indication
    }
][
    # get unique rows
    :, first(f[1:]), dt.by('umcgID', 'testCode')
][
    # drop vars and sort
    :, (f.umcgID, f.testCode, f.testDate, f.labIndication),
    dt.sort(as_type(f.umcgID, int))
]

# join tables
array_darwin.key = ['umcgID','testCode']
lab_array = array_adlas[:, :, dt.join(array_darwin)]

# format `testDate` as yyyy-mm-dd
lab_array['testDate'] = dt.Frame([
    cosasUtils.format_date(d, asString = True) for d in lab_array['testDate'].to_list()[0]
])

# format `labindication` as lowercase
lab_array['labIndication'] = dt.Frame([
    d.lower() for d in lab_array['labIndication'].to_list()[0]
])

# format `testCode`: to lowercase
lab_array['testCode'] = dt.Frame([
    d.lower() for d in lab_array['testCode'].to_list()[0]
])

#//////////////////////////////////////////////////////////////////////////////

# Create NGS Lab Tables

status_msg('Mapping COSAS Labs NGS...')

ngs_adlas = raw_ngs_adlas[
    # select variables of interest
    :, {
        'umcgID': f.UMCG_NUMBER,
        'requestID': f.ADVVRG_ID,
        'dnaID': f.DNA_NUMMER,
        'testCode': f.TEST_CODE
    }
][
    # find distinct cases
    :, first(f[1:]), dt.by('umcgID', 'requestID', 'dnaID', 'testCode')
][
    # drop vars and sort
    :, (f.umcgID, f.requestID, f.dnaID, f.testCode),
    dt.sort(as_type(f.umcgID, int))
]


ngs_darwin = raw_ngs_darwin[
    # select variables of intest
    :, {
        'umcgID': f.UmcgNr,
        'testCode': f.TestId,  # reformat
        'testDate': f.TestDatum, # recode
        'labIndication': f.Indicatie, # recode
        'sequencer': f.Sequencer,
        'prepKit': f.PrepKit,
        'sequencingType': f.SequencingType,
        'seqType': f.SeqType,
        'capturingKit': f.CapturingKit,
        'batchName': f.BatchNaam,
        'genomeBuild': f.GenomeBuild
    }
][
    # find distinct cases
    :, first(f[1:]), dt.by('umcgID', 'testCode')
][
    # sort
    :, :, dt.sort(as_type(f.umcgID, int))
]

del ngs_darwin[:, ['testCode.0']]


# join tables
ngs_darwin.key = ['umcgID', 'testCode']
lab_ngs = ngs_adlas[:, :, dt.join(ngs_darwin)]

# format `testCode`: to lowercase
lab_ngs['testCode'] = dt.Frame([
    d.lower() for d in lab_ngs['testCode'].to_list()[0]
])

# format `testDate` as yyyy-mm-dd
lab_ngs['testDate'] = dt.Frame([
    cosasUtils.format_date(d, asString = True) for d in lab_ngs['testDate'].to_list()[0]
])

# format `labIndication`: to lowercase
lab_ngs['labIndication'] = dt.Frame([
    d.lower() for d in lab_ngs['labIndication'].to_list()[0]
])

#//////////////////////////////////////////////////////////////////////////////

# Finalize Samples
# Merge data from Lab tables

vars = [f.umcgID, f.requestID, f.dnaID, f.testCode, f.testDate, f.labIndication]
keys = ['umcgID', 'requestID', 'dnaID', 'testCode']

lab_subset = dt.rbind(lab_ngs[:, (vars)], lab_array[:, (vars)])
lab_subset.key = keys

samples = samples[:, :, dt.join(lab_subset)][:, :, dt.join(patientFamilyIDs)]


#//////////////////////////////////////////////////////////////////////////////

# IMPORT DATA

status_msg('Preparing data for import into COSAS...')

# set timestamps
patients[:, dt.update(dateLastUpdated = cosasUtils.timestamp())]
clinical[:, dt.update(dateLastUpdated = cosasUtils.timestamp())]
samples[:, dt.update(dateLastUpdated = cosasUtils.timestamp())]
lab_array[:, dt.update(dateLastUpdated = cosasUtils.timestamp())]
lab_ngs[:, dt.update(dateLastUpdated = cosasUtils.timestamp())]

# convert to list of dictionaries (make sure all nan's are recoded!)
cosas_patients = cosasUtils.as_records(patients)
cosas_clinical = cosasUtils.as_records(clinical)
cosas_samples = cosasUtils.as_records(samples)
cosas_labs_array = cosasUtils.as_records(lab_array)
cosas_labs_ngs = cosasUtils.as_records(lab_ngs)

status_msg('Importing mapping COSAS data...')
cosas.update_table(entity = 'cosas_patients', data = cosas_patients)
cosas.update_table(entity = 'cosas_clinical', data = cosas_clinical)
cosas.update_table(entity = 'cosas_samples', data = cosas_samples)
cosas.update_table(entity = 'cosas_labs_array', data = cosas_labs_array)
cosas.update_table(entity = 'cosas_labs_ngs', data = cosas_labs_ngs)

# delete tables (useful for debugging)
# [cosas.delete(x) for x in ['cosas_labs_array','cosas_labs_ngs', 'cosas_samples', 'cosas_clinical','cosas_patients']]