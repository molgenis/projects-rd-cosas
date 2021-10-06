#'////////////////////////////////////////////////////////////////////////////
#' FILE: mappings_cosas.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-10-05
#' MODIFIED: 2021-10-06
#' PURPOSE: primary mapping script for COSAS
#' STATUS: in.progress
#' PACKAGES: datatable
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

# import pandas as pd
# def read_xlsx(path, nrows = None, usecols = None, converters = None):
#     data = pd.read_excel(
#         path,
#         engine = 'openpyxl',
#         nrows = nrows,
#         usecols = usecols,
#         converters = converters,
#         dtype = str
#     )
#     return data.to_dict('records')
# raw_patients = dt.Frame(read_xlsx('_raw/cosasportal_patients.xlsx'))
# raw_clinical = dt.Frame(read_xlsx('_raw/cosasportal_diagnoses.xlsx'))
# raw_samples = dt.Frame(read_xlsx('_raw/cosasportal_samples.xlsx'))
# raw_array_adlas = dt.Frame(read_xlsx('_raw/cosasportal_array_adlas.xlsx'))
# raw_array_darwin = dt.Frame(read_xlsx('_raw/cosasportal_array_darwin.xlsx'))
# raw_ngs_adlas = dt.Frame(read_xlsx('_raw/cosasportal_ngs_adlas.xlsx'))
# raw_ngs_darwin = dt.Frame(read_xlsx('_raw/cosasportal_ngs_darwin.xlsx'))


import re
from datetime import datetime
from datatable import dt, f, as_type, first
import molgenis.client as molgenis
import json
import requests
from urllib.parse import quote_plus


class molgenis(molgenis.Session):
    """molgenis
    
    An extension of the molgenis.client class
    
    """
    
    # update_table
    def update_table(self, data, entity):
        """Update Table
        
        When importing data into a new table using the client, there is a 1000
        row limit. This method allows you push data without having to worry
        about the limits.
        
        @param self required class param
        @param data object containing data to import
        @param entity ID of the target entity written as 'package_entity'
        
        @return a response code
        """
        if len(data) < 1000:
            response = self._session.post(
                url = self._url + 'v2/' + quote_plus(entity),
                headers = self._get_token_header_with_content_type(),
                data = json.dumps({'entities' : data})
            )
            if response.status_code == 201:
                status_msg(
                    'Successfully imported data (response: {})'
                    .format(response.status_code)
                )
            else:
                status_msg(
                    'Failed to import data (response: {}): \nReason:{}'
                    .format(response.status_code, response.content)
                )
        else:    
            for d in range(0, len(data), 1000):
                response = self._session.post(
                    url=self._url + 'v2/' + entity,
                    headers=self._get_token_header_with_content_type(),
                    data=json.dumps({'entities': data[d:d+1000]})
                )
                if response.status_code == 201:
                    status_msg(
                        'Successfuly imported batch {} (response: {})'
                        .format(d, response.status_code)
                    )
                else:
                    status_msg(
                        'Failed to import data (response: {}): \nReason:{}'
                        .format(response.status_code, response.content)
                    )

    # batch_update_one_attr
    def batch_update_one_attr(self, entity, attr, values):
        """Batch Update One Attribute
        
        Import data for an attribute in groups of 1000
        
        @param self required class param
        @param entity ID of the target entity written as `package_entity`
        @param values data to import, a list of dictionaries where each dictionary
              is structured with two keys: the ID attribute and the attribute
              that you wish to update. E.g. [{'id': 'id123", 'x': 1},...]
        
        @return a response code
        """
        add = 'No new data'
        for i in range(0, len(values), 1000):
            add = 'Update did tot go OK'
            """Updates one attribute of a given entity with the given values of the given ids"""
            response = self._session.put(
                self._url + "v2/" + quote_plus(entity) + "/" + attr,
                headers=self._get_token_header_with_content_type(),
                data=json.dumps({'entities': values[i:i+1000]})
            )
            if response.status_code == 200:
                add = 'Update went OK'
            else:
                try:
                    response.raise_for_status()
                except requests.RequestException as ex:
                    self._raise_exception(ex)
                return response
        return add


def timestamp():
    """Timestamp
    
    Print a timestamp as yyyy-mm-dd HH:MM:SS:ms
    
    """
    return datetime.utcnow().strftime('%H:%M:%S.%f')[:-3]



def status_msg(*args):
    """Status Message
    
    Prints a message with a timestamp
    
    @param *args : message to write 
    
    """
    msg = ' '.join(map(str, args))
    print('\033[94m[' + timestamp() + '] \033[0m' + msg)

    

# Create function for extracting unique phenotypic codes
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
        
    value = datetime.strptime(date, pattern).date()
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


# calculate age (in years) based on two dates
def calculate_age(earliest = None, recent = None):
    """Calculate Years of Age between two dates
    
    @param earliest : the earliest date (datetime: yyyy-mm-dd)
    @param recent : the most recent date (datetime: yyyy-mm-dd)
    
    @return int; years of age
    """
    if earliest is None or recent is None:
        return None

    return int((recent - earliest).days) / 365.25


#//////////////////////////////////////////////////////////////////////////////
    
    
# Read Portal Data
status_msg('Reading data from the portal...')
cosas = molgenis(url = 'http://localhost/api/')
cosas.login()


raw_patients = cosas.get('cosasportal_patients', batch = 10000)
raw_clinical = cosas.get('cosasportal_clinical', batch = 10000)
raw_samples = cosas.get('cosasportal_samples', batch = 10000)
raw_array_adlas = cosas.get('cosasportal_array_adlas', batch = 10000)
raw_array_darwin = cosas.get('cosasportal_array_darwin', batch = 10000)
raw_ngs_adlas = cosas.get('cosasportal_ngs_adlas', batch = 10000)
raw_ngs_darwin = cosas.get('cosasportal_ngs_darwin', batch = 10000)

#//////////////////////////////////////////////////////////////////////////////

# CREATE COSAS PATIENTS
# Map the data from cosasportal_patients into COSAS terminology and structure
# of the table: `cosas_patients`. Select variables of interest and apply
# additional transformations (where applicable).

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
    format_date(d) for d in patients['dateOfBirth'].to_list()[0]
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
    format_date(d) for d in patients['dateOfDeath'].to_list()[0]
])

# recode inclusion status: based on `dateOfDeath`
patients['inclusionStatus'] = dt.Frame([
    recode_inclusion_status(d) for d in patients['dateOfDeath'].to_list()[0]
])

# calculate `ageAtDeath`: using `dateofBirth` and `dateOfDeath`
patients['ageAtDeath'] = dt.Frame([
    calculate_age(d[0], d[1]) for d in patients[:, (f.dateOfBirth, f.dateOfDeath)].to_tuples()
])

#//////////////////////////////////////////////////////////////////////////////

# CREATE COSAS CLINICAL

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
    d.split(':')[0] for d in clinical['code'].to_list()[0]
])

# format certainty
clinical['certainty'] = dt.Frame([
    d.lower().replace(' ', '-') if d != '-' else None for d in clinical['certainty'].to_list()[0]
])


# create `provisionalPhenotype`: uncertain, missing, or certain
clinical['provisionalPhenotypeCodes'] = dt.Frame([
    d[0] if d[1] in ['zeker', 'niet-zeker', 'onzeker', None] else None for d in clinical[
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
    extract_phenotypic_codes(
        id = d,
        column = f.provisionalPhenotypeCodes
    ) for d in clinical['umcgID'].to_list()[0]
])

# collapse all excludedPhenotype codes by ID
clinical['excludedPhenotype'] = dt.Frame([
    extract_phenotypic_codes(
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
    format_date(d) for d in samples['requestDate'].to_list()[0]
])
samples['resultDate'] = dt.Frame([
    format_date(d) for d in samples['resultDate'].to_list()[0]
])
samples['labResultDate'] = dt.Frame([
    format_date(d) for d in samples['labResultDate'].to_list()[0]
])

# format testCode: to lower
samples['testCode'] = dt.Frame([
    d.lower() for d in samples['testCode'].to_list()[0]
])

#//////////////////////////////////////////////////////////////////////////////

# CREATE LABS ARRAY
# map and merge both array datasets

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

# format `testDate` as yyyy-mm-dd
array_darwin['testDate'] = dt.Frame([
    format_date(d) for d in array_darwin['testDate'].to_list()[0]
])

# format `labindication` as lowercase
array_darwin['labIndication'] = dt.Frame([
    d.lower() for d in array_darwin['labIndication'].to_list()[0]
])

# join tables
array_darwin.key = ['umcgID','testCode']
lab_array = array_adlas[:, :, dt.join(array_darwin)]

#//////////////////////////////////////////////////////////////////////////////

# Create NGS Lab Tables

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

ngs_adlas['testCode'] = dt.Frame([
    d.lower() for d in ngs_adlas['testCode'].to_list()[0]
])

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

# format `testCode`: to lowercase
ngs_darwin['testCode'] = dt.Frame([
    d.lower() for d in ngs_darwin['testCode'].to_list()[0]
])

# format `testDate` as yyyy-mm-dd
ngs_darwin['testDate'] = dt.Frame([
    format_date(d) for d in ngs_darwin['testDate'].to_list()[0]
])

# format `labIndication`: to lowercase
ngs_darwin['labIndication'] = dt.Frame([
    d.lower() for d in ngs_darwin['labIndication'].to_list()[0]
])

ngs_darwin.key = ['umcgID', 'testCode']
lab_ngs = ngs_adlas[:, :, dt.join(ngs_darwin)]