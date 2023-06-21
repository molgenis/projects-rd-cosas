#//////////////////////////////////////////////////////////////////////////////
# FILE: alissa.py
# AUTHOR: David Ruvolo
# CREATED: 2022-04-19
# MODIFIED: 2023-06-21
# PURPOSE: fetch data from alissa
# STATUS: stable
# PACKAGES: **see below**
# COMMENTS: The purpose of this script is to extract variant information for
# all patients, or a subset of patients, from the UMCG instance of Alissa
# Interpret.
#//////////////////////////////////////////////////////////////////////////////

from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
from datatable import dt, f, as_type
import molgenis.client as molgenis
from datetime import datetime
from os.path import abspath
import numpy as np
import requests
import tempfile
import json
import pytz
import csv
import re

def now():
  return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  
def today():
  return datetime.today().strftime('%Y-%m-%d')

def print2(*args):
  message = ' '.join(map(str, args))
  time = datetime.now(tz=pytz.timezone('Europe/Amsterdam')).strftime('%H:%M:%S.%f')[:-3]
  print(f'[{time}] {message}')
  
def cleanKeyName(value):
  val = re.sub(r'[()\+]', '', value)
  return re.sub(r'(\s+|[-/])', '_', val)

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
      print2('Connected to',host,'as',username)
    else:
      print2('Unable to connect to',host,'as',username)
      

  def _formatOptionalParams(self, params: dict=None) -> dict:
    """Format Optional Parameters
    @param params dictionary containg one or more parameter
    @return dict
    """
    return {
      key: params[key] for key in params.keys() if (key != 'self') and (params[key] is not None)
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
      
  def _post(self, endpoint, data=None, json=None, **kwargs):
    """POST
    @param endpoint the Alissa Interpret endpoint where data should be
      sent to. The path "/interpret/api/2" is prefilled.
    @param data Optional dictionary, list of tuples, bytes, or file-like object
    @param json Optional json data
    """
    uri = f'{self.apiUrl}/{endpoint}'
    response = self.session.post(uri, data, json, **kwargs)
    response.raise_for_status()
    return response.json()

  def getPatientVariantExportId(
    self,
    analysisId: int,
    markedForReview: bool=True,
    markedIncludeInReport: bool=True
  ) -> dict:
    """Request Patient Molecular Variants Export
    Request an export of all variants. When filter criteria are provided,
    the result is limited to the variants matching the criteria. By default
    the parameters `markedForReview` and `markedIncludeInReport` are set to
    True. This will return all results that have been selected.

    @param analysisId ID of the analysis
    @param markedForReview Is the variant marked for review
    @param markedIncludeInReport Is the variant included in the report

    @reference Alissa Interpret Public API (v5.3; p44)
    @param dictionary containing the export identifier
    """
    data={'markedForReview': markedForReview, 'markedIncludeInReport': markedIncludeInReport}
    api=f"patient_analyses/{analysisId}/molecular_variants/exports"
    return self._post(endpoint=api,json=data)

  def getPatientVariantExportData(self, analysisId: int, exportId: str) -> dict:
    """Get Patient Molecular Variants Export
    Get the exported variants of a patient analysis via the export ID
    returned when requesting the export.

    @param analysisId The unique internal identifier of an analysis
    @param exportId The unique internal identifier of the export

    @reference Alissa Interpret Public API (v5.3; p45)
    @return dictionary containing the molecular variant export data from a
        single analysis of one patient
    """
    api=f"patient_analyses/{analysisId}/molecular_variants/exports/{exportId}"
    return self._get(endpoint=api)

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
# Connect to the UMCG instance of Alissa Interpret
print2('Establishing connections to COSAS and Alissa....')

# ~ LOCAL DEV ~
# For local molgenis development
# Connect to COSAS database
# from dotenv import load_dotenv
# from os import environ
# load_dotenv()
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

# ~ PROD ~
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
# Retrieve metadata

# ~ 1a ~
# Get existing patient metadata
print2('Pulling reference data for Alissa patients....')
alissaPatients = cosas.get(
  entity='alissa_patients',
  q="hasError==false",
  batch_size=10000
)

for row in alissaPatients:
  for column in ['analyses', 'inheritanceAnalyses', 'variants']:
    if row.get(column):
      row[column] = ','.join([record['id'] for record in row[column]])
    else:
      row[column] = None

alissaPatientsDT = dt.Frame(alissaPatients)
del alissaPatientsDT['_href']

patientIDs = alissaPatientsDT['alissaInternalID'].to_list()[0]

# ~ 1b ~
# Get existing analysis metadata to retrieve variant metadata
analysesByPatient = cosas.get('alissa_analyses',batch_size=10000)
analysisDT = dt.Frame(analysesByPatient)
analysisIDs = analysisDT['analysisId'].to_list()[0]

del analysisDT['_href']

# ~ 1c ~
# Get existing variant exports
alissaVariantsDT = dt.Frame(
  cosas.get(
    entity = 'alissa_variantexports',
    batch_size=10000
  )
)

if alissaVariantsDT.nrows:
  del alissaVariantsDT['_href']

# ~ 1d ~
# Get column names of the variant export table
variantTableColumns = dt.Frame(
  cosas.get(
    entity='sys_md_Attribute',
    q="entity==alissa_variantexports",
    sort_column='sequenceNr',
    attributes='name'
  )
)['name'].to_list()[0]

#///////////////////////////////////////////////////////////////////////////////
            
# ~ 2 ~
# GET VARIANT EXPORT IDs
#
# Using the patient-analysis identifier, get all variant export identifiers.
# This step will create an object where each row is one patient, analysis, and
# variant export (long format).
#
# NOTE: The reason for the try-except is that a patient may have a valid analysis
# identifier but not records at the variant export endpoint. If this is the
# case, the server throws a 404 error.
print2('Alissa: geting variant-export-ids.....')

variantExportsByAnalyses = []
for row in analysesByPatient:
  try:
    variantResponse = alissa.getPatientVariantExportId(
      analysisId=row['analysisId'],
      markedForReview=True,
      markedIncludeInReport=False
    )
    if variantResponse:
      if isinstance(variantResponse, dict):
        variantResponse['patientId'] = row['patientId']
        variantResponse['analysisId'] = row['analysisId']
        variantExportsByAnalyses.append(variantResponse)

      if isinstance(variantResponse, list):
        for record in variantResponse:
          record['patientId'] = row['patientId']
          record['analysisId'] = row['analysisId']
          variantExportsByAnalyses.append(record)

  except requests.exceptions.HTTPError as error:
    pass

print2('Returned',len(variantExportsByAnalyses),'export identifiers')

#///////////////////////////////////////

# ~ 2b ~
# GET VARIANT EXPORT REPORTS
# Now that a list of variant export reports has been compiled, it is possible
# to retrieve the variant export report for the patient and analysis.
print2('Alissa: retrieving variant-exports....')

variantExport = []
for variantRow in variantExportsByAnalyses:
  try:
    exportResponse = alissa.getPatientVariantExportData(
      analysisId=variantRow['analysisId'],
      exportId=variantRow['exportId']
    )
    if exportResponse:
      if isinstance(exportResponse, dict):
        exportResponse['patientId'] = variantRow['patientId']
        exportResponse['analysisId'] = variantRow['analysisId']
        exportResponse['variantExportId'] = variantRow['exportId']
        variantExport.append(exportResponse)

      if isinstance(exportResponse, list):
        for export in exportResponse:
          export['patientId'] = variantRow['patientId']
          export['analysisId'] = variantRow['analysisId']
          export['variantExportId'] = variantRow['exportId']
          variantExport.append(export)

  except requests.exceptions.HTTPError as error:
    pass

print2('Returned metadata for',len(variantExport),'reports')

#///////////////////////////////////////////////////////////////////////////////

# ~ 3 ~
# PROCESS VARIANT EXPORT DATA
# NOTE: Many of the columns are removed in the following step. However,
# it is important to keep this here in case it is decided to add this information
# in the future.
print2('Processing variant export data....')

variantdata = []

for row in variantExport:
  if 'errorCode' not in row.keys():
    newRow = dict(row)
    
    if bool(newRow['variantAssessment']):
      newRow['variantAssessment'] = json.dumps(newRow['variantAssessment'])
    
    if not bool(newRow['variantAssessmentLabels']):
      newRow['variantAssessmentLabels'] = None
    
    if not bool(newRow['variantAssessmentNotes']):
      newRow['variantAssessmentNotes'] = None
      
    if bool(newRow.get('geneProfileReport')):
      newRow['geneProfileReport'] = json.dumps(newRow['geneProfileReport'])
    
    # flatten databaseReferences
    if 'databaseReferences' in newRow:
      if bool(newRow['databaseReferences']):
        for key in newRow['databaseReferences'].keys():
          if bool(newRow['databaseReferences'][key]):
            newRow[f'databaseReferences_{key}'] = newRow['databaseReferences'][key]
          else:
            newRow[f'databaseReferences_{key}'] = None
        del newRow['databaseReferences']
    
    # flatten classification tree labels
    if 'classificationTreeLabelsScore' in newRow:
      if bool(newRow['classificationTreeLabelsScore']):
        newRow['classificationTreeLabels'] = json.dumps(
          newRow['classificationTreeLabelsScore']['labels']
        )
        newRow['classificationTreeScores'] = newRow['classificationTreeLabelsScore']['score']
        del newRow['classificationTreeLabelsScore']
      
    # for now, convert customfields to a json stringified object
    if 'customFields' in newRow:
      if bool(newRow['customFields']):
        newRow['customFields'] = json.dumps(newRow['customFields'])
      else:
        newRow['customFields'] = None
    
    # flatten externalDatabases
    if 'externalDatabases' in newRow:
      if bool(newRow['externalDatabases']):
        for key in newRow['externalDatabases'].keys():
          newKey = cleanKeyName(key)
          if bool(newRow['externalDatabases'][key]):
            newRow[f'_{newKey}'] = json.dumps(newRow['externalDatabases'][key])
          else:
            newRow[f'_{newKey}'] = None
        del newRow['externalDatabases']
    
    # flatten platformDatasets
    if 'platformDatasets' in newRow:
      if bool(newRow['platformDatasets']):
        for key in newRow['platformDatasets'].keys():
          newKey = cleanKeyName(key)
          if bool(newRow['platformDatasets'][key]):
            newRow[f'_{newKey}'] = json.dumps(newRow['platformDatasets'][key])
          else:
            newRow[f'_{newKey}'] = None
        del newRow['platformDatasets']
  
    for column in newRow.keys():
      if bool(newRow[column]) and type(newRow[column]) == str:
        newRow[column] = newRow[column].replace(',',';')

    variantdata.append(newRow)

#///////////////////////////////////////////////////////////////////////////////

# ~ 6 ~ 
# Merge datasets
print2('Building datasets....')

# convert to datatable object
variantsDT = dt.Frame(variantdata)

# First, select cases that are necessary
# We are only in cases where that have a specific classification or where the
# classification is missing (to investigate this further)
variantsDT['mustKeep'] = dt.Frame([
  (not bool(value)) or (value in ['','Likely pathogenic', 'Pathogenic', 'VOUS'])
  for value in variantsDT['classification'].to_list()[0]
])

variantsDT = variantsDT[f.mustKeep, :]
del variantsDT['mustKeep']

# set classes
variantsDT[:, dt.update(
  patientId=as_type(f.patientId, str),
  analysisId=as_type(f.analysisId, str),
)]

# clean columns
for column in variantsDT.names:
  if variantsDT[column].type == dt.Type.str32:
    variantsDT[column] = dt.Frame([
      re.sub(r'([-]{1,}\s+)|(\<br\>)|([\\"])', '', value) if value else value
      for value in variantsDT[column].to_list()[0]
    ])

#///////////////////////////////////////

# ~ 6a ~
# merge patient info
print2('Merging patient data with variants....')
variantsDT[['umcgNr', 'accessionNumber']] = dt.Frame([
  alissaPatientsDT[
    f.alissaInternalID==id, (f.umcgNr,f.accessionNr)
  ].to_tuples()[0]
  for id in variantsDT['patientId'].to_list()[0]
])

#///////////////////////////////////////

# ~ 6b ~
# merge analysis info
print2('Merging analaysis data with variants....')
variantsDT[[
  'analysisReference', 'status', 'targetPanelNames','genomeBuild'
]] = dt.Frame([
  analysisDT[
    f.analysisId==id, (f.reference,f.status,f.targetPanelNames,f.genomeBuild)
  ].to_tuples()[0]
  for id in variantsDT['analysisId'].to_list()[0]
])
  
# set row identifier
print2('Creating row identifier...')
variantsDT['id'] = dt.Frame([
  f"{row[0]}_{row[1]}_{row[2].split('.')[0]}_{row[3]}_{row[4]}" if all(row) else None
  for row in variantsDT[:, (f.umcgNr,f.start,f.transcript,f.reference,f.analysisId)].to_tuples()
])

#///////////////////////////////////////

# drop rows where an ID could not be generated
variantsDT = variantsDT[f.id != None,:]

# select columns of interest
for column in variantsDT.names:
  if column not in variantTableColumns:
    del variantsDT[column]

#///////////////////////////////////////

# update API dates
# init columns in not present
for column in ['dateFirstRun', 'dateLastUpdated']:
  if column not in variantsDT.names:
    variantsDT[column] = None

variantsDT[:, dt.update(
  dateFirstRun=as_type(f.dateFirstRun, dt.str32),
  dateLastUpdated=as_type(f.dateLastUpdated, dt.str32)
)]

alissaVariantsIDs = alissaVariantsDT['id'].to_list()[0] if alissaVariantsDT else []
variantsDT[['dateFirstRun','dateLastUpdated']] = dt.Frame([
  (row[1], today())
  if row[0] in alissaVariantsIDs
  else (today(), None)
  for row in variantsDT[:, ['id', 'dateFirstRun','dateLastUpdated']].to_tuples()
])

variantsDT[:, dt.update(
  dateFirstRun=as_type(f.dateFirstRun, dt.str32),
  dateLastUpdated=as_type(f.dateLastUpdated, dt.str32)
)]

#///////////////////////////////////////////////////////////////////////////////

# ~ 7 ~
# Import data
print2('Importing data patient and variants data....')
cosas.importDatatableAsCsv(pkg_entity='alissa_variantexports', data=variantsDT)
cosas.logout()
