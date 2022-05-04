#'////////////////////////////////////////////////////////////////////////////
#' FILE: molgenis_emx2_client.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-02-09
#' MODIFIED: 2022-02-23
#' PURPOSE: EMX2 API py client
#' STATUS: in.progress
#' PACKAGES: requests
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

from urllib.parse import urlparse, urlunparse
from cosas.utils.cli import cli
from os import path
import requests

def __clean__url__(url):
    """Clean Urls
    @param url (str) : string containing a URL
    """
    urlNew = urlparse(url)
    urlNew = urlNew._replace(path = urlNew.path.replace('//','/'))
    return urlunparse(urlNew)


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
        self.cli.alert_success(
            f'Configured client for schema {self.cli.text_value(self.database)} at host {self.cli.text_value(self._url)}'
        )
        
    def signin(self, email, password):
        """Signin
        Login into an EMX2 instance with your email and password
        @param email (str) : email address associated with your account
        @param password (str) : your password
        @return a status message
        """
        self.user_email = email
        variables = {'email': email, 'password': password}
        query = """
            mutation($email:String, $password: String) {
                signin(email: $email, password: $password) {
                    status
                    message
                }
            }
        """
        response = self.session.post(
            url=self._url_signin,
            json={
                'query': query,
                'variables': variables
            }
        )
        response.raise_for_status()
        msg = f'{self.cli.text_value(self.database)} as {self.cli.text_value(email)}'
        status = response.json().get('data',{}).get('signin')
        
        if status.get('status') == 'SUCCESS':
            self.cli.alert_success(f'signed into {msg}')
        else:
            self.cli.alert_error(
                f'unable to sign into {msg}: {status.get("message")}'
            )
         
   
    def POST(self, url, **kwargs):
        response=self.session.post(url=url, **kwargs)
        response.raise_for_status()
        return response
        
    def importCsvFile(self, table, file):
        """Import CSV File
        Import a csv file into a table
        
        Attributes:
            table : name of the table
            file  : path to the location to a csv file
            
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
        url=f'{self._url_db_api}/csv/{table}'
        with open(file, 'rb') as data:
            dataBinary = data.read()
            data.close()
        response=self.POST(url=url, data=dataBinary)

        location=f"{self.cli.text_value(self.database)}::{self.cli.text_value(table)}"
        if response.status_code == 200:
            self.cli.alert_success(f'Imported data into {location}')
        else:
            self.cli.alert_error(f'Failed to import data into {location}')
                
            
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
        url=f'{self._url_db_api}/csv/{table}'
        response=self.POST(url, data=data)
        location=f"{self.cli.text_value(self.database)}::{self.cli.text_value(table)}"
        if response.status_code == 200:
            self.cli.alert_success(f'Imported data into {location}')
        else:
            self.cli.alert_error(f'Failed to import data into {location}')
