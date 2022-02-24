#'////////////////////////////////////////////////////////////////////////////
#' FILE: mappings_cosas.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-10-05
#' MODIFIED: 2022-02-24
#' PURPOSE: primary mapping script for COSAS
#' STATUS: stable
#' PACKAGES: **see below**
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////


from datatable import dt, f, as_type, first
import molgenis.client as molgenis
from datetime import datetime
import numpy as np
import requests
import json
import re

# only for local dev
from dotenv import load_dotenv
from os import environ
load_dotenv()
host = environ['MOLGENIS_HOST_ACC']
token = environ['MOLGENIS_TOKEN_ACC'] 

# uncomment when deployed
# host = 'http://localhost/api/'
# token = '${molgenisToken}'

starttime = datetime.now()
createdBy = 'cosasbot'

# generic status message with timestamp
def status_msg(*args):
    """Status Message
    Print a log-style message, e.g., "[16:50:12.245] Hello world!"

    @param *args one or more strings containing a message to print
    @return string
    """
    print('[{}] {}'.format(
        datetime.utcnow().strftime('%H:%M:%S.%f')[:-3], ' '.join(map(str, args))
    ))


class Molgenis(molgenis.Session):
    def __init__(self, *args, **kwargs):
        super(Molgenis, self).__init__(*args, **kwargs)
        self.__getApiUrl__()
    
    def __getApiUrl__(self):
        """Find API endpoint regardless of version"""
        props = list(self.__dict__.keys())
        if '_url' in props:
            self._apiUrl = self._url
        if '_api_url' in props:
            self._apiUrl = self._api_url
    
    def _checkResponseStatus(self, response, label):
        if (response.status_code // 100) != 2:
            err = response.json().get('errors')[0].get('message')
            status_msg(f'Failed to import data into {label} ({response.status_code}): {err}')
        else:
            status_msg(f'Imported data into {label}')
    
    def _POST(self, url: str = None, data: list = None, label: str=None):
        try:
            response = self._session.post(
                url = url,
                headers = self._get_token_header_with_content_type(),
                data = json.dumps({'entities': data})
            )
            
            self._checkResponseStatus(response, label)
            response.raise_for_status()
            
        except requests.exceptions.HTTPError as e:
            raise SystemError(e)
            
    def _PUT(self, url: str=None, data: list=None, label: str=None):
        try:
            response = self._session.put(
                url = url,
                headers = self._get_token_header_with_content_type(),
                data = json.dumps({'entities': data})
            )
            
            self._checkResponseStatus(response, label)
            response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            raise SystemError(e)
            
    
    def importData(self, entity: str, data: list):
        """Import Data
        Import data into a table. The data must be a list of dictionaries that
        contains the 'idAttribute' and one or more attributes that you wish
        to import.
        
        @param entity (str) : name of the entity to import data into
        @param data (list) : data to import (a list of dictionaries)
        
        @return a status message
        """
        url = '{}v2/{}'.format(self._apiUrl, entity)
        # single push
        if len(data) < 1000:
            self._POST(url=url, entity=entity, data=data, label=str(entity))
            
        # batch push
        if len(data) >= 1000:    
            for d in range(0, len(data), 1000):
                self._POST(
                    url = url,
                    data = data[d:d+1000],
                    label = '{} (batch {})'.format(str(entity), str(d))
                )
    
    
    def updateRows(self, entity: str, data: list):
        """Update Rows
        Update rows in a table. The data must be a list of dictionaries that
        contains the 'idAttribute' and must contain values for all attributes
        in addition to the one that you wish to update. This is ideal for
        updating rows. To update an attribute, use `updateColumn`.
        
        @param entity (str) : name of the entity to import data into
        @param data (list) : data to import (list of dictionaries)
        
        @return a status message
        """
        url = '{}v2/{}'.format(self._apiUrl, entity)
        # single push
        if len(data) < 1000:
            self._PUT(url=url, data=data, label=str(entity))
            
        # batch push
        if len(data) >= 1000:    
            for d in range(0, len(data), 1000):
                self._PUT(
                    url = url,
                    data = data[d:d+1000],
                    label = '{} (batch {})'.format(str(entity), str(d))
                )

    def updateColumn(self, entity: str, attr: str, data: list):
        """Update Column
        Update values of an single column in a table. The data must be a list of
        dictionaries that contain the `idAttribute` and the value of the
        attribute that you wish to update. As opposed to the `updateRows`, you
        do not need to supply values for all columns.
        
        @param entity (str) : name of the entity to import data into
        @param attr (str) : name of the attribute to update
        @param data (list) : data to import (list of dictionaries)
        
        @retrun status message
        """
        url = '{}v2/{}/{}'.format(self._apiUrl, str(entity), str(attr))
        
        # single push
        if len(data) < 1000:
            self._PUT(url=url, data=data, label=str(entity))
        
        # batch push
        if len(data) >= 1000:
            for d in range(0, len(data), 1000):
                self._PUT(
                    url = url,
                    data = data[d:d+1000],
                    label = '{}/{} (batch {})'.format(
                        str(entity),
                        str(attr),
                        str(d)
                    )
                )

# class cosasLogger:
#     def __init__(self):
#         """Cosas Logger
#         Keep records of all processing steps and summarize the daily imports
#        
#         cosaslogs = CosasLogger()
#        
#         """
#         self.currentStep = None
#         self.log = self.startLog()
#         self.processingStepLogs = []
#        
#     def __stoptime__(self, name):
#         timeFormat = '%Y-%m-%d %H:%M:%S'
#         self[str(name)]['endTime'] = datetime.now().strftime(timeFormat)
#         self[str(name)]['elapsedTime'] = (
#             self[str(name)]['endTime'] - self[str(name)]['startTime']
#         ).total_seconds()
#         self[str(name)]['endTime'] = self[str(name)]['endTime'].strftime(timeFormat)
#         self[str(name)]['startTime'] = self[str(name)]['startTime'].strftime(timeFormat)
#        
#
#     def startProcessingStepLog(self, tablename):
#         self.currentStep = {
#             'identifier': '{}_{}'.format(
#                 datetime.now().strftime('%Y-%m-%d'),
#                 len(self.processingStepLogs) + 1
#             ),
#             'name': None,
#             'step': None,
#             'databaseTable': tablename,
#             'startTime': datetime.now(),
#             'endTime': None,
#             'elapsedTime': None,
#             'status': None,
#             'comment': None
#         }
#        
#     def stopProcessingStepLog(self):
#         self.__stoptime__(name='currentStep')
#         self.log['steps'].append(self.currentStep['identifier'])
#         self.processingStepLogs.append(self.currentStep)
#         self.currentStep = None
#        
#        
#     def startLog(self):
#         self.log = {
#             'identifier': datetime.now().strftime('%Y-%m-%d'),
#             'name': 'cosas-daily-import',
#             'databaseName': 'cosas',
#             'startTime': datetime.now(),
#             'endTime': None,
#             'elapsedTime': None,
#             'steps': [],
#             'comments': None
#         }
#        
#     def stopLog(self):
#         self.__stoptime__(name='log')
#         self.log['endTime'] = datetime.now()
#         self.log['elapsedTime'] = (self.log['endTime'] - self.log['startTime']).total_seconds()
#         self.log['steps'] = ','.join(self.log['steps'])
#
# cosaslogs = cosasLogger()
# cosaslogs.startLog()


# create class of methods used in the mappings
class cosastools:
    
    @staticmethod
    def calcAge(earliest: datetime.date=None, recent: datetime.date=None):
        """Calculate Years of Age between two dates
        
        @param earliest: the earliest date (datetime: yyyy-mm-dd)
        @param recent: the most recent date (datetime: yyyy-mm-dd)
        @return int
        """
        if (earliest is None) or (recent is None):
            return None

        return round(((recent - earliest).days) / 365.25, 4)
    
    @staticmethod
    def collapseFamilyIDs(value: str=None, valueToRemove: str=None):
        """Collapse string of Family Member Identifiers
        Format IDs as a comma separated string. Remove subject ID it exists in
        the list of IDs as it isn't necessary to reference the subject here.
        
        @param value comma separated string containing one or more IDs
        @param valueToRemove value to remove from the list of IDs
        
        @return comma separated string containing one ore more family IDs
        """
        if (str(value) in ['nan','-','']) or (value is None): return None
        pattern = re.compile(f'((,)?({valueToRemove})(,)?)')
        newString = re.sub(pattern, '', value).strip().replace(' ','')
        return re.sub(r'([,]$)', '',newString)
    
    @staticmethod
    def collapseHpoCodes(id, column):
        """Collapse HPO Codes
        In the COSAS clinical table, find all HPO codes by subject identifier,
        collapse, get distinct values, and collapse into a string.
        
        @param id : identifier to search for
        @param column : name of the column to search for (datatable f-expression)
        
        @return comma separated string containing one or more value
        """
        results = clinical[f.belongsToSubject == id, column]
        if results.nrows == 0:
            return None
        return ','.join(list(set(filter(None, results.to_list()[0]))))
        
    
    @staticmethod
    def collapseTestCodes(subjectID, sampleID, requestID, column):
        """Collapse Test Codes
        In the COSAS samples table, find all matching alternative identifiers
        by id (subject-, sample-, and request identifiers), get distinct
        values, and collapse into a string
        
        @param subjectId (str) : subject ID to locate
        @param sampleId  (str) : sample ID to locate
        @param requestId (str) : specific request associated with a sample
        @param column    (str) : name of the column where the codes are stored
        
        @return comma separated string containing one or more value
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
    
    @staticmethod
    def formatAsYear(date: datetime.date = None):
        """Format Date as Year
        @param date: a datetime object
        @return datetime object formated as year
        """
        if date is None or str(date) == 'nan':
            return None

        return date.strftime('%Y')
    
    @staticmethod
    def formatAsDate(date=None, pattern='%Y-%m-%d %H:%M:%S', asString = False):
        """Format Date String as yyyy-mm-dd
        
        @param string : date string
        @param pattern : date format, default: %Y-%m-%d %H:%M:%S
        @param asString : If True, the result will be returned as string

        @return datetime or string
        """
        if not date or str(date) == 'nan':
            return None
            
        x = date
        if re.search(r'(T00:00)$', x):
            x = re.sub(r'(T00:00)$', ' 00:00:00', x)
        value = datetime.strptime(x, pattern).date()

        if asString:
            value = str(value)

        return value
    
    @staticmethod
    def recodeValue(
        mappings: None,
        value: str=None,
        label:str=None,
        warn=True
    ):
        """Recode value
        Recode values using new mappings. It is recommended to define all
        mappings using lowercase letters and the the input for value should
        also be lowered.
        
        @param mappings a datatable object containing where each key
            corresponds to a new value
        @param value string containing a value to recode
        @param label string that indicates the mapping type for error messages
        @param warn If True (default), a message will be displayed when a value
            cannot be mapped
        
        @return string or NoneType
        """
        try:
            return mappings[value]
        except KeyError:
            if bool(value) and warn:
                status_msg('Error in {} recoding: "{}" not found'.format(label, value))
            return None
        except AttributeError and warn:
            if bool(value):
                status_msg('Error in {} recoding: "{}" not found'.format(label, value))
            return None
    
    @staticmethod
    def mapCineasToHpo(value: str, refData):
        """Recode Cineas Code to HPO
        Find the HPO term to a corresponding Cineas
        
        @param value : a string containing a cineas code
        @param refData : datatable object containing Cineas to HPO mappings
        
        @return string
        """
        if value is None:
            return None
        
        return refData[f.value == value, f.hpo][0][0]
    
    @staticmethod
    def timestamp():
        """Return Generic timestamp as yyyy-mm-ddThh:mm:ssZ"""
        return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        
    @staticmethod
    def to_keypairs(data, keyAttr='sourceValue', valueAttr='newValue'):
        """To Key pairs
        Convert a list of dictionaries into a key-value dictionary. This method
        is useful for creating objects for mapping tables.
        
        @param data list of dictionaries that you wish to convert
        @param keyAttr attribute that will be key
        @param valueAttr attribute that contains the value
        
        @return a dictionary
        """
        maps = {}
        for d in data:
            maps[d[keyAttr]] = d.get(valueAttr)
        return maps


#//////////////////////////////////////////////////////////////////////////////

# ~ 0 ~
# Fetch data
status_msg('Loading the latest data exports...')

# connect to db (token is generated on run)
db = Molgenis(url=host, token=token)

# get patients
raw_subjects = dt.Frame(
    db.get(
        entity = 'cosasportal_patients',
        batch_size = 10000
    )
)

# get clinical and phenotying data (BenchCNV)
raw_clinical = dt.Frame(
    db.get(
        entity = 'cosasportal_diagnoses',
        batch_size = 10000
    )
)

raw_benchcnv = dt.Frame(
    db.get(
        entity = 'cosasportal_benchcnv_prepped',
        batch_size = 10000
    )
)

cineasmappings = dt.Frame(
    db.get(
        entity = 'cosasportal_cineasmappings',
        batch_size = 10000
    )
)

# get samples data from the portal
raw_samples = dt.Frame(
    db.get(
        entity = 'cosasportal_samples',
        batch_size = 10000
    )
)

# get array data from the portal (x2)
raw_array_adlas = dt.Frame(
    db.get(
        entity = 'cosasportal_labs_array_adlas',
        batch_size = 10000
    )
)

raw_array_darwin = dt.Frame(
    db.get(
        entity = 'cosasportal_labs_array_darwin',
        batch_size = 10000
    )
)

# get ngs data from the portal (x2)
raw_ngs_adlas = dt.Frame(
    db.get(
        entity = 'cosasportal_labs_ngs_adlas',
        batch_size = 10000
    )
)

raw_ngs_darwin = dt.Frame(
    db.get(
        entity = 'cosasportal_labs_ngs_darwin',
        batch_size = 10000
    )
)

# delete _href column (not necessary, but helpful for local dev)
del raw_subjects['_href']
del raw_clinical['_href']
del raw_benchcnv['_href']
del cineasmappings['_href']
del raw_samples['_href']
del raw_array_adlas['_href']
del raw_array_darwin['_href']
del raw_ngs_adlas['_href']
del raw_ngs_darwin['_href']


# create a list of unique subject identifiers
cosasSubjectIdList = list(set(raw_subjects[:, 'UMCG_NUMBER'].to_list()[0]))

# ~ 0a ~
# Pull COSAS Portal Mappings
#
# The following objects allow internal data to be mapped to the unified model
# terminology. If you receive a message in this script stating "mapping value
# not found". Add a new record in the corresponding table. Some tables may only
# have a single mapping, but this may change in the future.
#
status_msg('Pulling umcg to UMDM mapping tables...')

genderMappings = cosastools.to_keypairs(
    data = db.get(
        entity='cosasportal_mappings_genderidentity',
        attributes='sourceValue,newValue'
    )
)

biospecimenTypeMappings = cosastools.to_keypairs(
    data = db.get(
        entity='cosasportal_mappings_biospecimentype',
        attributes='sourceValue,newValue'
    )
)

sampleReasonMappings = cosastools.to_keypairs(
    data = db.get(
        entity='cosasportal_mappings_samplereason',
        attributes='sourceValue,newValue,newValueSecondary'
    )
)


sequencerPlatformMappings = cosastools.to_keypairs(
    data = db.get(
        entity='cosasportal_mappings_sequencerinfo',
        attributes='sourceValue,newValue'
    ),
    keyAttr = 'sourceValue',
    valueAttr = 'newValue'
)

sequencerInstrumentMappings = cosastools.to_keypairs(
    data = db.get(
        entity='cosasportal_mappings_sequencerinfo',
        attributes='sourceValue,newValueSecondary'
    ),
    keyAttr = 'sourceValue',
    valueAttr = 'newValueSecondary'
)

genomeBuildMappings = db.get(
    entity='cosasportal_mappings_genomebuild',
    attributes='sourceValue,newValue,newValueSecondary'
)

cineasHpoMappings = cosastools.to_keypairs(
    data = db.get(
        entity='cosasportal_cineasmappings',
        attributes='code,hpo'
    ),
    keyAttr = 'code',
    valueAttr = 'hpo'
)


#//////////////////////////////////////////////////////////////////////////////

status_msg('')

# ~ 1 ~
# Build Subjects Table
#
# Map COSAS portal data into harmonized model structure for subject metadata.
# For COSAS, we will be populating the columns of interest these are listed
# below. All personal identifier columns will be validated against `subjectID`
# Therefore, any ID that does not exist in the export should not be referenced
# in this export.
#
# NOTE: Row level metadata will be applied at the end of the script.
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
        'genderIdentity': f.GESLACHT,
        'ageAtDeath': None,
        'primaryOrganization': 'UMCG'
    }
][:, :, dt.sort(as_type(f.subjectID, int))]


#
# ~ 1a ~
# Identify new linked family members
#
# In the new data, find subjects that do not exist in the following columns:
# `belongsWithFamilyMembers`. These IDs are import to keep, but it throws
# an error because the referenced IDs do not exist in the column `subjectID`.
# Instead of removing the IDs, it is better to register these cases as new
# COSAS subjects.
#
# The following code identifies missing IDs, creates a new COSAS record, and
# appends them to the main subject dataset.
#
status_msg('Identifying unregistered family member identifiers...')

maternalIDs = subjects['belongsToMother'].to_list()[0]
paternalIDs = subjects['belongsToFather'].to_list()[0]
familyData = subjects[:, (f.belongsWithFamilyMembers, f.belongsToFamily,f.subjectID)].to_tuples()

belongsWithFamilyMembers = dt.Frame()
for entity in familyData:
    if not (entity[0] is None):
        ids = [d.strip() for d in entity[0].split(',') if not (d is None) or (d != '')]
        for el in ids:
            
            # value must not be blank, not equal to subject ID, and isn't a known ID
            if (
                (el != '') and
                (el != entity[2]) and
                (el not in cosasSubjectIdList) and
                (el not in maternalIDs) and
                (el not in paternalIDs)
            ):
                belongsWithFamilyMembers.rbind(
                    dt.Frame([
                        {
                            'subjectID': el,
                            'belongsToFamily': entity[1],
                            'belongsWithFamilyMembers': entity[0],
                            'comments': 'manually registered in COSAS'
                        }
                    ])
                )
                
del entity, ids, el

# select unique subjects only
belongsWithFamilyMembers = belongsWithFamilyMembers[
    :, first(f[:]), dt.by('subjectID')
][:, :, dt.sort(as_type(f.subjectID, int))]

status_msg(
    "Identified {} family members that aren't in the export..."
    .format(belongsWithFamilyMembers.nrows)
)


# ~ 1b ~
# Identify new material identifiers
#
# In the subjects dataset, check all values in the the column `belongsToMother`
# to make sure the ID exists in the `subjectID` column. Rather than removing 
# values from COSAS, unknown identifiers will be registered as new subjects.
#
status_msg('Identifying new maternal identifiers...')

belongsToMother = dt.Frame([
    {
        'subjectID': d[0],
        'belongsToFamily': d[1],
        'genderIdentity': 'Vrouw',
        'comments': 'manually registered in COSAS'
    } for d in subjects[:, (f.belongsToMother, f.belongsToFamily)].to_tuples()
    if not (d[0] is None) and not (d[0] in cosasSubjectIdList)
])

status_msg(
    "Identified {} new maternal identifiers that aren't in the export..."
    .format(belongsToMother.nrows)
)


# ~ 1c ~
# Identify new paternal identifiers
#
# Check all values in the column `belongsToFather` to make sure the ID
# exists in the `subjectID` column.
#
status_msg('Identifying new paternal identifiers...')
belongsToFather = dt.Frame([
    {
        'subjectID': d[0],
        'belongsToFamily': d[1],
        'genderIdentity': 'Man',
        'comments': 'manually registered in COSAS'
    } for d in subjects[:, (f.belongsToFather, f.belongsToFamily)].to_tuples()
    if not (d[0] is None) and not (d[0] in cosasSubjectIdList)
])

status_msg(
    "Identified {} new maternal identifiers that aren't in the export..."
    .format(belongsToFather.nrows)
)

#
# ~ 1d ~
# Combine all new subject identifiers
#
# Like the column `belongsWithFamilyMembers`, we will also check the columns
# `belongsToMother` and `belongsToFather` to make sure all subjects are properly
# registered in COSAS. The following code will also bind new family members so
# that we can bind the data in one step.
#

status_msg('Creating new subjects to register dataset...')
subjectsToRegister = dt.rbind(
    belongsToMother,
    belongsToFather,
    belongsWithFamilyMembers,
    force = True
)

status_msg('Registering {} new subjects'.format(subjectsToRegister.nrows))
del belongsWithFamilyMembers
del belongsToMother
del belongsToFather


#
# ~ 1e ~
# Merge and format subject data
#
# In this step, we will create the table `umdm_subjects` using the objects
# `subjects` and `subjectsToRegister`. Afterwards, several columns will need
# to be recoded or formated for MOLGENIS.
#
#
# Bind `subjectsToRegister` with subjects so that all columns can be formated
# at once. Make sure distinct cases are selected and the dataset is sorted by
# ID.
#
status_msg('Binding subjects with new subjects...')

subjects = dt.rbind(subjects, subjectsToRegister, force = True)[
    :, first(f[:]), dt.by(f.subjectID)
][:, :, dt.sort(as_type(f.subjectID, int))]


# Format `belongsWithFamilyMembers`: trimws, remove subject ID
status_msg('Formating linked Family IDs...')
subjects['belongsWithFamilyMembers'] = dt.Frame([
    cosastools.collapseFamilyIDs(d[0],d[1])
    for d in subjects[:, (f.belongsWithFamilyMembers, f.subjectID)].to_tuples()
])


# map gender values to `umdm_lookups_genderIdentity`
status_msg('Recoding gender identity...')
subjects['genderIdentity'] = dt.Frame([
    cosastools.recodeValue(
        mappings = genderMappings,
        value = d,
        label = 'genderIdentity'
    )
    for d in subjects['genderIdentity'].to_list()[0]
])


# format date columns to the correct format (yyyy-mm-dd)
status_msg('Transforming and calculating date variables...')

# format `dateOfBirth` as yyyy-mm-dd
subjects['dateOfBirth'] = dt.Frame([
    cosastools.formatAsDate(date = d, pattern = '%d-%m-%Y')
    for d in subjects['dateOfBirth'].to_list()[0]
])

# format `yearOfBirth` as yyyy
subjects['yearOfBirth'] = dt.Frame([
    cosastools.formatAsYear(d)
    for d in subjects['dateOfBirth'].to_list()[0]
])


# format `dateOfDeath` as yyyy-mm-dd
subjects['dateOfDeath'] = dt.Frame([
    cosastools.formatAsDate(date = d, pattern = '%d-%m-%Y')
    for d in subjects['dateOfDeath'].to_list()[0]
])


# format `yearOfDeath` as yyyy
subjects['yearOfDeath'] = dt.Frame([
    cosastools.formatAsYear(d) for d in subjects['dateOfDeath'].to_list()[0]
])

# using `dateOfDeath` set `subjectStatus`
subjects['subjectStatus'] = dt.Frame([
    'Dead' if bool(d) else None
    for d in subjects['dateOfDeath'].to_list()[0]
])

# calcuate `ageAtDeath` if `dateOfDeath` is defined
subjects['ageAtDeath'] = dt.Frame([
    cosastools.calcAge(
        earliest = d[0],
        recent = d[1]
    ) for d in subjects[:, (f.dateOfBirth, f.dateOfDeath)].to_tuples()
])


# format dates as string now that age calcuations are complete. Otherwise, you 
# will get an error when the data is imported.
subjects['dateOfBirth'] = dt.Frame([
    str(d) if bool(d) else None for d in subjects['dateOfBirth'].to_list()[0]
])

subjects['dateOfDeath'] = dt.Frame([
    str(d) if bool(d) else None for d in subjects['dateOfDeath'].to_list()[0]
])


# track records and cleanup
status_msg('Mapped {} new records'.format(subjects.nrows))
del maternalIDs, paternalIDs
del subjectsToRegister
del familyData

#//////////////////////////////////////////////////////////////////////////////

status_msg('')
status_msg('==== Building COSAS Clinical ====')

# ~ 2 ~
# Build Phenotypic Data from workbench export
#
# This dataset provides historical records on observedPhenotypes for older cases.
# This allows us to populate the COSAS Clinical table with extra information. 
status_msg('Mapping historical phenotypic data...')

# Process data from external provider
confirmedHpoDF = raw_benchcnv[:, {'clinicalID':f.subjectID, 'observedPhenotype': f.observedPhenotype}]
confirmedHpoDF['keep'] = dt.Frame([
    d in cosasSubjectIdList
    for d in confirmedHpoDF['clinicalID'].to_list()[0]
])

confirmedHpoDF = confirmedHpoDF[f.keep == True, :]
confirmedHpoDF.key = 'clinicalID'
del confirmedHpoDF['keep']


# ~ 2a ~
# Build COSAS Clinical Table
#
# Map data from the portal into the preferred structure of the harmonized
# model's (HM) clinical table. The mappings will be largely based on the
# attribute `certainty`. Values will be mapped into one of the phenotype
# allowed in this table (at the moment). Use the reference table,
# columns (observed, unobserved, or provisional).
# 
# Only HPO codes are `cosasportal_cineasmappings` to map CINEAS codes to HPO.
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
status_msg('Formatting CINEAS codes and mapping to HPO...')

clinical['code'] = dt.Frame([
    d.split(':')[0] if d else None
    for d in clinical['code'].to_list()[0]
])

# map cineas codes to HPO
clinical['hpo'] = dt.Frame([
    cosastools.recodeValue(
        mappings = cineasHpoMappings,
        value = d,
        label = 'Cineas-HPO',
        warn = False
    )
    for d in clinical['code'].to_list()[0]
])


# format certainty rating
# Certainty is used to determine which code is a provisional or an unobserved
# phenotype code. Confirmed phenotype is only available in the
# Cartagenia export. 
status_msg('Formating certainty ratings and triaging HPO codes...')
clinical['certainty'] = dt.Frame([
    d.lower().replace(' ', '-') if (d != '-') and (d) else None
    for d in clinical['certainty'].to_list()[0]
])

# create `provisionalPhenotype`: uncertain, missing, or certain
provisionalCertaintyRatings = ['zeker','niet-zeker','onzeker',None]
clinical['provisionalPhenotype'] = dt.Frame([
    d[0] if (d[1] in provisionalCertaintyRatings) and (d[0]) else None
    for d in clinical[:, (f.hpo, f.certainty)].to_tuples()
])

# create `excludedPhenotype`: zeker-niet
clinical['unobservedPhenotype'] = dt.Frame([
    d[0] if d[1] in ['zeker-niet'] else None
    for d in clinical[:, (f.hpo, f.certainty)].to_tuples()
])


# Collapse all phenotypic codes by subject
# Now that all codes have been identified and mapped to HPO, we can prepare
# the dataset. The shape of the clinical dataset is: one row per subject
# and all HPO codes collapsed into the correct phenotype column. Since we
# aren't capturing phenotype by date (it isn't necessary for COSAS), all codes
# need to be collapsed into a single string. The following function filters
# the dataset for by subject, pulls all HPO codes, and collapses the values
# into a string.
status_msg('Collapsing provisional- and unobserved HPO columns...')   

# collapse all provisionalPhenotype codes by ID
clinical['provisionalPhenotype'] = dt.Frame([
    cosastools.collapseHpoCodes(id = d, column = 'provisionalPhenotype')
    for d in clinical['belongsToSubject'].to_list()[0]
])

# collapse all excludedPhenotype codes by ID
clinical['unobservedPhenotype'] = dt.Frame([
    cosastools.collapseHpoCodes(id = d, column = 'unobservedPhenotype')
    for d in clinical['belongsToSubject'].to_list()[0]
])


del clinical[:, ['certainty','code','hpo']]

# pull unique rows only since codes were duplicated
status_msg('Selecting distinct rows only and merging confirmed HPO data...')

clinical = clinical[:, first(f[1:]), dt.by(f.clinicalID)]
clinical.key = 'clinicalID'
clinical = clinical[:, :, dt.join(confirmedHpoDF)][:, :, dt.sort(as_type(f.clinicalID, int))]

# Check IDs
# Make sure all identifiers in the clinical dataset exist in COSAS
clinical['idExists'] = dt.Frame([
    d in cosasSubjectIdList
    for d in clinical['belongsToSubject'].to_list()[0]
])

if clinical[f.idExists == False,:].nrows > 0:
    status_msg(
        'Error in clinical mappings: Excepted 0 flagged cases, but found {}.'
        .format(clinical[f.idExists == False,:].nrows)
    )
    clinical = clinical[f.idExists, :]

del clinical['idExists']
    
status_msg('Processing {} new records for the clinical table'.format(clinical.nrows))
del confirmedHpoDF

#//////////////////////////////////////////////////////////////////////////////

status_msg('')
status_msg('==== Building COSAS Samples ====')

# ~ 3 ~
# Build umdm_samples
#
# Pull data from `cosasportal_samples` and map to the new samples table.
# Information about the laboratory procedures will be mapped to the 
# samplePreparation and the sequencing tables. The reasonse for 
# reason for the sampling will be populated from the laboratory data
# exports (ADLAS and Darwin). Row level metadata will be added before import
# into Molgenis.
#
#
status_msg('Processing new sample data...')

# Pull attributes of interest
samples = raw_samples[:,
    {
        'sampleID': f.DNA_NUMMER,
        'belongsToSubject': f.UMCG_NUMMER,
        'belongsToRequest': f.ADVVRG_ID,
        # 'dateOfRequest': f.ADVIESVRAAG_DATUM,  # not really needed
        'biospecimenType': f.MATERIAAL,
        # 'alternativeIdentifiers': f.TEST_CODE  # not really needed
    }
]


# collapse request by sampleID into a comma seperated string
status_msg('Formatting request identifiers...')
samples['belongsToRequest'] = dt.Frame([
    ','.join(
        list(
            set(
                samples[
                    f.sampleID == d[0], 'belongsToRequest'
                ].to_list()[0]
            )
        )
    ) for d in samples[:, (f.sampleID, f.belongsToRequest)].to_tuples()
])

# pull unique rows only since codes were duplicated
samples = samples[
    :, first(f[:]), dt.by(f.sampleID)
][
    :, :, dt.sort(as_type(f.belongsToSubject, int))
]

# recode biospecimenType
samples['biospecimenType'] = dt.Frame([
    cosastools.recodeValue(
        mappings = biospecimenTypeMappings,
        value = d.lower(),
        label = 'biospecimenType'
    ) if d else None
    for d in samples['biospecimenType'].to_list()[0]
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

# ~ 4 ~
# Build Sample Prepation and Sequencing Tables
#
# Using the Adlas and Darwin files, map the data into the structure of the
# `samplePreparation` and `sequencing` tables. The column `samplingReason`
# (i.e., `labIndication`) must also be merged with the `samples` table.
#
# In this section, combine the ADLAS and Darwin exports for each test type
# indepently, and then bind them into one object.
#


# ~ 4a ~ 
# Build Array Adlas dataset
# Pull the required columns from the array-adlas dataset. The following
# will further reduce the dataset by distinct rows only. This object will
# be joined with the object defined in the next step.
status_msg('Building Array dataset...')

# ~ 4a.i ~
# Build array-aldas data
status_msg('Processing array-aldas data...')
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
    first(f[:]),  # returns distinct records
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

# ~ 4a.ii ~
# Build array-darwin data
status_msg('Processing array-darwin data...')
array_darwin = raw_array_darwin[
    :, {
        'belongsToSubject': f.UmcgNr,
        'belongsToLabProcedure': f.TestId, # codes are written into ID
        'sequencingDate': f.TestDatum, # recode date
        'reasonForSequencing': f.Indicatie, # format lab indication
        'sequencingMethod': None,
    }
][
    # get distinct rows only
    :, first(f[:]), dt.by(f.belongsToSubject, f.belongsToLabProcedure)
][
    :, (
        f.belongsToSubject,
        f.belongsToLabProcedure,
        f.sequencingDate,
        f.reasonForSequencing
    ),
    dt.sort(as_type(f.belongsToSubject, int))
]

# ~ 4a.iii ~
# Create full arrayData object
status_msg('Creating object "arrayData"')
array_darwin.key = ['belongsToSubject','belongsToLabProcedure']
arrayData = array_adlas[:, :, dt.join(array_darwin)]

del array_darwin, array_adlas


# ~ 4b ~
# Build NGS Dataset
#
# Like the Array dataset, the NGS dataset consists of data from ADLAS and
# Darwin. Each dataset will be processed independently, and the merged.
# The NGS and Adlas dataset will be merged to create the main dataset that
# will be used create teh sampleprep and sequencing tables.
status_msg('Building NGS dataset...')

# ~ 4b.i ~
# Process ngs-aldas data
status_msg('Processing ngs-adlas data...')
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

# ~ 4b.ii ~
# reshape: NGS data from Darwin
status_msg('Processing ngs-darwin data...')
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

# ~ 4b.iii ~
# Create ngsData
status_msg('Creating object "ngsData"')
ngs_darwin.key = ['belongsToSubject', 'belongsToLabProcedure']
ngsData = ngs_adlas[:, :, dt.join(ngs_darwin)]


# ~ 4c ~
# Create main sample-labs dataset
#
# Using the arrayData and ngsData objects created in the previous steps,
# create the main sample+labs dataset that will be used to create the
# sampleprep and sequencing tables.
# 
# NOTES:
#   - Some of the column `sampleID` is repeated for ease of mapping. It is
#       easier to process these values in this step rather than independently.
#   - This step also removes unknown samples, i.e. samples that aren't
#       listed in the `samples` table.
#
status_msg('Merging array and ngs dataset to create sample+lab tables...')

sampleSequencingData = dt.rbind(arrayData, ngsData, force=True)
sampleSequencingData[
    :, dt.update(
        belongsToSample = f.sampleID,
        belongsToSamplePreparation = f.sampleID
    )
]

# ~ 4c.ii ~
# Filter dataset for known samples
#
# Remove entries that aren't registered in samples table. It isn't clear why a
# sample appears in the darwin data and not the adlas dataset. It is possible
# that some of the samples aren't authorized, or were never authorized, by the
# lab.
#
status_msg('Filtering sample+lab data for known samples...')

registeredSamples = samples['sampleID'].to_list()[0]

sampleSequencingData['flag'] = dt.Frame([
    d in registeredSamples
    for d in sampleSequencingData['belongsToSample'].to_list()[0]
])

sampleSequencingData = sampleSequencingData[f.flag == True, :]


# ~ 4c.iii ~
# Prepare data
#
# Apply additional transformations and any recoding. In order to make
# each sample 'unique' the row identifier is a concatenation of multiple IDs.
# These are: sampleID + requestID + labProcedure. At some point, we may want
# to change this format
#

# create unique identifier: sampleID + request + belongsToLabProcedure
status_msg('Setting unqiue identifiers (primary key)...')

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
status_msg('Formatting sequencing date...')
sampleSequencingData['sequencingDate'] = dt.Frame([
    cosastools.formatAsDate(
        date = d,
        pattern = '%d-%m-%Y %H:%M:%S',
        asString = True
    )
    for d in sampleSequencingData['sequencingDate'].to_list()[0]
])


# format `labIndication`: use urdm_lookups_samplingReason
status_msg('Mapping reasons for sequencing...')
sampleSequencingData['reasonForSequencing'] = dt.Frame([
    cosastools.recodeValue(
        mappings = sampleReasonMappings,
        value = d.lower(),
        label = 'reasonForSequencing'
    ) if bool(d) else None
    for d in sampleSequencingData['reasonForSequencing'].to_list()[0]
])


# recode `sequencingPlatform`
status_msg('Recoding sequencingPlatform...')
sampleSequencingData['sequencingPlatform'] = dt.Frame([
    cosastools.recodeValue(
        mappings = sequencerPlatformMappings,
        value = d,
        attr = 'platform',
        label = 'sequencingPlatform'
    ) if bool(d) else None
    for d in sampleSequencingData['sequencingPlatform'].to_list()[0]
])

# recode `sequencingInstrumentModel`
status_msg('Recoding sequencing instrument model...')
sampleSequencingData['sequencingInstrumentModel'] = dt.Frame([
    cosastools.recodeValues(
        data = sequencerInstrumentMappings,
        value = d,
        type = 'model'
    ) for d in sampleSequencingData['sequencingInstrumentModel'].to_list()[0]
])

# recode `genomeBuild`
sampleSequencingData['referenceGenomeUsed'] = dt.Frame([
    cosastools.recodeGenomeBuild(d) for d in sampleSequencingData['referenceGenomeUsed'].to_list()[0]
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

# set record-level metadata
subjects[:, dt.update(
    dateRecordCreated=cosastools.timestamp(),
    recordCreatedBy=createdBy
)]

clinical[:, dt.update(
    dateRecordCreated=cosastools.timestamp(),
    recordCreatedBy=createdBy
)]

samples[:, dt.update(
    dateRecordCreated=cosastools.timestamp(),
    recordCreatedBy=createdBy
)]

samplePreparation[:, dt.update(
    dateRecordCreated = cosastools.timestamp(),
    recordCreatedBy=createdBy
)]

sequencing[:, dt.update(
    dateRecordCreated=cosastools.timestamp(),
    recordCreatedBy=createdBy
)]

# convert to list of dictionaries (make sure all nan's are recoded!), and save
status_msg('Importing data to...')

# db.delete(entity='cosasportal_patients')
# db.delete(entity='cosasportal_diagnoses')
# db.delete(entity='cosasportal_samples')
# db.delete(entity='cosasportal_benchcnv')
# db.delete(entity='cosasportal_benchcnv_prepped')
# db.delete(entity='cosasportal_labs_array_adlas')
# db.delete(entity='cosasportal_labs_array_darwin')
# db.delete(entity='cosasportal_labs_ngs_adlas')
# db.delete(entity='cosasportal_labs_ngs_darwin')
# db.delete(entity='umdm_subjects')
# db.delete(entity='umdm_samples')

# Prepare import for umdm_subjects
umdm_subjects = subjects.to_pandas().replace({np.nan: None}).to_dict('records')
umdm_subject_ids = subjects[
    :,(f.subjectID, f.dateRecordCreated,f.recordCreatedBy)
].to_pandas().replace({np.nan: None}).to_dict('records')

db.importData(entity='umdm_subjects', data=umdm_subject_ids)
db.updateData(entity='umdm_subjects', data=umdm_subjects)

# prepare import for umdm_samples
umdm_samples = samples.to_pandas().replace({np.nan: None}).to_dict('records')
db.importData(entity='umdm_samples', data = umdm_samples)