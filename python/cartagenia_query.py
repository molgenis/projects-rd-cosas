#'////////////////////////////////////////////////////////////////////////////
#' FILE: cartagenia_query.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-03-23
#' MODIFIED: 2022-03-23
#' PURPOSE: run query for cartagenia data
#' STATUS: in.progress
#' PACKAGES: **see below**
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

from datatable import dt, f, as_type, first
import numpy as np
import datetime
import requests
import re

# only for local dev
from dotenv import load_dotenv
from os import environ
load_dotenv()
apiUrl = environ['CNV_API_HOST']
apiToken = environ['CNV_API_TOKEN']


class Cartagenia:
    """Cartagenia Client"""
    def __init__(self, url, token):
        self.session = requests.Session()
        self._api_url = url
        self._api_token = token
    
    def getData(self):
        try:
            print('Sending request....')
            response = self.session.get(
                url = self._api_url,
                headers = {'x-api-key': self._api_token}
            )
            
            response.raise_for_status()
            
            print('Preparing data...')
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

# ~ 1 ~
# Build Phenotype Dataset
#
# Pull the latest dataset from Cartagenia, process the data, and import into
# the portal table cosasportal_cartagenia. Data will be used in the main data
# processing script ('cosas_mappings.py').


# query the Cartagenia endpoint (i.e., lambda function for UMCG data)
cg = Cartagenia(url = apiUrl, token = apiToken)
rawData = cg.getData()


# ~ 1a ~
# Query the Cartagenia endpoint and extract results
# 
# For the time being, keep all columns in case we need these later. Columns of
# interest are selected in the next step.
#
rawBenchCnv = dt.Frame()
for entity in rawData:
    row = list(entity)
    rawBenchCnv = dt.rbind(
        rawBenchCnv,
        dt.Frame([
            {
                'primid': row[0],
                'secid': row[1],
                'externalid': row[2],
                'gender': row[3],
                'comment': row[4],
                'phenotype': row[5],
                'created': row[6]
            }]
        )
    )


# Identify cases to keep
# Inclusion criteria for a record is that each record must have...
#   1) a valid ID, e.g., 1*
#   2) one or more valid HPO code, e.g., HP:*

rawBenchCnv['keep'] = dt.Frame([
    (
        bool(re.search(r'^[0-9].*', str(d[0]).strip())) and
        bool(re.search(r'^(HP:)', d[1].strip()))
    )
    if (d[0] is not None) and (d[1] is not None) else False
    for d in rawBenchCnv[:, (f.primid, f.phenotype)].to_tuples()
])

# remove rows and columns
benchcnv = rawBenchCnv[f.keep, :][:, (f.primid, f.phenotype), dt.sort(f.primid)]


# clean IDs: remove white space
benchcnv['primid'] = dt.Frame([
    d.strip().replace(' ','')
    for d in benchcnv['primid'].to_list()[0]
])


# Format HPO terms
benchcnv['phenotype'] = dt.Frame([
    ','.join(list(set(d.strip().split())))
    for d in benchcnv['phenotype'].to_list()[0]
])


# determine fetus status
benchcnv['isFetus'] = dt.Frame([
    True if re.search(r'^[0-9]{1,}(F|f)', d) else False
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


# extract 
benchcnv[['subjectID','belongsToMother','alternativeIdentifiers']] = dt.Frame([
    extractIdsFromValue(d[0].strip())
    if d[1] else (None,None,None)
    for d in benchcnv[:, (f.primid, f.isFetus)].to_tuples()
])

# rename columns
benchcnv.names = {'primid': 'id', 'phenotype': 'observedPhenotype'}

# select columns
benchCnvPrepped = benchcnv.to_pandas().replace({np.nan: None}).to_dict('records')