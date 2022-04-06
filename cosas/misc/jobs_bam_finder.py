#'////////////////////////////////////////////////////////////////////////////
#' FILE: jobs_bam_finder.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-10-28
#' MODIFIED: 2021-10-28
#' PURPOSE: Randomly select samples for finding BAM files
#' STATUS: in.progress
#' PACKAGES: molgenis.client
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////


# imports
import molgenis.client as molgenis
from urllib.parse import quote_plus
from datetime import datetime
import json
import requests
import random
import string

# extend molgenis.Session class
class molgenis(molgenis.Session):
    """molgenis
    An extension of the molgenis.client class
    """
    
    # update_table
    def update_table(self, entity: str, data: list):
        """Update Table
        
        When importing data into a new table using the client, there is a 1000
        row limit. This method allows you push data without having to worry
        about the limits.
        
        @param entity (str) : name of the entity to import data into
        @param data (list) : data to import
        
        @return a status message
        """
        props = list(self.__dict__.keys())
        if '_url' in props: url = self._url
        if '_api_url' in props: url = self._api_url
        url = f'{url}v2/{quote_plus(entity)}'
        
        # single push
        if len(data) < 1000:
            try:
                response = self._session.post(
                    url = url,
                    headers = self._get_token_header_with_content_type(),
                    data = json.dumps({'entities' : data})
                )
                if not response.status_code // 100 == 2:
                    return f'Error: unable to import data({response.status_code}): {response.content}'
                
                return f'Imported {len(data)} entities into {str(entity)}'
            except requests.exceptions.HTTPError as err:
                raise SystemError(err)
        
        # batch push
        if len(data) >= 1000:    
            for d in range(0, len(data), 1000):
                try:
                    response = self._session.post(
                        url = url,
                        headers = self._get_token_header_with_content_type(),
                        data = json.dumps({'entities': data[d:d+1000] })
                    )
                    if not response.status_code // 100 == 2:
                        raise response.raise_for_status()

                    return f'Batch {d}: Imported {len(data)} entities into {str(entity)}'
                except requests.exceptions.HTTPError as err:
                    raise SystemError(f'Batch {d} Error: unable to import data:\n{str(err)}')
                    

# create status message
def status_msg(*args):
    """Status Message
    
    Prints a message with a timestamp
    
    @param *args : message to write 
    
    @example
    status_msg('hello world')
    
    """
    msg = ' '.join(map(str, args))
    t = datetime.utcnow().strftime('%H:%M:%S.%f')[:-3]
    print('\033[94m[' + t + '] \033[0m' + msg)
    
def random_id(n = 6):
    """Generate a Random ID
    
    Create a string of random letters and digits
    
    @param n (int) : number of characters to return
    
    @return string
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k = n))
    

#//////////////////////////////////////////////////////////////////////////////

status_msg('Starting BAM file metadata job...')

# init record for jobs entity
job = {
    'id': 'bam_' + random_id(n = 6),
    'name': 'bam metadata',
    'description': 'randomly select samples and extract required data for finding BAM files',
    'start': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S:%fZ'),
    'end': None,
    'status': 'ongoing',
    'outputEntity': 'jobs_results_bamdata',
    'comment': 'job started'
}

# init connection
# db = molgenis(url = 'http://localhost/api/', token='${}')
db = molgenis(url = 'http://localhost/api/')
db.login()

# pull required tables
status_msg('Pulling data from the patient and lab tables...')
patients = db.get(
    entity = 'cosas_patients',
    attributes = 'umcgID,biologicalSex', 
    batch_size=10000
)

samples = db.get(
    entity = 'cosas_labs_ngs',
    q = 'labIndication==informative',
    attributes = 'umcgID,dnaID,labIndication,genomeBuild',
)

# update status
if patients and samples:
    job['comment'] = 'pulled data'