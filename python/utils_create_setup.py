#'////////////////////////////////////////////////////////////////////////////
#' FILE: utils_create_setup.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-12-06
#' MODIFIED: 2022-02-08
#' PURPOSE: refresh setup.py file
#' STATUS: experimental
#' PACKAGES: pandas, requests
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

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

# List available files
gh = github()
emx = gh.contents(owner = 'molgenis', repo = 'rd-datamodel', path = 'emx/dist/')
lookups = gh.contents(owner = 'molgenis', repo = 'rd-datamodel', path = 'emx/lookups/')

files = [file['download_url'] for file in emx if file['name'] == 'urdm.xlsx'] + [file['download_url'] for file in lookups]
files = [f'mcmd import -u {file}\n' for file in files]

# Read existing setup.sh script and refresh contents
with open('dist/setup.sh', 'r') as stream:
    scriptContents = stream.readlines()
    stream.close()
 
startPattern = '# <!--- start: utils_create_setup.py --->\n'
endPattern = '# <!--- end: utils_create_setup.py --->\n'
baseContents = scriptContents[0:scriptContents.index(startPattern)+1]
endContents = scriptContents[scriptContents.index(endPattern):len(scriptContents)]

with open('dist/setup.sh', 'w') as stream:
    stream.writelines(baseContents)
    stream.writelines(files)
    stream.writelines(endContents)