#///////////////////////////////////////////////////////////////////////////////
# FILE: alissa_get_inheritance.py
# AUTHOR: David Ruvolo
# CREATED: 2023-06-08
# MODIFIED: 2023-06-09
# PURPOSE: retrieve inheritance metadata where applicable
# STATUS: stable
# PACKAGES: **see below**
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
from datatable import dt, f, as_type
import molgenis.client as molgenis
from datetime import datetime
from os.path import abspath
import numpy as np
import tempfile
import json
import pytz
import csv

def now():
  return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  
def today():
  return datetime.today().strftime('%Y-%m-%d')

def print2(*args):
  message = ' '.join(map(str, args))
  time = datetime.now(tz=pytz.timezone('Europe/Amsterdam')).strftime('%H:%M:%S.%f')[:-3]
  print(f'[{time}] {message}')
  
class Alissa:
  """Alissa Interpret Public API (v5.3)"""
  
  def __init__(self, host, clientId, clientSecret, username, password):
    """Create new instance of the client
    A mini api client to get molecular variant information per patient.

    @param host The url of your Alissa Interpret instance
    @param clientId provided by Alissa Support
    @param clientSecret provided by Alissa Support
    @param username username of the API account
    @param password password of the API account
    
    @reference Alissa Interpret Public API documentation v5.3
    @return class
    """
    self.host=host
    self.apiUrl=f"{host}/interpret/api/2"
    self.session=OAuth2Session(client=LegacyApplicationClient(client_id=clientId))
    self.session.fetch_token(
      token_url=f"{host}/auth/oauth/token",
      username=username,
      password=password,
      client_id=clientId,
      client_secret=clientSecret
    )

    if self.session.access_token:
      print('Connected to', host, 'as', username)
    else:
      print('Unable to connect to', host, 'as', username)
      

  def _formatOptionalParams(self, params: dict=None) -> dict:
    """Format Optional Parameters
    
    @param params dictionary containg one or more parameter
    @return dict
    """
    return {
      key: params[key]
      for key in params.keys()
      if (key != 'self') and (params[key] is not None)
    }
  
  def _get(self, endpoint, params=None, **kwargs):
    """GET

    @param endpoint the Alissa Interpret endpoint where data should be
        sent to. The path "/interpret/api/2" is prefilled.
    @param params Optional parameters to add to the request

    """
    uri = f'{self.apiUrl}/{endpoint}'
    response = self.session.get(uri, params=params, **kwargs)
    response.raise_for_status()
    return response.json()
  
  def getInheritanceAnalysis(self, analysisId: int=None) -> dict:
    """Get Interhitance Analysis
    Get the inheritance analysis of a patient for a specific analysis.
    
    @param analysisId The unique internal identifier of an analysis
    
    @reference Alissa Interpret Public API (v5.3; p89-90)
    @return dictionary
    """
    return self._get(endpoint=f"inheritance_analyses/{analysisId}")

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

def filterList(data, key, condition):
  return [row for row in data if row[key] == condition][0]

#///////////////////////////////////////////////////////////////////////////////

# ~ 0 ~
# Connect to Alissa and MOLGENIS
print2('Connecting to Alissa and MOLGENIS....')

# ~ DEV ~
# for local dev
# from dotenv import load_dotenv
# load_dotenv()
# from os import environ
# cosas = Molgenis(environ['MOLGENIS_ACC_HOST'])
# cosas.login(environ['MOLGENIS_ACC_USR'], environ['MOLGENIS_ACC_PWD'])
# alissa = Alissa(
#   host=environ['ALISSA_HOST'],
#   clientId=environ['ALISSA_CLIENT_ID'],
#   clientSecret=environ['ALISSA_CLIENT_SECRET'],
#   username=environ['ALISSA_API_USR'],
#   password=environ['ALISSA_API_PWD']
# )

#///////////////////////////////////////

# ~ DEPLOY ~
# for deployment

cosas = Molgenis('http://localhost/api/', token='${molgenisToken}')
credentials = cosas.get(
  'sys_sec_Token',
  q='description=like="alissa-api-"',
  attributes='token,description'
)

host=filterList(credentials,'description','alissa-api-host')['token']
clientId=filterList(credentials,'description','alissa-api-client-id')['token']
clientSecret=filterList(credentials,'description', 'alissa-api-client-secret')['token']
apiUser=filterList(credentials,'description','alissa-api-username')['token']
apiPwd=filterList(credentials,'description','alissa-api-password')['token']

alissa = Alissa(
  host=host,
  clientId=clientId,
  clientSecret=clientSecret,
  username=apiUser,
  password=apiPwd
)

#///////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Retrieve Metadata
# Before analysis information can be retrieved, build a list of IDs to query.
# In the previous script, we've retrieved information on which analyses are listed
# as "inheritance". This allows us to query the inheritance analysis endpoint
# directly.

# get alissa analysis metadata
alissaAnalysesDT = dt.Frame(
  cosas.get(
    entity = 'alissa_analyses',
    q='analysisType=="INHERITANCE"',
    batch_size=10000,
  )
)

# get existing inheritance data
alissaInheritanceDT = dt.Frame(
  cosas.get(
    entity = 'alissa_inheritance',
    batch_size=10000
  )
)

# get subject metadata
subjects = cosas.get('alissa_patients',batch_size=10000)
for row in subjects:
  for column in ['analyses', 'inheritanceAnalyses', 'variants']:
    if row.get(column):
      row[column] = ','.join([subrow['id'] for subrow in row[column]])
    else:
      row[column] = None

subjectsDT = dt.Frame(subjects)
subjectsDT[:, dt.update(
  analyses = as_type(f.analyses, dt.str32),
  inheritanceAnalyses = as_type(f.inheritanceAnalyses, dt.str32),
  variants = as_type(f.variants, dt.str32)
)]
del subjectsDT['_href']

#///////////////////////////////////////////////////////////////////////////////

# ~ 2 ~
# Retrieve inheritance analysis metadata

analysisIDs = alissaAnalysesDT['analysisId'].to_list()[0]

print2(f"Querying for {len(analysisIDs)} inheritance analyses....")

analyses = []
for id in analysisIDs:
  response = alissa.getInheritanceAnalysis(analysisId=id)
  if response:
    if response.get('status') == 'COMPLETED':
      analyses.extend([response])
  
print2(f"Retrieved metadata for {len(analyses)} inheritance analyses...")

#///////////////////////////////////////////////////////////////////////////////

# ~ 3 ~
# Transform data
print2('Flattening nested data and expanding family members....')

analysesData = analyses.copy()
for row in analysesData: 
  
  # flatten target panel names
  if row.get('targetPanelNames'):
    row['targetPanelNames'] = ','.join([
      value for value in row['targetPanelNames'] if value != 'NONE'
    ])
   
  # save lab results as json format
  if row.get('labResults'):
    row['labResults'] = json.dumps(row['labResults'])
    
  # expand family members
  row['maternalPatientId'] = None
  row['paternalPatientId'] = None
  row['maternalAffectedStatus'] = None
  row['paternalAffectedStatus'] = None
  if 'familyMembers' in row:
    for person in row['familyMembers']:
      if person['relationType'] == 'MOTHER':
        row['maternalPatientId'] = person['patientId']
        row['maternalAffectedStatus'] = person['affected']
        
      if person['relationType'] == 'FATHER':
        row['paternalPatientId'] = person['patientId']
        row['paternalAffectedStatus'] = person['affected']
  row['familyMembers'] = None

# convert to datatable 
analysesDT = dt.Frame(analysesData)
del analysesDT['familyMembers']

# init columns in not present
for column in ['dateFirstRun', 'dateLastUpdated','comments']:
  if column not in analysesDT.names:
    analysesDT[column] = None

#///////////////////////////////////////

# add umcgNr
print2('Merging umcgNr and generating table identifiers....')

analysesDT['umcgNr'] = dt.Frame([
  subjectsDT[f.alissaInternalID==str(value), 'umcgNr'].to_list()[0][0]
  if value else value
  for value in analysesDT['patientId'].to_list()[0]
])

# init analyisId (i.e., copy ID)
analysesDT['analysisId'] = analysesDT[:, f.id]

# create ID: `<patient-id>_<analysis-id>`
analysesDT['id'] = analysesDT[:, f.umcgNr + '_' + f.analysisId]


print2('Updating data types....')
analysesDT[:, dt.update(
  patientId=as_type(f.patientId, dt.str32),
  analysisId=as_type(f.analysisId, dt.str32),
  maternalPatientId=as_type(f.maternalPatientId, dt.str32),
  paternalPatientId=as_type(f.paternalPatientId, dt.str32),
  dateFirstRun=as_type(f.dateFirstRun, dt.str32),
  dateLastUpdated=as_type(f.dateLastUpdated, dt.str32),
  comments=as_type(f.comments, dt.str32),
)]

#///////////////////////////////////////

# determine if each analysis exists and set dates
print2('Updating date run and date updated....')

analysisIds = alissaInheritanceDT['analysisId'].to_list()[0] if alissaInheritanceDT.nrows else []

analysesDT[['dateFirstRun','dateLastUpdated', 'comments']] = dt.Frame([
  (row[1], today(), 'record was refreshed')
  if row[0] in analysisIds else (today(), None, None)
  for row in analysesDT[:, ['analysisId', 'dateFirstRun','dateLastUpdated']].to_tuples()
])

# make sure columns remain string (will get overwritten if all are none)
analysesDT[:, dt.update(
  dateFirstRun=as_type(f.dateFirstRun, dt.str32),
  dateLastUpdated=as_type(f.dateLastUpdated, dt.str32),
  comments=as_type(f.comments, dt.str32),
)]

#///////////////////////////////////////

# update analyses references in patients
print2('Updating analysis table references in alissa_patients....')

analysesPatients = analysesDT['umcgNr'].to_list()[0]
for id in analysesPatients:
  ids = []
  
  current = analysesDT[f.umcgNr==id, 'id'].to_list()[0]
  if current: ids.extend(current)
    
  existing = subjectsDT[f.umcgNr==id, 'inheritanceAnalyses'].to_list()[0][0]
  if existing: ids.extend(existing.split(','))
    
  patientAnalysisIds = list(set(filter(lambda value: value != None, ids)))
  subjectsDT[f.umcgNr==id, 'inheritanceAnalyses'] = ','.join(patientAnalysisIds)
  subjectsDT[f.umcgNr==id, 'dateLastUpdated'] = today()

#///////////////////////////////////////////////////////////////////////////////

# ~ 4 ~
# Import Data
print2('Importing data....')
cosas.importDatatableAsCsv(pkg_entity='alissa_inheritance',data=analysesDT)
cosas.importDatatableAsCsv(pkg_entity='alissa_patients',data=subjectsDT)
cosas.logout()
