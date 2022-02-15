#'////////////////////////////////////////////////////////////////////////////
#' FILE: setup.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-02-15
#' MODIFIED: 2022-02-15
#' PURPOSE: script to setup the UMDM script in python
#' STATUS: 
#' PACKAGES: 
#' COMMENTS: 
#'////////////////////////////////////////////////////////////////////////////

from urllib.parse import urlparse, urlunparse
import molgenis.client as molgenis
from os.path import basename
import requests

# define class for listing metadata for public github repos
class github:
    def __init__(self):
        self.host = 'https://api.github.com/'
        self.headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        
    def _get(self, url, headers):
        try:
            r = requests.get(url, headers = headers)
            if not r.status_code // 100 == 2:
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
        raw = self._get(url, self.headers)
        return raw
        
class Molgenis(molgenis.Session):
    
    def __setSessionUrls__(self):
        props = list(self.__dict__.keys())
        if '_url' in props:
            self._apiUrl = self._url
        if '_api_url' in props:
            self._apiUrl = self._api_url
            
        if self._apiUrl:
            url = urlparse(self._apiUrl)
            url = url._replace(path = '')
            self._hostUrl = urlunparse(url)
    
    def importFile(self, filepath, action='ADD'):
        actions = [
            'ADD',
            'ADD_UPDATE_EXISTING',
            'UPDATE',
            'ADD_IGNORE_EXISTING'
        ]
        if action not in actions:
            raise KeyError(f'Value {str(action)} is not a valid action')
        
        self.__setSessionUrls__()
        url = '{}/plugin/importwizard/importByUrl?notify=false&action={}&url={}'.format(
            self._hostUrl,
            action.lower(),
            filepath
        )
        
        try:
            response = self._session.post(
                url = url,
                headers = self._get_token_header_with_content_type()
            )
            
            print(response.status_code, response.content)
            
            response.raise_for_status()
            
            if response.status_code // 100 == 2:
                print(f'Imported file {basename(filepath)}')
 
        except requests.exceptions.HTTPError as e:
            raise SystemError(e)

#//////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Fetch Available Files
#
# From the molgenis/rd-datamodel repository, compile a list of files associated
# with the 
gh = github()
repo = gh.contents(
    owner = 'molgenis',
    repo = 'rd-datamodel',
    path = 'dist/umdm-emx1'
)

# collate list of files: path should contain all umdm files, but run a check
# just to be sure
files = []
for file in repo:
    if (file.get('name') == 'umdm.xlsx') or ('umdm_lookups_' in file.get('name')):
        files.append({
            'name': file['name'],
            'download_url': file['download_url']
        })
        

# ~ 2 ~
# Import

db = Molgenis(url='http://localhost/api/', token='${molgenisToken}')

for file in files[:1]:
    print(f'Importing file {file.get("download_url")}')
    db.importFile(filepath = file.get('download_url'))
