#'////////////////////////////////////////////////////////////////////////////
#' FILE: molgenis_emx1_client.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-12-03
#' MODIFIED: 2022-06-29
#' PURPOSE: extra functions for COSAS mapping
#' STATUS: stable
#' PACKAGES: molgenis.client, datetime, json, pytz
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

import molgenis.client as molgenis
from datetime import datetime
import pytz
import json

# <!--- start: cosastools --->
def status_msg(*args):
  """Status Message
  Print a log-style message, e.g., "[16:50:12.245] Hello world!"

  @param *args one or more strings containing a message to print
  @return string
  """
  message = ' '.join(map(str, args))
  time = datetime.now(tz=pytz.timezone('Europe/Amsterdam')).strftime('%H:%M:%S.%f')[:-3]
  print(f'[{time}] {message}')


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

  def _checkResponseStatus(self, response, label):
    if (response.status_code // 100) != 2:
      err = response.json().get('errors')[0].get('message')
      status_msg(f'Failed to import data into {label} ({response.status_code}): {err}')
    else:
      status_msg(f'Imported data into {label}')

  def _POST(self, url: str = None, data: list = None, label: str = None):
    response = self._session.post(
      url=url,
      headers=self._get_token_header_with_content_type(),
      data=json.dumps({'entities': data})
    )
    self._checkResponseStatus(response, label)
    response.raise_for_status()

  def _PUT(self, url: str = None, data: list = None, label: str = None):
    response = self._session.put(
      url=url,
      headers=self._get_token_header_with_content_type(),
      data=json.dumps({'entities': data})
    )
    self._checkResponseStatus(response, label)
    response.raise_for_status()
  
  def _datatableToCsv(self, path, datatable):
    """To CSV
    Write datatable object as CSV file

    @param path location to save the file
    @param data datatable object
    """
    datatable.to_pandas().replace({np.nan: None}).to_csv(path, index=False, quoting=csv.QUOTE_ALL)
  
  def importDatatableAsCsv(self, filename: str, data, label: str):
    with tempfile.TemporaryDirectory() as tmpdir:
      filepath=f"{tmpdir}/{filename}"
      self._datatableToCsv(filepath, data)
      
      response = self._session.post(
        url=self._fileImportUrl,
        headers = self._get_token_header(),
        files={'file': open(filepath, 'rb')},
        params = {
          'action': 'add_update_existing',
          'metadataAction': 'ignore'
        }
      )
      self._checkResponseStatus(response, label)

  def importData(self, entity: str, data: list):
    """Import Data
    Import data into a table. The data must be a list of dictionaries that
    contains the 'idAttribute' and one or more attributes that you wish
    to import.

    @param entity (str) : name of the entity to import data into
    @param data (list) : data to import (a list of dictionaries)

    @return a status message
    """
    url = '{}v2/{}'.format(self._apiUrl, entity)
    # single push
    if len(data) < 1000:
      self._POST(url=url, data=data, label=str(entity))

    # batch push
    if len(data) >= 1000:
      for d in range(0, len(data), 1000):
        self._POST(
          url=url,
          data=data[d:d+1000],
          label='{} (batch {})'.format(str(entity), str(d))
        )

  def updateRows(self, entity: str, data: list):
    """Update Rows
    Update rows in a table. The data must be a list of dictionaries that
    contains the 'idAttribute' and must contain values for all attributes
    in addition to the one that you wish to update. This is ideal for
    updating rows. To update an attribute, use `updateColumn`.

    @param entity (str) : name of the entity to import data into
    @param data (list) : data to import (list of dictionaries)

    @return a status message
    """
    url = '{}v2/{}'.format(self._apiUrl, entity)
    # single push
    if len(data) < 1000:
      self._PUT(url=url, data=data, label=str(entity))

    # batch push
    if len(data) >= 1000:
      for d in range(0, len(data), 1000):
        self._PUT(
          url=url,
          data=data[d:d+1000],
          label='{} (batch {})'.format(str(entity), str(d))
        )

  def updateColumn(self, entity: str, attr: str, data: list):
    """Update Column
    Update values of an single column in a table. The data must be a list of
    dictionaries that contain the `idAttribute` and the value of the
    attribute that you wish to update. As opposed to the `updateRows`, you
    do not need to supply values for all columns.

    @param entity (str) : name of the entity to import data into
    @param attr (str) : name of the attribute to update
    @param data (list) : data to import (list of dictionaries)

    @retrun status message
    """
    url = '{}v2/{}/{}'.format(self._apiUrl, str(entity), str(attr))

    # single push
    if len(data) < 1000:
      self._PUT(url=url, data=data, label=f'{entity}/{attr}')

    # batch push
    if len(data) >= 1000:
      for d in range(0, len(data), 1000):
        self._PUT(
          url=url,
          data=data[d:d+1000],
          label='{}/{} (batch {})'.format(str(entity),str(attr), str(d))
        )

                
# <!--- end: cosastools --->