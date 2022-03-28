#'////////////////////////////////////////////////////////////////////////////
#' FILE: cartagenia_query.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-03-23
#' MODIFIED: 2022-03-28
#' PURPOSE: run query for cartagenia data
#' STATUS: stable
#' PACKAGES: **see below**
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

import molgenis.client as molgenis
from datatable import dt, f
import numpy as np
import datetime
import requests
import json
import pytz
import re

# only for local dev
# from dotenv import load_dotenv
# from os import environ
# load_dotenv()
# apiUrl = environ['CNV_API_HOST']
# apiToken = environ['CNV_API_TOKEN']

def status_msg(*args):
    """Status Message
    Print a log-style message, e.g., "[16:50:12.245] Hello world!"

    @param *args one or more strings containing a message to print
    @return string
    """
    message = ' '.join(map(str, args))
    time = datetime.datetime.now(tz=pytz.timezone('Europe/Amsterdam')).strftime('%H:%M:%S.%f')[:-3]
    print(f'[{time}] {message}')


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

class Cartagenia:
    """Cartagenia Client"""
    def __init__(self, url, token):
        self.session = requests.Session()
        self._api_url = url
        self._api_token = token
    
    def getData(self):
        try:
            status_msg('Sending request....')
            response = self.session.get(
                url = self._api_url,
                headers = {'x-api-key': self._api_token}
            )
            
            response.raise_for_status()
            
            status_msg('Preparing data...')
            data = response.json()
            
            if 'Output' not in data:
                raise KeyError('Expected object "Output" not found')
            
            return list(eval(data['Output']))
            
        except requests.exceptions.HTTPError as e:
            raise SystemError(e)

def extractIdsFromValue(value):
    """Extract Identifiers from value
    Extract subject ID, maternal ID, and alternative IDs from a string
    @return tuple 
    """
    # 1: default fetus ID; e.g., 99999F, 99999F1, 99999F1.2, etc.
    testA = re.search(
        pattern = r'^([0-9]{1,}((F)|(F[-_])|(F[0-9]{1,2})|(F[0-9]{1,}.[0-9]{1,})))$',
        string=value
    )
    
    # 2: fetus-patient linked ID; e.g., 99999F-88888, 99999_88888, etc.
    testB = re.search(
        pattern = r'^([0-9]{1,}(F|f)?([0-9]{1,2})?[-_=][0-9]{1,})$',
        string=value
    )
    
    if testA:
        return (
            testA.string, # subjectID
            testA.string.split('F')[0], # belongsToMother
            None # alternative identifiers (always none for default patterns)
        )
    elif testB:
        values = re.split(r'[-_=]', testB.string)
        return (
            values[0], # subjectID; optional: .replace('F','')
            values[0].split('F')[0], # belongsToMother
            values[1] # alternative identifiers
        )
    else:
        return None

#//////////////////////////////////////////////////////////////////////////////

# ~ 0 ~
# init db connections
db = Molgenis(url='http://localhost/api/', token = '${molgenisToken}')


# get login information for Cartagenia
apiUrl = db.get(
    entity = 'sys_sec_Token',
    attributes='token',
    q='description=="cartagenia-api-url"'
)[0]['token']

apiToken = db.get(
    entity = 'sys_sec_Token',
    attributes='token',
    q='description=="cartagenia-api-token"'
)[0]['token']

cg = Cartagenia(url = apiUrl, token = apiToken)


# ~ 1 ~
# Build Phenotype Dataset
#
# Pull the latest dataset from Cartagenia, process the data, and import into
# the portal table `cosasportal_cartagenia`. Data will be used in the main data
# processing script ('cosas_mappings.py'). Only columns of interest and records
# that meet the following inclusion criteria are imported into the COSAS portal
# table.
#
# INCLUSION CRITERIA
# Each records must have the following:
#
#   1) a valid subject identifier that starts with the pattern ^([0-9]{1,})
#   2) a valid HPO code that matches the pattern ^(HP:)
#
# All other cases will be removed from the dataset as they do not contain any
# information of use for the COSAS dataset. Should this change at any point,
# please update step 1c accordingly.
#

# ~ 1a ~
# query the Cartagenia endpoint (i.e., lambda function for UMCG data)
status_msg('Querying Cartagenia endpoint....')
rawData = cg.getData()


# ~ 1b ~
# Query the Cartagenia endpoint and extract results
# 
# For the time being, keep all columns in case we need these later. Columns of
# interest are selected in the next step. Convert to datatable.Frame for faster
# data transformatons. The headers were defined by the original Cartagenia
# file. The structure did not change when the export was moved to a private
# endpoint.
status_msg('Processing raw data....')

rawBenchCnv = dt.Frame()
for entity in rawData:
    row = list(entity)
    rawBenchCnv = dt.rbind(
        rawBenchCnv,
        dt.Frame([{
            'primid': row[0],
            'secid': row[1],
            'externalid': row[2],
            'gender': row[3],
            'comment': row[4],
            'phenotype': row[5],
            'created': row[6]
        }])
    )

# ~ 1c ~
# Filter dataset (apply inclusion criteria)
status_msg('Applying inclusion criteria....')
rawBenchCnv['keep'] = dt.Frame([
    (
        bool(re.search(r'^[0-9].*', str(d[0]).strip())) and
        bool(re.search(r'^(HP:)', d[1].strip()))
    )
    if (d[0] is not None) and (d[1] is not None) else False
    for d in rawBenchCnv[:, (f.primid, f.phenotype)].to_tuples()
])

benchcnv = rawBenchCnv[f.keep, :][
    :, (f.primid, f.secid, f.phenotype), dt.sort(f.primid)
]

# ~ 1d ~
# Transform columns
status_msg('Formatting columns....')

# format IDs: remove white space
benchcnv['primid'] = dt.Frame([
    d.strip().replace(' ','')
    for d in benchcnv['primid'].to_list()[0]
])


# Format HPO terms
benchcnv['phenotype'] = dt.Frame([
    ','.join(list(set(d.strip().split())))
    for d in benchcnv['phenotype'].to_list()[0]
])


# set fetus status
benchcnv['isFetus'] = dt.Frame([
    True if re.search(r'^[0-9]{1,}(F|f)', d) else False
    for d in benchcnv['primid'].to_list()[0]
])


# extract subjectID, belongsToMother (maternal ID), and alternative IDs from
# Cartagenia identifier 'primid'.
benchcnv[['subjectID','belongsToMother','alternativeIdentifiers']] = dt.Frame([
    extractIdsFromValue(d[0].strip())
    if d[1] else (d[0],None,None)
    for d in benchcnv[:, (f.primid, f.isFetus)].to_tuples()
])

# check for duplicate entries
if len(list(set(benchcnv['primid'].to_list()[0]))) != benchcnv.nrows:
    raise SystemError(
        'Total number of distinct identifiers ({}) must match row numbers ({})'
        .format(
            len(list(set(benchcnv['primid'].to_list()[0]))),
            benchcnv.nrows
        )
    )

# ~ 1e ~
# Convert data to record set
benchcnv.names = {'primid': 'id', 'secid': 'belongsToFamily', 'phenotype': 'observedPhenotype'}
benchCnvPrepped = benchcnv.to_pandas().replace({np.nan: None}).to_dict('records')

#//////////////////////////////////////////////////////////////////////////////

# ~ 2 ~
# Import data

status_msg('Imporing data into cosasportal...')
db.delete(entity='cosasportal_cartagenia')
db.importData(entity='cosasportal_cartagenia', data=benchCnvPrepped)
