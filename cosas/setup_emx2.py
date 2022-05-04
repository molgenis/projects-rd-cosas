#//////////////////////////////////////////////////////////////////////////////
# FILE: setup_emx2.py
# AUTHOR: David Ruvolo
# CREATED: 2022-05-03
# MODIFIED: 2022-05-04
# PURPOSE: setup umdm for emx2
# STATUS: stable
# PACKAGES: **see below**
# COMMENTS: To get started with EMX2, sign in to your EMX2 instance and
# create two schemas.
#
#   1) unifiedmodel
#   2) unifiedmodel_lookups
#
# Navigate to the rd_datamodel repository and import the corresponding
# xlsx files into each schema. Return to this script and continue with
# data importing.
#//////////////////////////////////////////////////////////////////////////////

from cosas.api.molgenis_emx2_client import Molgenis
from dotenv import load_dotenv
from os import environ, listdir, path
import pandas as pd

# set credentials
load_dotenv()
host=environ['EMX2_HOST']
email=environ['EMX2_USERNAME']
password=environ['EMX2_PASSWORD']

# sign in to both schemas
unifiedmodel=Molgenis(url=host, database='unifiedmodel')
unifiedmodelrefs=Molgenis(url=host, database='unifiedmodel_lookups')

unifiedmodel.signin(email=email, password=password)
unifiedmodelrefs.signin(email=email, password=password)


# define files to import for all schemas. Create a new record for
# each file that you wish to import using the following format:
# `tablename: filepath`
files={
    'unifiedmodel': {
        'organizations': 'lookups/umdm_organizations.csv',
        'labProcedures': 'lookups/umdm_labProcedures.csv'
    }
}

umdmDir='/Users/dcruvolo/GitHub/rd-datamodel'
files['unifiedmodel_lookups'].update({
    file.replace('.csv','').split('_')[-1]: f'{umdmDir}/lookups/{file}'
    for file in listdir(f'{umdmDir}/lookups')
    if file not in [
        'umdm_lookups_biospecimenUsability.csv'
    ]
})


# import lookups
for file in files['unifiedmodel_lookups']:
    unifiedmodelrefs.importCsvFile(
        table=file,
        file=files['unifiedmodel_lookups'][file]
    )

# import lookup cosas 
for file in files['unifiedmodel']:
    unifiedmodel.importCsvFile(
        table=file,
        file=files['unifiedmodel'][file]
    )
    

# manually import cosas extensions
unifiedmodelrefs.importCsvFile(
    table='biospecimenType',
    file='lookups/umdm_lookups_biospecimenType.csv'
)
