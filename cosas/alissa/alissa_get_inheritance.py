#///////////////////////////////////////////////////////////////////////////////
# FILE: alissa_get_inheritance.py
# AUTHOR: David Ruvolo
# CREATED: 2023-06-08
# MODIFIED: 2023-07-03
# PURPOSE: retrieve inheritance metadata where applicable
# STATUS: stable
# PACKAGES: **see below**
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from cosastools.molgenis import Molgenis, print2
from cosastools.alissa import Alissa
from datatable import dt, f, as_type
from datetime import datetime
import json

def today():
  return datetime.today().strftime('%Y-%m-%d')

def filterList(data, key, condition):
  return [row for row in data if row[key] == condition][0]

#///////////////////////////////////////////////////////////////////////////////

# ~ 0 ~
# Connect to Alissa and MOLGENIS
print2('Connecting to Alissa and MOLGENIS....')

# ~ DEV ~
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
