#'////////////////////////////////////////////////////////////////////////////
#' FILE: mappings_cosas.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-10-05
#' MODIFIED: 2022-04-06
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
import pytz
import re

# uncomment when deployed
host = 'http://localhost/api/'
token = '${molgenisToken}'
createdBy = 'cosasbot'

# only for local dev
# from dotenv import load_dotenv
# from os import environ
# load_dotenv()
# host = environ['MOLGENIS_HOST_ACC']
# token = environ['MOLGENIS_TOKEN_ACC'] 

# generic status message with timestamp
def status_msg(*args):
    """Status Message
    Print a log-style message, e.g., "[16:50:12.245] Hello world!"

    @param *args one or more strings containing a message to print
    @return string
    """
    message = ' '.join(map(str, args))
    time = datetime.now(tz=pytz.timezone('Europe/Amsterdam')).strftime('%H:%M:%S.%f')[:-3]
    print(f'[{time}] {message}')


# custom logs
class cosasLogger:
    def __init__(self, logname: str='cosas-daily-import', silent=False, printWithTime=True):
        """Cosas Logger
        Keep records of all processing steps and summarize the daily imports
        
        @param logname : name of the log
        @param silent : If True, all messages will be disabled
        @param printWithTime: If True and silent is False, all messages will be
            printed with timestamps
        """
        self.silent = silent
        self.logname = logname
        self.log = {}
        self.currentStep = {}
        self.processingStepLogs = []
        self._printWithTime = printWithTime
    
    def _now(self, strftime=None):
        if strftime:
            return datetime.now(tz=pytz.timezone('Europe/Amsterdam')).strftime(strftime)
        return datetime.now(tz=pytz.timezone('Europe/Amsterdam'))
        
    def _printMsg(self, message):
        if not self.silent:
            if self._printWithTime:
                message = f"[{self._now(strftime='%H:%M:%S.%f')[:-3]}] {message}"
            print(message)
       
    def __stoptime__(self, name):
        timeFormat = '%Y-%m-%dT%H:%M:%SZ'
        log = self.__getattribute__(name)
        log['endTime'] = self._now()
        log['elapsedTime'] = (log['endTime'] - log['startTime']).total_seconds()
        log['endTime'] = log['endTime'].strftime(timeFormat)
        log['startTime'] = log['startTime'].strftime(timeFormat)
        self.__setattr__(name, log)
       
    def start(self):
        """Start Log
        Start logs for an entire job, script, action, etc.
        """
        self.log = {
            'identifier': self._now(strftime='%Y-%m-%d'),
            'name': self.logname,
            'date': self._now(strftime='%Y-%m-%d'),
            'databaseName': 'cosas',
            'startTime': self._now(),
            'endTime': None,
            'elapsedTime': None,
            'steps': [],
            'comments': None
        }
        
        self._printMsg(
            '{}: log started at {}'
            .format(self.logname, self.log['startTime'].strftime('%H:%M:%S'))
        )
       
    def stop(self):
        """Stop Log
        End logging at the end of job, script, etc.
        """
        self.__stoptime__(name='log')
        self.log['steps'] = ','.join(map(str, self.log['steps']))
        self._printMsg(
            'Logging stopped (elapsed time: {} seconds)'
            .format(self.log['elapsedTime'])
        )

    def startProcessingStepLog(self, type: str=None, name: str=None, tablename: str=None):
        """Start a new log for a processing step
        Create a new logging object for an individual step such as transforming
        data or importing data.
        
        @param type : data handling type (see lookups)
        @param name : name of the current step (e.g., 'import-data', 'save-data')
        @param tablename : database table the current step relates to
        """
        stepID = len(self.processingStepLogs) + 1
        self.currentStep = {
            'identifier': int(f"{self._now(strftime='%Y%m%d')}{stepID}"),
            'date': self._now(strftime='%Y-%m-%d'),
            'name': name,
            'step': type,
            'databaseTable': tablename,
            'startTime': self._now(),
            'endTime': None,
            'elapsedTime': None,
            'status': None,
            'comment': None
        }
        
        self._printMsg('{}: starting step {}'.format(self.logname, name))
       
    def stopProcessingStepLog(self):
        """Stop a log for a processing step
        Stop logging for the current step
        
        @return confirmation message
        """
        self.__stoptime__(name='currentStep')
        self.log['steps'].append(self.currentStep['identifier'])
        self.processingStepLogs.append(self.currentStep)
        
        self._printMsg(
            '{}: finished step {} in {} seconds'
            .format(
                self.logname,
                self.currentStep['name'],
                self.currentStep['elapsedTime']
            )
        )

# extend molgenis.Session class
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
            self._POST(url=url, data=data, label=str(entity))
            
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
            self._PUT(url=url, data=data, label=f'{entity}/{attr}')
        
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
        except AttributeError:
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
        return datetime.now(tz=pytz.timezone('Europe/Amsterdam')).strftime('%Y-%m-%dT%H:%M:%SZ')
        
    @staticmethod
    def to_keypairs(data, keyAttr='from', valueAttr='to'):
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
        
    @staticmethod
    def to_records(data):
        """Datatable object to records
        @param data : datatable object
        @return list of dictionaries
        """
        return data.to_pandas().replace({np.nan: None}).to_dict('records')


#//////////////////////////////////////////////////////////////////////////////

# ~ 99 ~
# Initial Steps
# Steps to run before starting the mapping steps

# connect to db (token is generated on run)
db = Molgenis(url=host, token=token)

# init logs
status_msg('COSAS: starting job...')
cosaslogs = cosasLogger(silent=True)
cosaslogs.start()    

#////////////////////////////////////////////////////////////////////////////// 

# ~ 0 ~
# Fetch data
# Load all data from the portal. Including the cineas-hpo mappings. Cartagenia
# should also be pulled, but only the prepared dataset. If you have an new
# release of the Cartagenia data, import it into `cosasportal_benchcnv`, and
# then run the cosasportal_benchcnv_prep.py script. The prepped data will be
# uploaded to 'cosasportal_benchcnv_prepped'.

status_msg('COSAS Portal: Loading the latest data exports...')
cosaslogs.startProcessingStepLog(
    type='Data retrieval',
    name='Fetch portal data',
    tablename="cosasportal"
)

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
        entity = 'cosasportal_cartagenia',
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
        attributes = 'DNA_NUMMER,UMCG_NUMMER,ADVVRG_ID,MATERIAAL,TEST_CODE,TEST_OMS',
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

# get labprocedures
activeTestCodes = dt.Frame(
    db.get(
        entity='umdm_labProcedures',
        attributes='code'
    )
)

# delete _href column (not necessary, but helpful for local dev)
# del raw_subjects['_href']
# del raw_clinical['_href']
# del raw_benchcnv['_href']
# del cineasmappings['_href']
# del raw_samples['_href']
# del raw_array_adlas['_href']
# del raw_array_darwin['_href']
# del raw_ngs_adlas['_href']
# del raw_ngs_darwin['_href']
# del activeTestCodes['_href']

# ~ 0a ~
# Before we move on, check to see if the objects are empty. If any of these
# datasets are, then quit the job. It is likely that something failed during
# the file import process.
datasets = {
    'subjects': raw_subjects,
    'samples': raw_samples,
    'clinical': raw_clinical,
    'array_adlas': raw_array_adlas,
    'array_darwin': raw_array_darwin,
    'ngs_adlas': raw_ngs_adlas,
    'ngs_darwin': raw_ngs_darwin
}

# test nrows: stop at first empty dataset
for data in datasets:
    if not datasets[data].nrows:

        cosaslogs.currentStep['status'] = 'Source Data Not Available'
        cosaslogs.currentStep['comment'] = f'Object {data} is empty'
        cosaslogs.stopProcessingStepLog()
        
        cosaslogs.stop()
        db.importData(entity='cosasreports_processingsteps',data=cosaslogs.processingStepLogs)
        db.importData(entity='cosasreports_imports', data=[cosaslogs.log])
        
        raise SystemError(f'Source data cannot be found for {data}')

# continue
del datasets
cosaslogs.currentStep['status'] = 'Success'
cosaslogs.stopProcessingStepLog()

# ~ 0b ~
# Pull COSAS Portal Mappings
#
# The following objects allow internal data to be mapped to the unified model
# terminology. If you receive a message in this script stating "mapping value
# not found". Add a new record in the corresponding table. Some tables may only
# have a single mapping, but this may change in the future.

status_msg('COSAS Portal: Pulling mapping tables...')
cosaslogs.startProcessingStepLog(
    type='Data retrieval',
    name='Fetch mapping tables',
    tablename='cosasportal'
)

genderMappings = cosastools.to_keypairs(
    data = db.get('cosasportal_mappings_genderatbirth')
)

biospecimenTypeMappings = cosastools.to_keypairs(
    data = db.get('cosasportal_mappings_biospecimentype')
)

sampleReasonMappings = cosastools.to_keypairs(
    data = db.get('cosasportal_mappings_samplereason')
)

sequencerPlatformMappings = cosastools.to_keypairs(
    data = db.get('cosasportal_mappings_sequencerinfo')
)

sequencerInstrumentMappings = cosastools.to_keypairs(
    data = db.get('cosasportal_mappings_sequencerinfo'),
    keyAttr = 'from',
    valueAttr= 'toAlternate'
)

genomeBuildMappings = cosastools.to_keypairs(
    data = db.get('cosasportal_mappings_genomebuild')
)

cineasHpoMappings = cosastools.to_keypairs(
    data = db.get('cosasportal_cineasmappings', attributes='code,hpo'),
    keyAttr = 'code',
    valueAttr = 'hpo'
)

cosaslogs.currentStep['status'] = 'Success'
cosaslogs.stopProcessingStepLog()

#//////////////////////////////////////////////////////////////////////////////

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
status_msg('Subjects: building initial table structure...')
cosaslogs.startProcessingStepLog(
    type='Data Processing',
    name='Build initial table structure',
    tablename='subjects'
)

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
        'genderAtBirth': f.GESLACHT,
        'ageAtDeath': None,
        'primaryOrganization': 'UMCG'
    }
][:, :, dt.sort(as_type(f.subjectID, int))]

# create a list of unique subject identifiers --- very important!!!!
cosasSubjectIdList = list(set(subjects[:, 'subjectID'].to_list()[0]))


# save row count and set status
cosaslogs.currentStep['comment'] = f'Initial subjects count: {subjects.nrows}'
cosaslogs.currentStep['status'] = 'Success' if subjects.nrows else 'Error'
cosaslogs.stopProcessingStepLog()


#
# NOTE: WILL NOT DO STEP "1a" FOR NOW.
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
# status_msg('Identifying unregistered family member identifiers...')

# maternalIDs = subjects['belongsToMother'].to_list()[0]
# paternalIDs = subjects['belongsToFather'].to_list()[0]
# familyData = subjects[:, (f.belongsWithFamilyMembers, f.belongsToFamily,f.subjectID)].to_tuples()

# belongsWithFamilyMembers = dt.Frame()
# for entity in familyData:
#     if not (entity[0] is None):
#         ids = [d.strip() for d in entity[0].split(',') if not (d is None) or (d != '')]
#         for el in ids:            
#             # value must: not be blank, not equal to subjectID, and does not exist
#             if (
#                 (el != '') and
#                 (el != entity[2]) and
#                 (el not in cosasSubjectIdList) and
#                 (el not in maternalIDs) and
#                 (el not in paternalIDs)
#             ):
#                 belongsWithFamilyMembers.rbind(
#                     dt.Frame([
#                         {
#                             'subjectID': el,
#                             'belongsToFamily': entity[1],
#                             'belongsWithFamilyMembers': entity[0],
#                             'comments': 'manually registered in COSAS'
#                         }
#                     ])
#                 )
                
# del entity, ids, el

# select unique subjects only
# belongsWithFamilyMembers = belongsWithFamilyMembers[
#     :, first(f[:]), dt.by('subjectID')
# ][:, :, dt.sort(as_type(f.subjectID, int))]

# status_msg(
#     "Identified {} family members that aren't in the export..."
#     .format(belongsWithFamilyMembers.nrows)
# )


# ~ 1b ~
# Identify new material identifiers
#
# In the subjects dataset, check all values in the the column `belongsToMother`
# to make sure the ID exists in the `subjectID` column. Rather than removing 
# values from COSAS, unknown identifiers will be registered as new subjects.
#
status_msg('Subjects: Identifying new maternal identifiers...')
cosaslogs.startProcessingStepLog(
    type='Filtering',
    name='Identify new maternalIDs',
    tablename='subjects'
)

belongsToMother = dt.Frame([
    {
        'subjectID': d[0],
        'belongsToFamily': d[1],
        'genderAtBirth': 'Vrouw',
        'comments': 'manually registered in COSAS'
    }
    for d in subjects[:, (f.belongsToMother, f.belongsToFamily)].to_tuples()
    if not (d[0] is None) and not (d[0] in cosasSubjectIdList)
])

# log number of cases found
status_msg('Subjects: found {} new maternal IDs'.format(belongsToMother.nrows))
cosaslogs.currentStep['comment'] = f'New maternalIDs found: {belongsToMother.nrows}'
cosaslogs.currentStep['status'] = 'Success'
cosaslogs.stopProcessingStepLog()


# ~ 1c ~
# Identify new paternal identifiers
#
# Check all values in the column `belongsToFather` to make sure the ID
# exists in the `subjectID` column.

status_msg('Subjects: Identifying new paternal identifiers...')
cosaslogs.startProcessingStepLog(
    type='Filtering',
    name='Identify new paternalIDs',
    tablename='subjects'
)

belongsToFather = dt.Frame([
    {
        'subjectID': d[0],
        'belongsToFamily': d[1],
        'genderAtBirth': 'Man',
        'comments': 'manually registered in COSAS'
    }
    for d in subjects[:, (f.belongsToFather, f.belongsToFamily)].to_tuples()
    if not (d[0] is None) and not (d[0] in cosasSubjectIdList)
])

# log number of cases found
status_msg('Subjects: Identified {} new maternal IDs'.format(belongsToFather.nrows))
cosaslogs.currentStep['comment'] = f'New paternalIDs found: {belongsToFather.nrows}'
cosaslogs.currentStep['status'] = 'Success'
cosaslogs.stopProcessingStepLog()


#
# ~ 1d ~
# Combine all new subject identifiers
#
# Like the column `belongsWithFamilyMembers`, we will also check the columns
# `belongsToMother` and `belongsToFather` to make sure all subjects are properly
# registered in COSAS. The following code will also bind new family members so
# that we can bind the data in one step.
#
status_msg('Subjects: combining all new subjects to register...')
cosaslogs.startProcessingStepLog(
    type='Aggregation',
    name='Merge new parental IDs',
    tablename='subjects'
)

# add `belongsWithFamilyMembers` if processed
subjectsToRegister = dt.rbind(belongsToMother, belongsToFather, force=True)

# log number of cases found
status_msg('Subjects: Will register {} subjects'.format(subjectsToRegister.nrows))
cosaslogs.currentStep['comment'] = f'Added {subjectsToRegister.nrows} rows'
cosaslogs.currentStep['status'] = 'Success'
cosaslogs.stopProcessingStepLog()


# clean up
# del belongsWithFamilyMembers
del belongsToMother
del belongsToFather
# del maternalIDs, paternalIDs
# del familyData

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

status_msg('Subjects: Binding subjects with new subjects...')
cosaslogs.startProcessingStepLog(
    type='Data Processing',
    name='Combine all subjects',
    tablename='subjects'
)

subjects = dt.rbind(subjects, subjectsToRegister, force = True)[
    :, first(f[:]), dt.by(f.subjectID)
][:, :, dt.sort(as_type(f.subjectID, int))]


# log nrows
cosaslogs.currentStep['comment'] = f'total subjects: {subjects.nrows}'
cosaslogs.currentStep['status'] = 'Success' if subjects.nrows else 'Error'
cosaslogs.stopProcessingStepLog()


# transform variables
cosaslogs.startProcessingStepLog(
    type='Data Processing',
    name='Transform columns',
    tablename='subjects'
)

# Format `belongsWithFamilyMembers`: trimws, remove subject ID
status_msg('Subjects: Formating linked Family IDs...')
subjects['belongsWithFamilyMembers'] = dt.Frame([
    cosastools.collapseFamilyIDs(d[0],d[1])
    for d in subjects[:, (f.belongsWithFamilyMembers, f.subjectID)].to_tuples()
])


# map gender values to `umdm_lookups_genderAtBirth`
status_msg('Subjects: Recoding gender at birth...')
subjects['genderAtBirth'] = dt.Frame([
    cosastools.recodeValue(
        mappings = genderMappings,
        value = d,
        label = 'genderAtBirth'
    )
    for d in subjects['genderAtBirth'].to_list()[0]
])


# format date columns to the correct format (yyyy-mm-dd)
status_msg('Subjects: formating date attributes...')

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
status_msg('Subjects: Mapped {} new records'.format(subjects.nrows))
cosaslogs.currentStep['status'] = 'Success' if subjects.nrows else 'Error'
cosaslogs.stopProcessingStepLog()

del subjectsToRegister

#//////////////////////////////////////////////////////////////////////////////


# ~ 2 ~
# Build Phenotypic Data from workbench export
#
# This dataset provides historical records on observedPhenotypes for older cases.
# This allows us to populate the COSAS Clinical table with extra information. 

status_msg('Clinical: mapping historical phenotypic data...')
cosaslogs.startProcessingStepLog(
    type='Data Processing',
    name='Prepare phenotypic data',
    tablename='clinical'
)

# Process data from external provider
confirmedHpoDF = raw_benchcnv[:, {'clinicalID':f.subjectID, 'observedPhenotype': f.observedPhenotype}]
confirmedHpoDF['keep'] = dt.Frame([
    d in cosasSubjectIdList
    for d in confirmedHpoDF['clinicalID'].to_list()[0]
])

confirmedHpoDF = confirmedHpoDF[f.keep == True, :]
confirmedHpoDF.key = 'clinicalID'
del confirmedHpoDF['keep']

# save log
status_msg('Clinical: prepped {} subjects'.format(confirmedHpoDF.nrows))
cosaslogs.currentStep['comment'] = f'prepped phenotypic data for: {confirmedHpoDF.nrows} subjects'
cosaslogs.currentStep['status'] = 'Success' if confirmedHpoDF.nrows else 'Error'
cosaslogs.stopProcessingStepLog()

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
# has HPO codes built in. The mapping dataset was created using SORTA. All
# codes that had a similarity score of 70% or greater were kept.
#
# Since we do not have a unique clinical diagnostic identifier, subjectID will
# be used instead.
#

status_msg('Clinical: building base structure...')
cosaslogs.startProcessingStepLog(
    type='Data Processing',
    name='Build initial table structure',
    tablename='clinical'
)

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

cosaslogs.currentStep['comment'] = f'Initial structure has {clinical.nrows} rows'
cosaslogs.currentStep['status'] = 'Success' if clinical.nrows else 'Error'
cosaslogs.stopProcessingStepLog()

# ~ 2b ~
# Map CINEAS to HPO
# Extract CINEAS code for string before mapping to HPO

status_msg('Clinical: mapping CINEAS codes to HPO...')
cosaslogs.startProcessingStepLog(
    type='Data Processing',
    name='Map CINEAS to HPO',
    tablename='clinical'
)

clinical['code'] = dt.Frame([
    d.split(':')[0] if d else None
    for d in clinical['code'].to_list()[0]
])

clinical['hpo'] = dt.Frame([
    cosastools.recodeValue(
        mappings = cineasHpoMappings,
        value = d,
        label = 'Cineas-HPO',
        warn = False
    )
    for d in clinical['code'].to_list()[0]
])

cosaslogs.stopProcessingStepLog()

# ~ 2c ~
# Process HPO codes based on certainty ratings
# Certainty is used to determine which code is a provisional or an unobserved
# phenotype code. Confirmed phenotype is only available in the Cartagenia
# export. 

status_msg('Clinical: Formating certainty ratings and triaging HPO codes...')
cosaslogs.startProcessingStepLog(
    type='Data Processing',
    name='Process codes based on certainty ratings',
    tablename='clinical'
)

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

cosaslogs.stopProcessingStepLog()

# ~ 2d ~
# Collapse all phenotypic codes by subject
#
# Now that all codes have been identified and mapped to HPO, we can prepare
# the dataset. The shape of the clinical dataset is: one row per subject
# and all HPO codes collapsed into the correct phenotype column. Since we
# aren't capturing phenotype by date (it isn't necessary for COSAS), all codes
# need to be collapsed into a single string. The following function filters
# the dataset for by subject, pulls all HPO codes, and collapses the values
# into a string.

status_msg('Clinical: collapsing HPO columns...')
cosaslogs.startProcessingStepLog(
    type='Data Processing',
    name='Collapsing HPO codes by subject',
    tablename='clinical'
)

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

# update log
del clinical[:, ['certainty','code','hpo']]
cosaslogs.stopProcessingStepLog()

# ~ 2e ~
# Finalize data
#
# Now that the clinical dataset is prepped and all codes have been collapsed
# by subject ID, select distinct rows and merge HPO data. Make sure all
# subject IDs in the clinical table exist in the subjects dataset.

status_msg('Clinical: Selecting distinct rows and merging HPO data...')
cosaslogs.startProcessingStepLog(
    type='Filtering',
    name='Filtering data',
    tablename='clinical'
)

# select distinct rows
clinical = clinical[:, first(f[1:]), dt.by(f.clinicalID)]

# join HPO data
clinical.key = 'clinicalID'
clinical = clinical[:, :, dt.join(confirmedHpoDF)][:, :, dt.sort(as_type(f.clinicalID, int))]


# Check IDs: Make sure all IDs in the clinical dataset exist in subjects
clinical['idExists'] = dt.Frame([
    d in cosasSubjectIdList
    for d in clinical['belongsToSubject'].to_list()[0]
])

# If there are unknown IDs, remove and log counts
if clinical[f.idExists == False,:].nrows > 0:
    status_msg(
        'Clinical: ERROR Excepted 0 flagged cases, but found {}.'
        .format(clinical[f.idExists == False,:].nrows)
    )
    cosaslogs.currentStep['comment'] = 'Rows removed {}'.format(
        cosaslogs.currentStep['comment'], clinical[f.idExists == False,:].nrows
    )
    clinical = clinical[f.idExists, :]
    

status_msg('Clinical: processed {} new records'.format(clinical.nrows))
cosaslogs.currentStep['status'] = 'Success' if clinical.nrows else 'Error'

del clinical['idExists']
del confirmedHpoDF

cosaslogs.stopProcessingStepLog()

#//////////////////////////////////////////////////////////////////////////////

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

# ~ 3a ~
# Build initial table structure
#
# Pull columns of interest and pull unique rows as we aren't interested in
# keeping request IDs, dates, etc. If this information is needed, you will
# need to adjust this step.
status_msg('Samples: building base structure...')
cosaslogs.startProcessingStepLog(
    type='Data Processing',
    name='Build initial table structure',
    tablename='samples'
)

# Pull attributes of interest
# Add: 'belongsToRequest': f.ADVVRG_ID (if needed again)
samples = raw_samples[:,{
    'sampleID': f.DNA_NUMMER,
    'belongsToSubject': f.UMCG_NUMMER,
    'biospecimenType': f.MATERIAAL
}]

# pull unique rows only since codes were duplicated
samples = samples[:, first(f[:]), dt.by(f.sampleID)][
    :, :, dt.sort(as_type(f.belongsToSubject, int))
]

cosaslogs.currentStep['comment'] = f'Samples row count: {samples.nrows}'
cosaslogs.currentStep['status'] = 'Success' if samples.nrows else 'Error'
cosaslogs.stopProcessingStepLog()

# ~ 3b ~
# Transform Columns
# 
# Transform and recode columns that require it. Add additional transformations
# here. If you need additional mapping tables, consider putting the mapping
# dataset in the 'cosasportal_mappings' package and importing the data in step 0.

cosaslogs.startProcessingStepLog(
    type='Data Processing',
    name='Transform columns',
    tablename='samples'
)

samples['biospecimenType'] = dt.Frame([
    cosastools.recodeValue(
        mappings = biospecimenTypeMappings,
        value = d.lower(),
        label = 'biospecimenType'
    )
    for d in samples['biospecimenType'].to_list()[0]
])

cosaslogs.stopProcessingStepLog()

# ~ 3b ~
# Finalize dataset
#
# Make sure all IDs in the samples table exist in other tables. If an ID does
# not exist, remove it and log counts.

status_msg('Samples: Validating subject IDs in the samples dataset...')
cosaslogs.startProcessingStepLog(
    type='Filtering',
    name='Filtering data',
    tablename='samples'
)

samples['idExists'] = dt.Frame([
    d in cosasSubjectIdList
    for d in samples['belongsToSubject'].to_list()[0]
])

if samples[f.idExists == False,:].nrows > 0:
    samples = samples[f.idExists, :]
    status_msg('Samples: ERROR excepted 0 flagged cases, but found {}.'.format(samples.nrows))
    cosaslogs.currentStep['comment'] = f'Rows removed {samples.nrows}'


status_msg('Samples: processed {} new records'.format(samples.nrows))
cosaslogs.currentStep['status'] = 'Success' if samples.nrows else 'Error'

del samples['idExists']

cosaslogs.stopProcessingStepLog()


#//////////////////////////////////////////////////////////////////////////////

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

status_msg('SamplePrep & Sequencing: building array dataset...')
cosaslogs.startProcessingStepLog(
    type='Data Processing',
    name='Build array dataset',
    tablename='samples-sampleprep-seq'
)

# ~ 4a.i ~
# Build array-aldas data
status_msg('SamplePrep & Sequencing: processing array-aldas data...')
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
status_msg('SamplePrep & Sequencing: processing array-darwin data...')
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
status_msg('SamplePrep & Sequencing: joining array objects...')
array_darwin.key = ['belongsToSubject','belongsToLabProcedure']
arrayData = array_adlas[:, :, dt.join(array_darwin)]

# save logs
cosaslogs.currentStep['comment'] = f'Row count for array data: {arrayData.nrows}'
cosaslogs.currentStep['status'] = 'Success' if arrayData.nrows else 'Error'
cosaslogs.stopProcessingStepLog()

del array_darwin, array_adlas


# ~ 4b ~
# Build NGS Dataset
#
# Like the Array dataset, the NGS dataset consists of data from ADLAS and
# Darwin. Each dataset will be processed independently, and the merged.
# The NGS and Adlas dataset will be merged to create the main dataset that
# will be used create teh sampleprep and sequencing tables.

status_msg('SamplePrep & Sequencing: building NGS dataset...')
cosaslogs.startProcessingStepLog(
    type='Data Processing',
    name='Build NGS dataset',
    tablename='samples-sampleprep-seq'
)


# ~ 4b.i ~
# Process ngs-aldas data
status_msg('SamplePrep & Sequencing: processing ngs-adlas data...')
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
status_msg('SamplePrep & Sequencing: processing ngs-darwin data...')
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
status_msg('SamplePrep & Sequencing: merging ngs data...')
ngs_darwin.key = ['belongsToSubject', 'belongsToLabProcedure']
ngsData = ngs_adlas[:, :, dt.join(ngs_darwin)]

# save logs
cosaslogs.currentStep['comment'] = f'Row count for array data: {ngsData.nrows}'
cosaslogs.currentStep['status'] = 'Success' if ngsData.nrows else 'Error'
cosaslogs.stopProcessingStepLog()

del ngs_darwin, ngs_adlas


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

status_msg('SamplePrep & Sequencing: merging ngs and array datasets...')
cosaslogs.startProcessingStepLog(
    type='Data Processing',
    name='Combine Array and NGS data',
    tablename='samples-sampleprep-seq'
)

sampleSequencingData = dt.rbind(arrayData, ngsData, force=True)

# duplicate IDs for later
sampleSequencingData[:, dt.update(
        belongsToSample = f.sampleID,
        belongsToSamplePreparation = f.sampleID
)]

del arrayData, ngsData

# save row count before filtering
cosaslogs.currentStep['status'] = 'Success' if sampleSequencingData.nrows else 'Error'
cosaslogs.stopProcessingStepLog()


# ~ 4c.ii ~
# Filter dataset for known samples
#
# Remove entries that aren't registered in samples table. It isn't clear why a
# sample appears in the darwin data and not the adlas dataset. It is possible
# that some of the samples aren't authorized, or were never authorized, by the
# lab.

status_msg('SamplePrep & Sequencing: filtering data for known samples...')
cosaslogs.startProcessingStepLog(
    type='Filtering',
    name='Filtering data',
    tablename='samples-sampleprep-seq'
)

registeredSamples = samples['sampleID'].to_list()[0]
sampleSequencingData['idExists'] = dt.Frame([
    d in registeredSamples
    for d in sampleSequencingData['belongsToSample'].to_list()[0]
])


if sampleSequencingData[f.idExists == False, :].nrows > 0:
    status_msg(
        "SamplePrep & Sequencing: ERROR expected 0 flagged cases, but found {}"
        .format(sampleSequencingData[f.idExists == False, :].nrows)
    )
    cosaslogs.currentStep['comment'] = 'Rows removed {}'.format(
        sampleSequencingData[f.idExists == False, :].nrows
    )
    sampleSequencingData = sampleSequencingData[f.idExists, :]

# log new row count
cosaslogs.currentStep['status'] = 'Success' if sampleSequencingData.nrows else 'Error'
cosaslogs.stopProcessingStepLog()
    

# ~ 4c.iii ~
# Prepare data
#
# Apply additional transformations and any recoding. In order to make
# each sample 'unique' the row identifier is a concatenation of multiple IDs.
# These are: sampleID + requestID + labProcedure. At some point, we may want
# to change this format
#

status_msg('SamplePrep & Sequencing: Setting unqiue identifiers (primary key)...')
cosaslogs.startProcessingStepLog(
    type='Data Processing',
    name='Transform columns',
    tablename='samples-sampleprep-seq'
)

# create unique identifier: sampleID + request + belongsToLabProcedure (i.e., test code)
# create IDs for multiple tables
sampleSequencingData[['belongsToSamplePreparation','sequencingID']] = dt.Frame([
    f'{d[0]}_{d[1]}_{d[2]}' for d in sampleSequencingData[
        :, (f.belongsToSample,f.belongsToRequest, f.belongsToLabProcedure)
    ].to_tuples()
])

# format `sequencingDate` as yyyy-mm-dd
status_msg('SamplePrep & Sequencing: Formatting sequencing date...')
sampleSequencingData['sequencingDate'] = dt.Frame([
    cosastools.formatAsDate(
        date = d,
        pattern = '%d-%m-%Y %H:%M:%S',
        asString = True
    )
    for d in sampleSequencingData['sequencingDate'].to_list()[0]
])


# format `labIndication`: use urdm_lookups_samplingReason
status_msg('SamplePrep & Sequencing: recoding "reason for sequencing"...')
sampleSequencingData['reasonForSequencing'] = dt.Frame([
    cosastools.recodeValue(
        mappings = sampleReasonMappings,
        value = d.lower(),
        label = 'reasonForSequencing'
    ) if bool(d) else None
    for d in sampleSequencingData['reasonForSequencing'].to_list()[0]
])

# set facility (links with umdm_organizations)
sampleSequencingData['sequencingFacilityOrganization'] = 'UMCG'

# recode `sequencingPlatform`
status_msg('SamplePrep & Sequencing: recoding sequencing platform...')
sampleSequencingData['sequencingPlatform'] = dt.Frame([
    cosastools.recodeValue(
        mappings = sequencerPlatformMappings,
        value = d,
        label = 'sequencingPlatform'
    )
    for d in sampleSequencingData['sequencingPlatform'].to_list()[0]
])

# recode `sequencingInstrumentModel`
status_msg('SamplePrep & Sequencing: recoding sequencing instrument model...')
sampleSequencingData['sequencingInstrumentModel'] = dt.Frame([
    cosastools.recodeValue(
        mappings = sequencerInstrumentMappings,
        value = d,
        label = 'sequencing instrument'
    ) for d in sampleSequencingData['sequencingInstrumentModel'].to_list()[0]
])

# recode `genomeBuild`
status_msg('SamplePrep & Sequencing: recoding reference genome...')
sampleSequencingData['referenceGenomeUsed'] = dt.Frame([
    cosastools.recodeValue(
        mappings = genomeBuildMappings,
        value = d,
        label = 'genome build'
    )
    for d in sampleSequencingData['referenceGenomeUsed'].to_list()[0]
])


cosaslogs.stopProcessingStepLog()

#//////////////////////////////////////

# ~ 4d ~
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

status_msg('Sample Preparation: Selecting relevant columns...')
cosaslogs.startProcessingStepLog(
    type='Data Processing',
    name='Finalize table',
    tablename='sample-preparation'
)

# create: sampleprepation
# Use sequencing ID for table key so that refs can be made with other tables
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

# rename columns and select distinct rows only
samplePreparation.names={'sequencingID': 'sampleID'}
samplePreparation = samplePreparation[:, first(f[:]), dt.by(f.sampleID)]

status_msg('Sample Preparation: Processed {} new records'.format(samplePreparation.nrows))
cosaslogs.currentStep['status'] = 'Success' if samplePreparation.nrows else 'Error'
cosaslogs.stopProcessingStepLog()
 

# create sequencing table
status_msg('Sequencing: Selecting relevant columns...')
cosaslogs.startProcessingStepLog(
    type='Data Processing',
    name='Finalize table',
    tablename='sequencing'
)

sequencing = sampleSequencingData[
    :, (
        f.sequencingID,
        f.belongsToLabProcedure,
        f.belongsToSamplePreparation,
        f.reasonForSequencing,
        f.sequencingDate,
        f.sequencingFacilityOrganization,
        f.sequencingPlatform,
        f.sequencingInstrumentModel,
        # f.sequencingMethod,
        f.referenceGenomeUsed
    )
]

status_msg('Sequencing: Processed {} new records'.format(sequencing.nrows))
cosaslogs.currentStep['status'] = 'Success' if sequencing.nrows else 'Error'

cosaslogs.stopProcessingStepLog()

#//////////////////////////////////////////////////////////////////////////////

# ~ 5 ~
# Process Active Test Codes
#
# Before importing the data, check to see if all testcodes are valid. Use the
# raw datasets to identify codes that do not exist in the table. Rather than
# the processed data as it will catch more cases that will need to be updated.
# This attribute is called 'belongsToLabProcedure' which is a xref to the table
# 'umdm_labProcedures' (fetched in step 0).

status_msg('Validation: checking test codes')
cosaslogs.startProcessingStepLog(
    type = 'Filtering',
    name = 'Identify new test codes',
    tablename='lab-procedures'
)

# bind all testcodes
testcodes = dt.rbind(
    raw_samples[:, ['TEST_CODE','TEST_OMS']],
    raw_array_adlas[:, ['TEST_CODE','TEST_OMS']],
    raw_ngs_adlas[:, ['TEST_CODE','TEST_OMS']],
    raw_array_darwin[:, {'TEST_CODE': f.TestId}],
    raw_ngs_darwin[:, {'TEST_CODE': f.TestId}],
    force = True
)[:, first(f[:]), dt.by('TEST_CODE')]

# test code: is it active?
testcodes['codeExists'] = dt.Frame([
    d in activeTestCodes['code'].to_list()[0]
    for d in testcodes['TEST_CODE'].to_list()[0]
])

# select new cases
if testcodes[f.codeExists == False, :].nrows:
    newTestCodes = testcodes[
        f.codeExists == False,
        {'code': f.TEST_CODE, 'description': f.TEST_OMS}
    ]
    
    status_msg('Validation: Identified {} new codes'.format(newTestCodes.nrows))
    cosaslogs.currentStep['comment'] = 'Identified {} new codes'.format(newTestCodes.nrows)
    
    status_msg('Validation: Importing new testcodes')    
    db.importData(entity='umdm_labProcedures', data=cosastools.to_records(newTestCodes))
    del newTestCodes

else:
    status_msg('Validation: all testcodes passed')

#//////////////////////////////////////////////////////////////////////////////

# ~ 6 ~
# Prep data and import
#
# All primary data tables will be written to csv, and then import via a
# secondary script. Before writing to files, we will need to set a few
# of the row-level metadata attributes.
# 
status_msg('COSAS Import: Preparing to import data...')

# ~ 6a ~
# Set row-level metadata attributes
# For all objects, add date of processing and author (i.e., cosasbot)

status_msg('COSAS Import: setting row-level metadata...')
cosaslogs.startProcessingStepLog(
    type='Data Processing',
    name='setting-row-metadata',
    tablename='all'
)

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

# update row counts in the log
cosaslogs.log['subjects'] = subjects.nrows
cosaslogs.log['clinical'] = clinical.nrows
cosaslogs.log['samples'] = samples.nrows
cosaslogs.log['samplePreparation'] = samplePreparation.nrows
cosaslogs.log['sequencing'] = sequencing.nrows
cosaslogs.stopProcessingStepLog()


# ~ 6b ~
# Clear database tables
# Before the data can be imported, clean up the existing COSAS tables.
status_msg('Clearing COSAS tables....')
cosaslogs.startProcessingStepLog(
    type = 'Data Processing',
    name = 'Clear COSAS tables',
    tablename = 'COSAS'
)

cosastables = [
    'umdm_files',
    'umdm_sequencing',
    'umdm_samplePreparation',
    'umdm_samples',
    'umdm_clinical',
    'umdm_subjects'
]

for table in cosastables:
    status_msg('Clearing', table)
    db.delete(entity = table)
    
cosaslogs.stopProcessingStepLog()


# ~ 6c ~
# Import data
# For objects that have intra-table references, you must run a two step import.
# The first import the reference columns, and then import everything else.
# convert to list of dictionaries (make sure all nan's are recoded!), and save
status_msg('COSAS Import: Importing data...')

# ~ 5b.i ~
# Import data into `umdm_subjects`
# Run in two steps: 1) subject identifiers, 2) the rest of the data
cosaslogs.startProcessingStepLog(
    type='Import',
    name='import-subjects',
    tablename='subjects'
)

umdm_subjects = cosastools.to_records(subjects)
umdm_subject_ids = cosastools.to_records(
    subjects[:,(f.subjectID, f.dateRecordCreated,f.recordCreatedBy)]
)

# import subject identifiers first, and then update rows
status_msg('Importing identifiers...')
db.importData(entity='umdm_subjects', data=umdm_subject_ids)

status_msg('Importing row data...')
db.updateRows(entity='umdm_subjects', data=umdm_subjects)

cosaslogs.stopProcessingStepLog()

# ~ 5b.ii ~
# Import data into 'umdm_clinical'
# This table has an xref with umdm_subjects
cosaslogs.startProcessingStepLog(
    type='Import',
    name='import-clinical',
    tablename='clinical'
)

umdm_clinical = cosastools.to_records(clinical)
db.importData(entity='umdm_clinical', data=umdm_clinical)

# ~ 5b.ii ~
# Import data into 'umdm_samples'
# There is a xref with umdm_subjects. Make sure all subjects in the samples
# dataset exist in the samples table prior to import. (See step 3.)
cosaslogs.startProcessingStepLog(
    type='Import',
    name='import-samples',
    tablename='samples'
)

umdm_samples = cosastools.to_records(samples)
db.importData(entity='umdm_samples', data = umdm_samples)

cosaslogs.stopProcessingStepLog()

# ~ 5b.iii
# Import data into umdm_samplePreparation
# This table has an xref with `umdm_samples`. All sample IDs and subject IDs
# must be imported and exist before importing. This should already have been 
# handled in step 4.
cosaslogs.startProcessingStepLog(
    type='Import',
    name='import-samplepreparation',
    tablename='samplepreparation'
)

umdm_samplePreparation = cosastools.to_records(samplePreparation)
db.importData(entity = 'umdm_samplePreparation', data=umdm_samplePreparation)

cosaslogs.stopProcessingStepLog()

# ~ 5b.iv ~
# Import data into 'umdm_sequencing'
# This table has an xref with `umdm_samplePreparation`. All sample IDs should
# have been validated (see step 4).
cosaslogs.startProcessingStepLog(
    type='Import',
    name='import-sequencing',
    tablename='sequencing'
)

umdm_sequencing = cosastools.to_records(sequencing)
db.importData(entity='umdm_sequencing', data=umdm_sequencing)

cosaslogs.stopProcessingStepLog()


# ~ 5b.v ~
# import logs
cosaslogs.stop()
status_msg(
    'Mapping completed in {} minutes'
    .format(round(cosaslogs.log['elapsedTime'] / 60,3))
)

status_msg('Importing logs...')
db.importData(entity='cosasreports_processingsteps',data=cosaslogs.processingStepLogs)
db.importData(entity='cosasreports_imports', data=[cosaslogs.log])
