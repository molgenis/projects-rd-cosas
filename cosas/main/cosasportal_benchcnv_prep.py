#'////////////////////////////////////////////////////////////////////////////
#' FILE: cosasportal_benchcnv_prep.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-02-21
#' MODIFIED: 2022-03-02
#' PURPOSE: prep bench cnv dataset before mapping
#' STATUS: stable
#' PACKAGES: **see below**
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

import molgenis.client as molgenis
from datetime import datetime
from datatable import dt, f
import numpy as np
import requests
import json
import pytz
import re

host='http://localhost/api/'
token='${molgenisToken}'

# for local dev only
# from dotenv import load_dotenv
# from os import environ
# load_dotenv()
# host=environ['MOLGENIS_HOST_ACC']
# token=environ['MOLGENIS_TOKEN_ACC']


def status_msg(*args):
    """Status Message
    Print a log-style message, e.g., "[16:50:12.245] Hello world!"

    @param *args one or more strings containing a message to print
    @return string
    """
    message = ' '.join(map(str, args))
    time = datetime.now(tz=pytz.timezone('Europe/Amsterdam')).strftime('%H:%M:%S.%f')[:-3]
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

#//////////////////////////////////////////////////////////////////////////////

# ~ 0 ~
# Fetch Data
# Create connection to molgenis instance and pull benchcnv data from the portal
status_msg('Pulling new data...')

db = Molgenis(url=host, token=token)
benchcnvRaw = dt.Frame(
    db.get(
        entity = 'cosasportal_benchcnv',
        attributes = 'primid,secid,phenotype,id',
        batch_size=10000
    )
)

# del benchcnvRaw['_href']

#//////////////////////////////////////

# ~ 1 ~ 
# Apply Transformations
# At the moment, the only attributes that we are interested in are: primid,
# secid, and phenotype. In this section, these attributes will be renamed to
# align with the UMDM and some transformations will be applied.
# 

# ~ 1a ~
# rename columns
status_msg('Pulling columns of interest and renaming...')

benchcnv = benchcnvRaw[:,
    {
        'primid': f.primid,
        'belongsToFamily': f.secid,
        'observedPhenotype': f.phenotype
    }
]

# ~ 1b ~ 
# Identify cases to keep
# All records must have a valid ID (i.e., start with a number) and must contain
# at least one valid HPO code.
status_msg('Removing rows that do not have phenotype info or valid ID...')

benchcnv['keep'] = dt.Frame([
    (
        bool(re.search(r'^[0-9].*', str(d[0]).strip())) and
        bool(re.search(r'^(HP:)', d[1].strip()))
    )
    for d in benchcnv[:, (f.primid, f.observedPhenotype)].to_tuples()
])

status_msg('Rows before =', benchcnv.nrows)

# remove rows
benchcnv = benchcnv[f.keep, :][:, :, dt.sort(f.primid)]

status_msg('Rows after =', benchcnv.nrows)
del benchcnv['keep']


# ~ 1c ~
# Format HPO codes
status_msg('Cleaning phenotype column...')

benchcnv['observedPhenotype'] = dt.Frame([
    ','.join(list(set(d.strip().split())))
    for d in benchcnv['observedPhenotype'].to_list()[0]
])


# ~ 1D ~
# Detect if subjectID is a fetus
status_msg('Setting fetal status...')

benchcnv['isFetus'] = dt.Frame([
    'f' in d.lower()
    for d in benchcnv['primid'].to_list()[0]
])

# check for duplicate entries
if len(list(set(benchcnv['primid'].to_list()[0]))) != benchcnv.nrows:
    print(
        'Total number of distinct identifiers ({}) must match row numbers ({})'
        .format(
            len(list(set(benchcnv['primid'].to_list()[0]))),
            benchcnv.nrows
        )
    )


# ~ 1e ~
# Based on fetal status, compute other identifers
status_msg('Computing maternal-, subject-, and alternative identifiers...')
benchcnv = benchcnv.to_pandas().replace({np.nan: None}).to_dict('records')

for index,row in enumerate(benchcnv):
    value = row.get('primid').strip().replace(' ', '')
    if row['isFetus']:

        # Pattern 1: 99999F, 99999F1, 99999F1.2
        pattern1 = re.search(r'((F)|(F[-_])|(F[0-9]{,2})|(F[0-9]{1,2}.[0-9]{1,2}))$', value)
        
        # Patern 2: 99999F-88888, 99999_88888
        pattern2 = re.search(r'^([0-9]{1,}(F)?([0-9]{1,2})?[-_=][0-9]{1,})$', value)
        if pattern1:
            row['belongsToMother'] = pattern1.string.replace(pattern1.group(0),'')
            row['subjectID'] = pattern1.string
        elif pattern2:
            ids = re.split(r'[-_=]', pattern2.string)
            row['belongsToMother'] = ids[0].replace('F', '')
            row['subjectID'] = ids[0] #.replace('F', '')
            row['alternativeIdentifiers'] = ids[1]
        else:
            status_msg('{}. F detected in {}, but pattern is unexpected'.format(index, value))
    else:
        row['belongsToMother'] = None
        row['subjectID'] = row['primid']
        row['alternativeIdentifiers'] = None

#//////////////////////////////////////
#     
# ~ 2 ~
# Import into COSAS

# import prepped data
status_msg('Importing data...')
db.importData(entity = 'cosasportal_benchcnv_prepped', data = benchcnv)


# update identifiers in source table
status_msg('Updating portal status...')
importedIDs = [x['primid'] for x in benchcnv]
benchcnvRaw['processed'] = dt.Frame([
    d in importedIDs
    for d in benchcnvRaw['primid'].to_list()[0]
])

updateProcessed = benchcnvRaw[:,['id', 'processed']].to_pandas().to_dict('records')

db.updateColumn(
    entity = 'cosasportal_benchcnv',
    attr = 'processed',
    data = updateProcessed
)
