#///////////////////////////////////////////////////////////////////////////////
# FILE: alissa_get_analyses.py
# AUTHOR: David Ruvolo
# CREATED: 2023-06-08
# MODIFIED: 2023-06-08
# PURPOSE: retrieve patient analyses from Alissa Interpret
# STATUS: in.progress
# PACKAGES: **see below**
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
from datatable import dt, f, as_type
import molgenis.client as molgenis
from datetime import datetime
from os.path import abspath
from time import sleep
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

  def getPatientAnalyses(self, patientId: str) -> dict:
    """Get Analyses of Patient

    @param patientId The unique internal identifier of the patient

    @reference Alissa Interpret Public API (v5.3; p42)
    @return dictionary containing metadata for one or more analyses
    """
    return self._get(endpoint=f"patients/{patientId}/analyses")

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
from dotenv import load_dotenv
load_dotenv()
from os import environ

cosas = Molgenis(environ['MOLGENIS_ACC_HOST'])
cosas.login(environ['MOLGENIS_ACC_USR'], environ['MOLGENIS_ACC_PWD'])
alissa = Alissa(
  host=environ['ALISSA_HOST'],
  clientId=environ['ALISSA_CLIENT_ID'],
  clientSecret=environ['ALISSA_CLIENT_SECRET'],
  username=environ['ALISSA_API_USR'],
  password=environ['ALISSA_API_PWD']
)


test = cosas.get('alissa_patients',q="hasError==false",num=10)

data = []
for row in test:
  tmp = alissa.getPatientAnalyses(patientId=row['alissaInternalID'])
  data.extend(tmp)

from datatable import dt, f, as_type
dataDT = dt.Frame(data)





#///////////////////////////////////////

# ~ DEPLOY ~
# for deployment
print2('\tConnecting to MOLGENIS....')

# cosas = Molgenis('http://localhost/api/', token='${molgenisToken}')

# print2('\tRetrieving credentials for Alissa....')
# credentials = cosas.get(
#   'sys_sec_Token',
#   q='description=like="alissa-api-"',
#   attributes='token,description'
# )

# host=filterList(credentials,'description','alissa-api-host')['token']
# clientId=filterList(credentials,'description','alissa-api-client-id')['token']
# clientSecret=filterList(credentials,'description', 'alissa-api-client-secret')['token']
# apiUser=filterList(credentials,'description','alissa-api-username')['token']
# apiPwd=filterList(credentials,'description','alissa-api-password')['token']


# print2('\tConnecting to Alissa UMCG....')
# alissa = Alissa(
#   host=host,
#   clientId=clientId,
#   clientSecret=clientSecret,
#   username=apiUser,
#   password=apiPwd
# )

#///////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Retrieve Analyses

# get list of patients that do not have errors
print2('Pulling existing Alissa Patients....')
subjectsDT = dt.Frame(
  cosas.get(
    entity='alissa_patients',
    q='hasError==false',
    batch_size=10000
  )
)

# get a list of analyses that do not have errors
analysesDT = dt.Frame(
  cosas.get(
    entity='alissa_analyses',
    q='hasError==false',
    batch_size='10000'
  )
)

# 

test = alissa


