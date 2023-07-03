#///////////////////////////////////////////////////////////////////////////////
# FILE: alissa_get_analyses.py
# AUTHOR: David Ruvolo
# CREATED: 2023-06-08
# MODIFIED: 2023-07-03
# PURPOSE: retrieve patient analyses from Alissa Interpret
# STATUS: stable
# PACKAGES: **see below**
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from cosastools.molgenis import Molgenis, print2
from cosastools.alissa import Alissa
from datatable import dt, f, as_type
from datetime import datetime

def today():
  return datetime.today().strftime('%Y-%m-%d')

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
# Before analysis information can be retrieved, it is important to build of
# identifiers that need to be tested.

# get list of patients that do not have errors
print2('Pulling existing Alissa Patients....')
subjects = cosas.get('alissa_patients',q='hasError==false', batch_size=10000)

# flatten data
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

# define a list of identifiers
patientIdentifiers = subjectsDT['alissaInternalID'].to_list()[0]

# # get analyses
alissaAnalyses = dt.Frame(cosas.get('alissa_analyses',batch_size='10000'))
del alissaAnalyses['_href']

#///////////////////////////////////////////////////////////////////////////////

# ~ 2 ~
# Retreive analysis information
print2(f'Retrieving analyses for {len(patientIdentifiers)} patients...')

analysesByPatient = []
for id in patientIdentifiers:
  analysisResponse = alissa.getPatientAnalyses(patientId=id)
  if analysisResponse:
    for analysis in analysisResponse:
      if analysis.get('status') == 'COMPLETED':
        analysis['analysisId'] = analysis['id']
        del analysis['id']
        analysesByPatient.append(analysis)

print2(f"Retrieved {len(analysesByPatient)} analyses....")

#///////////////////////////////////////////////////////////////////////////////

# ~ 3 ~
# Transform data
print2('Transforming data....')

analysesDT = dt.Frame(analysesByPatient)

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

# create ID: `<patient-id>_<analysis-id>`
analysesDT['id'] = analysesDT[:, f.umcgNr + '_' + f.analysisId]

#///////////////////////////////////////

# flatten targetPanelNames
print2('Flattening target panel names....')

analysesDT['targetPanelNames'] = dt.Frame([
  ';'.join(value)
  for value in analysesDT['targetPanelNames'].to_list()[0]
])

analysesDT['targetPanelNames'] = dt.Frame([
  None if value == 'NONE' else value
  for value in analysesDT['targetPanelNames'].to_list()[0]
])

#///////////////////////////////////////

# determine if each analysis exists and set dates
print2('Updating date run and date updated....')

analysisIds = alissaAnalyses['analysisId'].to_list()[0] if alissaAnalyses else []

analysesDT[['dateFirstRun','dateLastUpdated', 'comments']] = dt.Frame([
  (row[1], today(), 'record updated or refreshed')
  if row[0] in analysisIds
  else (today(), None, None)
  for row in analysesDT[:, ['analysisId', 'dateFirstRun','dateLastUpdated']].to_tuples()
])

#///////////////////////////////////////

# update data types
print2('Updating data types....')

analysesDT[:, dt.update(
  patientId=as_type(f.patientId, dt.str32),
  analysisId=as_type(f.analysisId, dt.str32),
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
    
  existing = subjectsDT[f.umcgNr==id, 'analyses'].to_list()[0][0]
  if existing: ids.extend(existing.split(','))
    
  patientAnalysisIds = list(set(filter(lambda value: value != None, ids)))
  subjectsDT[f.umcgNr==id, 'analyses'] = ','.join(patientAnalysisIds)
  subjectsDT[f.umcgNr==id, 'dateLastUpdated'] = today()

#///////////////////////////////////////////////////////////////////////////////

# ~ 4 ~
# Import Data

print2('Importing datasets....')
cosas.importDatatableAsCsv(pkg_entity='alissa_analyses', data=analysesDT)
cosas.importDatatableAsCsv(pkg_entity='alissa_patients', data=subjectsDT)
cosas.logout()
