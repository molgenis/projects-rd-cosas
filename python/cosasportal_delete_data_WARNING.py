#'////////////////////////////////////////////////////////////////////////////
#' FILE: cosasportal_delete_data_WARNING.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-02-15
#' MODIFIED: 2022-02-15
#' PURPOSE: clear all portal tables
#' STATUS: experimental
#' PACKAGES: molgenis.client
#' COMMENTS: DANGER Only run if you know what you are doing. This script should
#' be run on situtations where you need to reset the portal tables. For example,
#' you are testing a new job, updating the EMX, or something else. If you have
#' removed the cosasportal package for any reason, you must re-add all of the
#' approved users (i.e., import bots)
#'////////////////////////////////////////////////////////////////////////////

import molgenis.client as molgenis

host = 'http://localhost/api'
token = '${molgenisToken}'

cosasportal = molgenis.Session(url=host,token=token)

# define tables to wipe
tables = [
    'cosasportal_patients',
    'cosasportal_diagnoses',
    'cosasportal_samples',
    'cosasportal_labs_array_adlas',
    'cosasportal_labs_array_darwin',
    'cosasportal_labs_ngs_adlas',
    'cosasportal_labs_ngs_darwin'
]

# wipe tables
for t in tables:
    print(f'Warning: deleting {t}')
    cosasportal.delete(entity = t)

