#'////////////////////////////////////////////////////////////////////////////
#' FILE: emx2_client.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-02-09
#' MODIFIED: 2022-02-09
#' PURPOSE: EMX2 API py client
#' STATUS: in.progress
#' PACKAGES: requests
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////


from urllib.parse import urlparse, urlunparse
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
        self._stop = '\033[0m'
        self.success = '\033[92m✓' + self._stop
        self.fail = '\033[91mx' + self._stop
        self.warning = '\033[93m!' + self._stop
        self.blue = '\033[94m'
    
    def alert_success(self, message):
        """Print a success message"""
        print(f'{self.success} {message}')

    def alert_error(self, message):
        """Print an error message"""
        print(f'{self.fail} {message}')

    def alert_warning(self, message):
        """Print a warning message"""
        print(f'{self.warning} {message}')
        
    def value(self, value):
        """Wrap value in a color"""
        return self.blue + str(value) + self._stop


class molgenis:
    def __init__(self, url, database):
        self.user_email = None
        self.user_info = None
        self.database = database
        self.url = __clean__url__(url)
        self._url_signin = f'{self.url}/apps/central/graphql'
        self._url_db = f'{self.url}/{self.database}/'
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
        self.user_info = f'{self.cli.value(self.database)} as {self.cli.value(email)}'
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
            
    def importCSV(self, table, data):
        """Import Data
        """
        try:
            response = self.session.post(
                url = f'{self._url_db_api}/csv/{table}',
                headers = {'Content-Type': 'text/csv'},
                data = data
            )
            
            if response.status_code // 100 == 2:
                self.cli.alert_success(f'imported data into {table}')
            else:
                self.cli.alert_error(f'failed to import data into {table}')
        
        except requests.exceptions.HTTPError as error:
            self.cli.alert_error(f'unable to sign into {self.user_info}')
            raise SystemError(error)
        
m = molgenis(url = 'https://diagnostics-acc.molgeniscloud.org', database = 'umdm')
m.signin(
    email = 'admin',
    password = 'SOLID-stoppage-magnify-bounce'
)