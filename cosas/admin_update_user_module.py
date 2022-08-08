#'////////////////////////////////////////////////////////////////////////////
#' FILE: admin_update_user_module.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-08-08
#' MODIFIED: 2022-08-08
#' PURPOSE: Refresh lookup tables for user module
#' STATUS: stable
#' PACKAGES: **see below**
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

import molgenis.client as molgenis
from os.path import abspath
import numpy as np
import datetime
import tempfile
import pytz
import csv
import re
from datatable import dt

class Molgenis(molgenis.Session):
  def __init__(self, *args, **kwargs):
    super(Molgenis, self).__init__(*args, **kwargs)
    self.__getApiUrl__()

  def __getApiUrl__(self):
    """Find API endpoint regardless of version"""
    props = list(self.__dict__.keys())
    if '_url' in props:
      self._apiUrl = self._url
    if '_api_url' in props:
      self._apiUrl = self._api_url
      
    host=self._apiUrl.replace('/api/','')
    self._fileImportUrl=f"{host}/plugin/importwizard/importFile"
  
  def _print(self, *args):
    """Print
    Print a message with a timestamp, e.g., "[16:50:12.245] Hello world!".

    @param *args one or more strings containing a message to print
    @return string
    """
    message = ' '.join(map(str, args))
    time = datetime.datetime.now(tz=pytz.timezone('Europe/Amsterdam')).strftime('%H:%M:%S.%f')[:-3]
    print(f'[{time}] {message}')

  def _checkResponseStatus(self, response, label):
    if (response.status_code // 100) != 2:
      err = response.json().get('errors')[0].get('message')
      self._print('Failed to import data into',label,'(',response.status_code,'):',err)
    else:
      self._print('Imported data into', label)
  
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
          url=self._fileImportUrl,
          headers = self._get_token_header(),
          files={'file': file},
          params = {'action': 'add_update_existing', 'metadataAction': 'ignore'}
        )
        self._checkResponseStatus(response, pkg_entity)
        return response

#//////////////////////////////////////////////////////////////////////////////

# for local tests
# from cosas.api.molgenis2 import Molgenis
# from dotenv import load_dotenv
# from os import environ
# load_dotenv()
# db = Molgenis(environ['MOLGENIS_ACC_HOST'])
# db.login(environ['MOLGENIS_ACC_USR'], environ['MOLGENIS_ACC_PWD'])


# Connect to DB and pull pkgs and roles from the system tables
db = Molgenis(url = 'http://localhost/api/', token = '${molgenisToken}')


db._print('Compiling system packages and roles....')
pkgs = db.get('sys_md_Package')
roles = db.get('sys_sec_Role')

# extract packages
users_packages = dt.Frame()
for p in pkgs:
  if not (re.match(r'^(sys([_])?)|app_set', p['id'])):
    users_packages = dt.rbind(
      users_packages,
      dt.Frame([{
        'id': p['id'],
        'label': p['label'],
        'description': p.get('description')
      }])
    )
    
users_roles = dt.Frame()
for r in roles:
  if ((re.search(r'((_MANAGER)|(_EDITOR)|(_VIEWER))$', r['name'])) or (r['name'] == 'SU')) and ('app_set' not in r['name']):
    users_roles = dt.rbind(
      users_roles,
      dt.Frame([{
        'id': r['name'],
        'label': r['name'] if r['name'] == 'SU' else r['name'].replace('_', ' ').title(),
        'description': r.get('description')
      }])
    )

# importing data
db._print('Importing data into User module tables....')
db.importDatatableAsCsv(pkg_entity="users_packages", data=users_packages)
db.importDatatableAsCsv(pkg_entity="users_userPrivileges", data=users_roles)
