#///////////////////////////////////////////////////////////////////////////////
# FILE: variantdb_alissa_prep.py
# AUTHOR: David Ruvolo
# CREATED: 2023-01-26
# MODIFIED: 2023-07-03
# PURPOSE: compile a list of information necessary for querying the alissa API
# STATUS: stable
# PACKAGES: **see below**
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from cosastools.molgenis import Molgenis, print2
from cosastools.alissa import Alissa
from datatable import dt, f, as_type
from datetime import datetime
import requests
import sys

def filterList(data, key, condition):
  return [row for row in data if row[key] == condition][0]

#///////////////////////////////////////////////////////////////////////////////

# ~ 0 ~
# Connect to Alissa and MOLGENIS

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
print2('Connecting to APIs....')

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
# Pull Information from the Portal

# ~ 1a ~
# Pull Patients from the portal
# In order to retrieve data from Alissa, we need to create the identifiers that
# we can use to retrieve data via the API. Using the information stored in
# `cosasportal_labs_ngs_adlas`, we can create a list of patients and samples to
# use in the Alissa search.
print2('Retrieving the latest patientIDs from ADLAS-NGS datasets....')
subjectsDT = dt.Frame(
  cosas.get(
    entity='cosasportal_labs_ngs_adlas',
    attributes='UMCG_NUMBER',
    batch_size=10000
  )
)[:, dt.first(f[:]), dt.by(f.UMCG_NUMBER)]['UMCG_NUMBER']


# ~ 1b ~
# Retrieve family information
# pull patient info from patients portal table (i.e., `cosasportal_patients`)
# For the API, we need the familyID. We will merge the samples data with the
# family information. First, pull the data and select distinct rows only
print2('Retrieving latest family information.....')

familyInfoDT = dt.Frame(
  cosas.get(
    entity='cosasportal_patients',
    attributes='UMCG_NUMBER,FAMILIENUMMER',
    batch_size=10000
  )
)[
  f.UMCG_NUMBER != None, (f.UMCG_NUMBER, f.FAMILIENUMMER)
][
  :,dt.first(f[:]), dt.by(f.UMCG_NUMBER)
]

# join familyID with samples
subjectsDT.key = 'UMCG_NUMBER'
familyInfoDT.key = 'UMCG_NUMBER'
subjectsDT = subjectsDT[:, :, dt.join(familyInfoDT)]

#///////////////////////////////////////

# ~ 1c ~
# Retrieve existing metadata from alissa_patients
print2('Pulling existing Alissa Patients....')

rawAlissaPatients = cosas.get('alissa_patients', batch_size=10000)
for row in rawAlissaPatients:
  for column in ['analyses', 'inheritanceAnalyses', 'variants']:
    if row.get(column):
      row[column] = ','.join([record['id'] for record in row[column]])
    else:
      row[column] = None

alissaPatients = dt.Frame(rawAlissaPatients)

# add new subjects to existing alissa subjects metadata
if alissaPatients.nrows:
  print2('Combining new patients with existing patients....')
  del alissaPatients['_href']
  
  # check for new subjects and
  # automatically rerun records with error overwrite isNew status where applicable
  subjectIDs = alissaPatients['umcgNr'].to_list()[0]
  subjectsWithErrors = alissaPatients[f.hasError, 'umcgNr'].to_list()[0]
  subjectsDT['isNew'] = dt.Frame([
    value not in subjectIDs
    for value in subjectsDT['UMCG_NUMBER'].to_list()[0]
  ])

  # reduce to new subjects only
  subjectsDT = subjectsDT[f.isNew, :]

else:
  print2('Initialising patients....')
  subjectsDT['isNew'] = True

# are there any subjects to process? If not, exit.
if subjectsDT.nrows == 0:
  print2('There are no new subjects. Stopping script.')
  cosas.logout()
  sys.exit(0)

subjectsDT.names = {'UMCG_NUMBER': 'umcgNr', 'FAMILIENUMMER': 'familieNr'}
del subjectsDT['isNew']

#///////////////////////////////////////////////////////////////////////////////

# ~ 2 ~
# Create Alissa Information
# Here we will create and retrieve the internal Alissa ID. This will save time
# when we we run the full variant script.

# ~ 2a ~
# CREATE ACCESSIONNUMBER
# we will use this information to search for patients in alissa in order to
# retrieve the internal identifier
print2('Creating accession number....')

subjectsDT['accessionNr'] = dt.Frame([
  '_'.join(row) if all(row) else None
  for row in subjectsDT[:, (f.familieNr, f.umcgNr)].to_tuples()
])

# RETRIEVE ALISSA INTERNAL ID
print2('Initialising columns for alissa API responses...')
subjectsDT[:, dt.update(
  alissaInternalID=as_type(None, str),
  dateFirstRun = datetime.now().strftime('%Y-%m-%d'),
  dateLastUpdated = as_type(None, str),
  hasError=as_type(None, bool),
  errorType=as_type(None, str),
  errorMessage=as_type(None, str),
  comments=as_type(None, str)
)]

# bind records with error as well
subjectsDT = dt.rbind(alissaPatients[f.hasError,:], subjectsDT, force=True)

# retrieve internal identifier from Alissa
ids = subjectsDT[f.accessionNr!=None,'accessionNr'].to_list()[0]
print2(f"Querying patient metadata for {len(ids)} patients....")
for id in ids:
  try:
    patientInfo = alissa.getPatients(accessionNumber=id)
    if patientInfo:
      # response is always an array of objects. Results may often include other
      # results if the accessionNumber is in the string. We need to make sure
      # we extract the correct ID using an extact match.
      for row in patientInfo:
        if (row['accessionNumber'] == id):
          subjectsDT[f.accessionNr==id, 'hasError'] = False
          subjectsDT[f.accessionNr==id, 'alissaInternalID'] = str(row['id'])
          
          # if previously failed cases are now resolved, updated date solved
          if subjectsDT[f.accessionNr==id, 'hasError'] == True:
            subjectsDT[f.accessionNr==id, 'dateLastUpdated'] = datetime.now().strftime('%Y-%m-%d')
            subjectsDT[f.accessionNr==id, ['errorType', 'errorMessage']] = None
            subjectsDT[f.accessionNr==id, 'comments'] = 'accession number resolved'

          # log error if no patient identifier was found
          if bool(row['id']):            
            raise ValueError(
              'no.identifier',
              'valid accessionNr and response, but no internal identifier found'
            )
          
      # if an internal ID was not located in the previous step, flag this case
      if subjectsDT[f.accessionNr==id, f.alissaInternalID].to_list()[0] == [None]:
        raise ValueError(
          'no.match',
          'valid accessionNr and results were returned, but no match could be found'
        )
      
      # if more than one result is returned, then add a comment to indicate
      # It's not important, but good for record keeping
      if len(patientInfo) > 1:
        subjectsDT[f.accessionNr==id, f.comments] = 'more than one record returned'
    
    else:
      raise ValueError(
        'empty.response',
        'valid accessionNr, but response had length of 0'
      )
      
  # log http errors
  except requests.exceptions.HTTPError as error:
    e = error
    if e.response.status_code == 500:
      message = 'subject not found in alissa'
    else:
      message = f'unable to retrieve information ({e.response.status_code})'
    subjectsDT[f.accessionNr==id, f.hasError] = True
    subjectsDT[f.accessionNr==id, f.errorType] = 'http.error'
    subjectsDT[f.accessionNr==id, f.errorMessage] = message
  
  # log errors raise in the previous steps
  except ValueError as error:
    e = error
    subjectsDT[f.accessionNr==id, f.hasError] = True
    subjectsDT[f.accessionNr==id, f.errorType] = e.args[0]
    subjectsDT[f.accessionNr==id, f.errorMessage] = e.args[1]

#///////////////////////////////////////

# ~ 3 ~
# import data
print2('Importing data into alissa_patients....')
cosas.importDatatableAsCsv(pkg_entity='alissa_patients', data = subjectsDT)
cosas.logout()
