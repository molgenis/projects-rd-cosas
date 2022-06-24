#'////////////////////////////////////////////////////////////////////////////
#' FILE: cosasportal_delete_data_WARNING.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-02-15
#' MODIFIED: 2022-03-02
#' PURPOSE: clear all portal tables
#' STATUS: stable
#' PACKAGES: molgenis.client
#' COMMENTS: DANGER Only run if you know what you are doing. This script should
#' be run on situtations where you need to reset the portal tables. For example,
#' you are testing a new job, updating the EMX, or something else. If you have
#' removed the cosasportal package for any reason, you must re-add all of the
#' approved users (i.e., import bots)
#'////////////////////////////////////////////////////////////////////////////

import molgenis.client as molgenis

# define databases to wipe
databases = [
    'umdm',
    'cosasreports',
    'cosasportal',
    'variantdb'
]

# set session
host = 'http://localhost/api'
token = '${molgenisToken}'
cosasportal = molgenis.Session(url=host,token=token)

# define tables IDs
tables = {
    'cosasportal': [
        'cosasportal_patients',
        'cosasportal_diagnoses',
        'cosasportal_samples',
        'cosasportal_labs_array_adlas',
        'cosasportal_labs_array_darwin',
        'cosasportal_labs_ngs_adlas',
        'cosasportal_labs_ngs_darwin',
        # 'cosasportal_benchcnv',
        # 'cosasportal_benchcnv_prepped',
    ],
    'cosasreports': [
        'cosasreports_imports',
        'cosasreports_processingsteps'
    ],
    'umdm': [
        'umdm_files',
        'umdm_sequencing',
        'umdm_samplePreparation',
        'umdm_samples',
        'umdm_clinical',
        'umdm_subjects'
    ],
    'variantdb': [
        'variant'
    ]
}
    
# wipe tables per each database
for db in databases:
    print(f'Deleting data from {db}...')
    for table in tables.get(db):
        print(f'Deleting data from {table}...')
        cosasportal.delete(entity = table)

