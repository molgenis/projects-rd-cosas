#'////////////////////////////////////////////////////////////////////////////
#' FILE: setup.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-02-15
#' MODIFIED: 2022-03-03
#' PURPOSE: import UMDM files
#' STATUS: stable
#' PACKAGES: molgenis.client, datetime, os, requests, pytz, re
#' COMMENTS: This script is designed to run in MOLGENIS
#'////////////////////////////////////////////////////////////////////////////

import molgenis.client as molgenis
from datetime import datetime
from os.path import basename
import requests
import pytz
import re

# generic status message with timestamp
def status_msg(*args):
    """Status Message
    Print a log-style message, e.g., "[16:50:12.245] Hello world!"

    @param *args one or more strings containing a message to print
    @return string
    """
    message = ' '.join(map(str, args))
    time = datetime.now(tz=pytz.timezone('Europe/Amsterdam')).strftime('%H:%M:%S.%f')[:-3]
    print(f'[{time}] {message}')

# define class for listing metadata for public github repos
class github:
    def __init__(self):
        self.host = 'https://api.github.com/'
        self.headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        
    def _GET(self, url, headers):
        try:
            r = requests.get(url, headers = headers)
            if (r.status_code // 100) != 2:
                return f'Error: unable to import data({r.status_code}): {r.content}'
                
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as error:
            raise SystemError('Unable to get contents:\n{}'.format(error))
        
    def contents(self, owner: str, repo: str, path: str):
        """List contents at Github Repo Path
        
        Attributes:
            owner (str) : username who owns repository
            repo  (str) : name of the repository
            path  (str) : location of the files within the repository
            
        """
        url = f'{self.host}repos/{owner}/{repo}/contents/{path}'
        return self._GET(url, self.headers)
        
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
    
    def importFile(self, filepath, action='ADD'):
        actions = ['ADD','ADD_UPDATE_EXISTING','UPDATE','ADD_IGNORE_EXISTING']
        if action not in actions:
            raise KeyError(f'Value {str(action)} is not a valid action')
        
        url = '{}/plugin/importwizard/importByUrl?notify=false&action={}&url={}'.format(
            self._apiUrl, action.lower(), filepath
        )
        
        try:
            r = self._session.post(
                url=url, headers=self._get_token_header_with_content_type()
            )
            
            if (r.status_code // 100) != 2:
                err = r.json().get('errors')[0].get('message')
                status_msg(f'Failed to import file ({r.status_code}): {err}')
            else:
                status_msg(f'Imported {basename(filepath)}')
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise SystemError(e)

#//////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Fetch Available Files
# Based on the repositories defined above (see `reposToFetch`), list the files
# that are available to download and combine into a single object. Select files
# that match the expected file pattern.

gh = github()
availableFiles = gh.contents(
    owner = 'molgenis',
    repo = 'rd-datamodel',
    path = 'dist/umdm-emx1'
)

# collate list of files: path should contain all umdm files, but run a check
# just to be sure
files = []
for file in availableFiles:
    if re.search(r'^(umdm.xlsx|umdm_lookups_)', file.get('name')):
        files.append({
            'name': file['name'],
            'download_url': file['download_url']
        })
        

# ~ 2 ~
# Import
db = Molgenis(url='http://localhost/api/', token='${molgenisToken}')
for file in files:
    print(f'Importing file {file.get("download_url")}')
    db.importFile(filepath = file.get('download_url'))
