#//////////////////////////////////////////////////////////////////////////////
# FILE: alissa.py
# AUTHOR: David Ruvolo
# CREATED: 2022-04-19
# MODIFIED: 2023-07-03
# PURPOSE: fetch data from alissa
# STATUS: stable
# PACKAGES: **see below**
# COMMENTS: The purpose of this script is to extract variant information for
# all patients, or a subset of patients, from the UMCG instance of Alissa
# Interpret.
#//////////////////////////////////////////////////////////////////////////////

from cosastools.molgenis import Molgenis, print2
from cosastools.alissa import Alissa
from datatable import dt, f, as_type
import molgenis.client as molgenis
from datetime import datetime
import requests
import json
import re
  
def today():
  return datetime.today().strftime('%Y-%m-%d')

def cleanKeyName(value):
  val = re.sub(r'[()\+]', '', value)
  return re.sub(r'(\s+|[-/])', '_', val)

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
