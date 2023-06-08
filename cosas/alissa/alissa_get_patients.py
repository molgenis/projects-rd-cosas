#///////////////////////////////////////////////////////////////////////////////
# FILE: variantdb_alissa_prep.py
# AUTHOR: David Ruvolo
# CREATED: 2023-01-26
# MODIFIED: 2023-06-08
# PURPOSE: compile a list of information necessary for querying the alissa API
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
import requests
import tempfile
import pytz
import csv
import sys

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
      
  def _post(self, endpoint, data=None, json=None, **kwargs):
    """POST
    
    @param endpoint the Alissa Interpret endpoint where data should be
        sent to. The path "/interpret/api/2" is prefilled.
    @param data Optional dictionary, list of tuples, bytes, or file-like
        object
    @param json Optional json data
    """
    uri = f'{self.apiUrl}/{endpoint}'
    response = self.session.post(uri, data, json, **kwargs)
    response.raise_for_status()
    return response.json()

  def getPatients(
    self,
    accessionNumber: str = None,
    createdAfter: str = None,
    createdBefore: str = None,
    createdBy: str = None,
    familyIdentifier: str = None,
    lastUpdatedAfter: str = None,
    lastUpdatedBefore: str = None,
    lastUpdatedBy: str = None
  ) -> dict:
    """Get Patients
    Get all patients. When filter criteria are provided, the result is
    limited to the patients matching the criteria.

    @param accessionNumber The unique identifier of the patient
    @param createdAfter Filter patients with a creation date after the
        specific date time (ISO 8601 date time format)
    @param createdBefore Filter patients with a creation date before the
        specific date time (ISO 8601 date time format)
    @param createdBy User that created the patient
    @param familyIdentifier The unique identifier of the family.
    @param lastUpdatedAfter Filter patients with a last updated date after
        the specified date time (ISO 8601 date time format)
    @param lastUpdatedBefore Filter patients with a last updated date
        before the specified date time (ISO 8601 date time format)
    @param lastUpdatedBy User that updated the patient.
    
    @reference Alissa Interpret Public API (v5.3; p21)
    @return dictionary containing one or more patient records
    """
    params = self._formatOptionalParams(params=locals())
    return self._get(endpoint='patients', params=params)

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
print2('Starting sessions with API....')

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
print2('\tConnecting to MOLGENIS....')

cosas = Molgenis('http://localhost/api/', token='${molgenisToken}')

print2('\tRetrieving credentials for Alissa....')
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

print2('\tConnecting to Alissa UMCG....')
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
alissaPatients = dt.Frame(cosas.get('alissa_patients', batch_size=10000))

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

# retireve internal identifier from Alissa
print2('Querying Alissa for internal patient information....')
ids = subjectsDT[f.accessionNr!=None,'accessionNr'].to_list()[0]
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
