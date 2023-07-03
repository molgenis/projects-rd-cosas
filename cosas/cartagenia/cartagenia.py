#'////////////////////////////////////////////////////////////////////////////
#' FILE: cartagenia_query.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-03-23
#' MODIFIED: 2023-01-30
#' PURPOSE: run query for cartagenia data
#' STATUS: stable
#' PACKAGES: **see below**
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

import molgenis.client as molgenis
from datatable import dt, f
from os.path import abspath
import numpy as np
import datetime
import requests
import tempfile
import pytz
import csv
import re

def now():
  return datetime.datetime.now(tz=pytz.timezone('Europe/Amsterdam')).strftime('%H:%M:%S.%f')[:-3]

def print2(*args):
  """Status Message
  Print a log-style message, e.g., "[16:50:12.245] Hello world!"
  @param *args one or more strings containing a message to print
  @return string
  """
  message = ' '.join(map(str, args))
  print(f'[{now()}] {message}')

class Molgenis(molgenis.Session):
  def __init__(self, *args, **kwargs):
    super(Molgenis, self).__init__(*args, **kwargs)
    self.fileImportEndpoint = f"{self._root_url}plugin/importwizard/importFile"
  
  def _datatableToCsv(self, path, datatable):
    """To CSV
    Write datatable object as CSV file

    @param path location to save the file
    @param data datatable object
    """
    data = datatable.to_pandas().replace({np.nan: None})
    data.to_csv(path, index=False, quoting=csv.QUOTE_ALL)
  
  def importDatatableAsCsv(self, pkg_entity: str, data):
    """Import Datatable As CSV
    Save a datatable object to as csv file and import into MOLGENIS using the
    importFile api.
    
    @param pkg_entity table identifier in emx format: package_entity
    @param data a datatable object
    @param label a description to print (e.g., table name)
    """
    with tempfile.TemporaryDirectory() as tmpdir:
      filepath=f"{tmpdir}/{pkg_entity}.csv"
      self._datatableToCsv(filepath, data)
      with open(abspath(filepath),'r') as file:
        response = self._session.post(
          url = self.fileImportEndpoint,
          headers = self._headers.token_header,
          files = {'file': file},
          params = {'action': 'add_update_existing', 'metadataAction': 'ignore'}
        )
        if (response.status_code // 100 ) != 2:
          print2('Failed to import data into', pkg_entity, '(', response.status_code, ')')
        else:
          print2('Imported data into', pkg_entity)
        return response

class Cartagenia:
  """Cartagenia Client"""
  def __init__(self, url, token):
    self.session = requests.Session()
    self._api_url = url
    self._api_token = token 
    self._headers = {'x-api-key': self._api_token}

  def getData(self):
    response = self.session.get(url=self._api_url, headers=self._headers)
    response.raise_for_status()
    data = response.json()
    if 'Output' not in data:
      raise KeyError('Expected object "Output" not found')
    return list(eval(data['Output']))

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
  
  # @returns tuple: (<subjectID>, <belongsToMother>, <alternativeIdentifier)
  # for testA, <alternativeIdentifier> will always be None
  # for testB, you may want to run: values[0].replace('F', '')
  if testA:
    return (testA.string, testA.string.split('F')[0], None)
  elif testB:
    values = re.split(r'[-_=]', testB.string)
    return (values[0], values[0].split('F')[0], values[1])
  else:
    return None

#//////////////////////////////////////////////////////////////////////////////

# ~ 0 ~
# init db connections

# ~ For Deployment ~
cosas = Molgenis(url='http://localhost/api/', token = '${molgenisToken}')
apiUrl = cosas.get('sys_sec_Token',attributes='token',q='description=="cartagenia-api-url"')[0]['token']
apiToken = cosas.get('sys_sec_Token',attributes='token',q='description=="cartagenia-api-token"')[0]['token']
cartagenia = Cartagenia(url = apiUrl, token = apiToken)

# ~ for local development ~
# After connecting to the database, run the apiUrl and apiToken lines
# from dotenv import load_dotenv
# from os import environ
# load_dotenv()
# cosas = Molgenis(url=environ['MOLGENIS_ACC_HOST'])
# cosas.login(environ['MOLGENIS_ACC_USR'], environ['MOLGENIS_ACC_PWD'])
# cartagenia = Cartagenia(apiUrl, apiToken)


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
print2('Querying Cartagenia endpoint....')
rawData = cartagenia.getData()

# ~ 1b ~
# Query the Cartagenia endpoint and extract results
# 
# For the time being, keep all columns in case we need these later. Columns of
# interest are selected in the next step. Convert to datatable.Frame for faster
# data transformatons. The headers were defined by the original Cartagenia
# file. The structure did not change when the export was moved to a private
# endpoint.
print2('Processing raw data....')

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
print2('Applying inclusion criteria....')
rawBenchCnv['keep'] = dt.Frame([
  (
    bool(re.search(r'^[0-9].*', str(tuple[0]).strip())) and
    bool(re.search(r'^(HP:)', tuple[1].strip()))
  )
  if (tuple[0] is not None) and (tuple[1] is not None) else False
  for tuple in rawBenchCnv[:, (f.primid, f.phenotype)].to_tuples()
])

benchcnv = rawBenchCnv[f.keep, :][
  :, (f.primid, f.secid, f.phenotype), dt.sort(f.primid)
]

# ~ 1d ~
# Transform columns
print2('Formatting columns....')

# format IDs: trim, remove white space, and make sure string is uppercased
benchcnv['primid'] = dt.Frame([
  d.strip().replace(' ','').upper()
  for d in benchcnv['primid'].to_list()[0]
])

# Format HPO terms: split, trim, and get unique values
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
  extractIdsFromValue(row[0].strip())
  if row[1] else (row[0],None,None)
  for row in benchcnv[:, (f.primid, f.isFetus)].to_tuples()
])

# check for duplicate entries
if dt.unique(benchcnv['primid']).nrows != benchcnv.nrows:
  raise SystemError(
    'Total number of distinct identifiers ({}) must match row numbers ({})'
    .format(dt.unique(benchcnv['primid']).nrows, benchcnv.nrows)
  )

# ~ 1e ~
# Convert data to record set
benchcnv.names = {
  'primid': 'id',
  'secid': 'belongsToFamily',
  'phenotype': 'observedPhenotype'
}

# ~ 1f ~
# Import data
print2('Imporing data into cosasportal...')
cosas.importDatatableAsCsv(pkg_entity="cosasportal_cartagenia", data=benchcnv)
