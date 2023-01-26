#///////////////////////////////////////////////////////////////////////////////
# FILE: variantdb_alissa_prep.py
# AUTHOR: David Ruvolo
# CREATED: 2023-01-26
# MODIFIED: 2023-01-26
# PURPOSE: compile a list of information necessary for querying the alissa API
# STATUS: stable
# PACKAGES: **see below**
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from cosas.api.molgenis2 import Molgenis
from cosas.alissa.client import Alissa
from datatable import dt, f, as_type
from dotenv import load_dotenv
from datetime import datetime
from os import environ
from time import sleep
from tqdm import tqdm
import requests
load_dotenv()

db = Molgenis(environ['MOLGENIS_ACC_HOST'])
db.login(environ['MOLGENIS_ACC_USR'], environ['MOLGENIS_ACC_PWD'])

#///////////////////////////////////////

# ~ 1 ~
# Pull Information from the Portal
# In order to retrieve data from Alissa, we need to create the identifiers that
# we can use to retrieve data via the API. Using the information stored in
# `cosasportal_labs_ngs_adlas`, we can create a list of patients and samples to
# use in the Alissa search.

# pull patients listed in the `cosasportal_labs_ngs_adlas` and select distinct
# records
subjectsDT = dt.Frame(
  db.get(
    entity='cosasportal_labs_ngs_adlas',
    attributes='UMCG_NUMBER',
    batch_size=10000
  )
)[:, dt.first(f[:]), dt.by(f.UMCG_NUMBER)]['UMCG_NUMBER']


# pull patient info from patients portal table (i.e., `cosasportal_patients`)
# For the API, we need the familyID. We will merge the samples data with the
# family information. First, pull the data and select distinct rows only
familyInfoDT = dt.Frame(
  db.get(
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

# ~ 2 ~
# Create Alissa Information
# Here we will create and retrieve the internal Alissa ID. This will save time
# when we we run the full variant script.

# FOR TESTING ONLY --- TRIM DATASET TO 100 SUBJECTS ONLY
subjectsDT = subjectsDT[range(0,100),:]

# CREATE ACCESSIONNUMBER
# we will use this information to search for patients in alissa in order to
# retrieve the internal identifier
subjectsDT['accessionNr'] = dt.Frame([
  '_'.join(row)
  for row in subjectsDT[:, (f.FAMILIENUMMER, f.UMCG_NUMBER)].to_tuples()
])

# RETRIEVE ALISSA INTERNAL ID
# Connect to Alissa and search for patients using the accession number
alissa = Alissa(
  host=environ['ALISSA_HOST'],
  clientId=environ['ALISSA_CLIENT_ID'],
  clientSecret=environ['ALISSA_CLIENT_SECRET'],
  username=environ['ALISSA_API_USR'],
  password=environ['ALISSA_API_PWD']
)

# init additional columns
subjectsDT[:, dt.update(
  alissaInternalID=as_type(None, str),
  dateFirstRun = datetime.now().strftime('%Y-%m-%d'),
  hasError=as_type(None, bool),
  errorType=as_type(None, str),
  errorMessage=as_type(None, str),
  comments=as_type(None, str)
)]

# rename current columns
subjectsDT.names={
  'UMCG_NUMBER': 'umcgNr',
  'FAMILIENUMMER': 'familieNr'
}

# retireve internal identifier from Alissa
ids = subjectsDT['accessionNr'].to_list()[0]
for id in tqdm(ids):
  try:
    patientInfo = alissa.getPatients(accessionNumber=id)
    if patientInfo:
      # response is always an array of objects. Results may often include other
      # results if the accessionNumber is in the string. We need to make sure
      # we extract the correct ID using an extact match.
      for row in patientInfo:
        if row['accessionNumber'] == id:
          subjectsDT[f.accessionNr==id, f.hasError] = False
          subjectsDT[f.accessionNr==id, f.alissaInternalID] = str(row['id'])
          
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
  sleep(0.12)

# import data
db.importDatatableAsCsv(
  pkg_entity='alissa_patients',
  data = subjectsDT
)


#///////////////////////////////////////////////////////////////////////////////

# Misc Alissa Prep
variantExport = []  # retrieve data from the variant API to replicate this

# clean nested column names for a flattened structure
import re

labels = list(variantExport[0]['externalDatabases'].keys())
# labels = list(variantExport[0]['platformDatasets'].keys())
# labels = list(variantExport[0]['customFields'])

for index,label in enumerate(labels):
  lab1 = re.sub(r'[()\+]','',label)
  lab2 = re.sub(r'(\s+|[-/])', '_', lab1)
  labels[index] = f"_{lab2}"
  
[print(f"- name: {label}") for label in labels]
