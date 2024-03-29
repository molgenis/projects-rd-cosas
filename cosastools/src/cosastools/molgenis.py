import molgenis.client as molgenis
from datetime import datetime
from os.path import abspath
import numpy as np
import tempfile
import pytz
import csv

def now(tz='Europe/Amsterdam', strftime=True):
  """Now
  Print current time as datetime object or as string formatted time.
  
  @param tz string containing a timezone name
  @param strftime if True, the current time will be formatted as HOUR:MINUTE:SECOND
  
  @return datetime or string
  """
  time = datetime.now(tz=pytz.timezone(tz))
  if strftime:
    return time.strftime('%H:%M:%S.%f')[:-3]
  return time
  
def print2(*args):
  """Print2
  Print a message with a timestamp, e.g., "[16:50:12.245] Hello world!".

  @param *args one or more strings containing a message to print
  @return string
  """
  message = ' '.join(map(str, args))
  print(f"[{now()}] {message}")


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
