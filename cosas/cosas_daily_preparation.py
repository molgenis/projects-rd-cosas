#//////////////////////////////////////////////////////////////////////////////
# FILE: cosas_daily_preparation.py
# AUTHOR: David Ruvolo
# CREATED: 2022-03-16
# MODIFIED: 2022-06-24
# PURPOSE: script to run before imports or mappings
# STATUS: stable
# PACKAGES: molgenis.client
# COMMENTS: NA
#//////////////////////////////////////////////////////////////////////////////

import molgenis.client as molgenis

# set session
host = 'http://localhost/api'
token = '${molgenisToken}'
cosasportal = molgenis.Session(url=host,token=token)

# define tables to delete
portaltables = [
    'cosasportal_patients',
    'cosasportal_diagnoses',
    'cosasportal_samples',
    'cosasportal_labs_array_adlas',
    'cosasportal_labs_array_darwin',
    'cosasportal_labs_ngs_adlas',
    'cosasportal_labs_ngs_darwin',
    'variantdb_variant'
]

# delete tables
for table in portaltables:
    print(f'Deleting data from {table}...')
    cosasportal.delete(entity = table)
