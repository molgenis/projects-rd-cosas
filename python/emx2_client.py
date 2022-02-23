#'////////////////////////////////////////////////////////////////////////////
#' FILE: emx2_client.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-02-09
#' MODIFIED: 2022-02-23
#' PURPOSE: EMX2 API py client
#' STATUS: in.progress
#' PACKAGES: requests
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

from urllib.parse import urlparse, urlunparse
from os import path
import requests

def __clean__url__(url):
    """Clean Urls
    @param url (str) : string containing a URL
    """
    urlNew = urlparse(url)
    urlNew = urlNew._replace(path = urlNew.path.replace('//','/'))
    return urlunparse(urlNew)


class cli:
    def __init__(self):
        self._start = '\u001b'
        self._stop = '\u001b[0m'
        self._blue = '[34;1m'
        self._green = '[32:1m'
        self._red = '[31;1m'
        self._white = '[37;1m'
        self._yellow = '[33;1m'
        
        self.error = self.__setStatus__(self._red, '⨉')
        self.success = self.__setStatus__(self._green, '✓')
        self.warning = self.__setStatus__(self._yellow, '!')
        
    def __setStatus__(self, color, text):
        return self._start + color + text + self._stop
    
    def alert_success(self, text):
        """Print a success message"""
        print(f'{self.success} {text}')

    def alert_error(self, text):
        """Print an error message"""
        print(f'{self.error} {text}')

    def alert_warning(self, text):
        """Print a warning message"""
        print(f'{self.warning} {text}')
        
    def text_value(self, text):
        """Style text as a value"""
        return self._start + self._blue + str(text) + self._stop
    
    def text_success(self, text):
        """Style text as a success message"""
        return self._start + self._green + str(text) + self._stop
        
    def text_error(self, text):
        """Style text as an error message"""
        return self._start + self._red + str(text) + self._stop
    
    def text_warning(self, text):
        """Style text as an warning message"""
        return self._start + self._yellow + str(text) + self._stop


class Molgenis:
    def __init__(self, url, database):
        self.user_email = None
        self.user_info = None
        self.database = database
        self.signedIn = False
        self._url = __clean__url__(url)
        self._url_signin = f'{self._url}/apps/central/graphql'
        self._url_db = f'{self._url}/{self.database}'
        self._url_db_api = f'{self._url_db}/api'
        self._url_db_graphql = f'{self._url_db}/graphql'
        self.session = requests.Session()
        self.cli = cli()
        
    def signin(self, email, password):
        """Signin
        Login into an EMX2 instance with your email and password
        @param email (str) : email address associated with your account
        @param password (str) : your password
        @return a status message
        """
        
        self.user_email = email
        self.user_info = f'{self.cli.text_value(self.database)} as {self.cli.text_value(email)}'
        variables = {'email': email, 'password': password}
        
        query = """
            mutation($email:String, $password: String) {
                signin(email: $email, password: $password) {
                    status
                    message
                }
            }
        """
        
        try:
            response = self.session.post(
                url = self._url_signin,
                json = {'query': query, 'variables': variables}
            )

            response.raise_for_status()
            status = response.json().get('data').get('signin')
            
            if status.get('status') == 'SUCCESS':
                self.cli.alert_success(f'signed into {self.user_info}')
            else:
                self.cli.alert_error(
                    f'unable to sign into {self.user_info}: {status.get("message")}'
                )

        except requests.exceptions.HTTPError as error:
            self.cli.alert_error(f'Unable to sign into {self.user_info}')
            return SystemError(error)
         
   
    def __postData__(self, table, data):
        try:
            response = self.session.post(
                url = f'{self._url_db_api}/csv/{table}',
                data = data
            )
            
            if response.status_code == 200:
                self.cli.alert_success(
                    'imported data into {}/{}'.format(
                        self.cli.text_value(self.database),
                        self.cli.text_value(table)
                    )
                )
            else:
                self.cli.alert_error(
                    'failed to import data into {}/{}:\n  {}'
                    .format(
                        self.cli.text_value(self.database),
                        self.cli.text_value(table),
                        response.json().get('errors')[0].get('message')
                    )
                )

        except requests.exceptions.HTTPError as error:
            self.cli.alert_error(
                'failed to import data into {}/{}:'
                .format(
                    self.cli.text_value(self.database),
                    self.cli.text_value(table),
                )
            )
            raise SystemError(error)
            
        
    def importCsvFile(self, table, filename):
        """Import CSV File
        Import a csv file into a table
        
        Attributes:
            table     : name of the table
            filename  : location to a csv file
            
        Examples:
            ````
            from src.python.emx2_client import Molgenis
            
            # connect to EMX2 database
            db = Molgenis(url='https://my-emx2-server.com', database='test')
            db.signin(email='myusername', password='mypassword')
            
            # import file
            db.importCsvFile(table = 'myTable', filename='data.csv')
            ````
        """
        
        if not path.isfile(filename):
            raise ValueError('File does not exist')
        
        with open(filename, 'rb') as data:
            self.__postData__(table = table, data = data)
            data.close()
                
            
    def importData(self, table: str = None, data: str = None):
        """Import Data
        Import a data object into a schema table
       
        Attributes:
            table : name of the table
            data  : a string containing your data as a text/csv object
            
        Example:
            ````
            from src.python.emx2_client import Molgenis
            import pandas as pd
            
            # connect to EMX2 database
            db = Molgenis(url='https://my-emx2-server.com', database='test')
            db.signin(email='myusername', password='mypassword')
            
            # load data and apply transformations (if applicable)
            data = pd.read_csv('data.csv')
            data_str = data.to_csv(index=False)
            
            # import data
            db.importData(table = 'myTable', data = data_str)
            
            ````
        """
        self.__postData__(table = table, data = data)
