#'////////////////////////////////////////////////////////////////////////////
#' FILE: mappings_cosasrefs.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-10-07
#' MODIFIED: 2022-02-25
#' PURPOSE: build the laboratoryProcedures lookup table
#' STATUS: stable
#' PACKAGES: datatable
#' COMMENTS: This script should be run only if there are major updates or
#'  if the database needs to be rebuilt. This is script is designed to be run
#'  once. If new entries need to be added, then handle them independently.
#'////////////////////////////////////////////////////////////////////////////

import molgenis.client as molgenis
from datatable import dt, f, first
from dotenv import load_dotenv
from datetime import datetime
from os import environ
import pandas as pd
import numpy as np

load_dotenv()
host = environ['MOLGENIS_HOST_ACC']
token = environ['MOLGENIS_TOKEN_ACC']

def status_msg(*args):
    """Status Message
    Print a log-style message, e.g., "[16:50:12.245] Hello world!"

    @param *args one or more strings containing a message to print
    @return string
    """
    print('[{}] {}'.format(
        datetime.utcnow().strftime('%H:%M:%S.%f')[:-3], ' '.join(map(str, args))
    ))


db = molgenis.Session(url=host, token=token)

#//////////////////////////////////////

# ~ 1 ~
# Pull data from the portal and combine
status_msg('Pulling data from the portal....')

codesSamples = dt.Frame(
    db.get(
        entity = 'cosasportal_samples',
        attributes='TEST_CODE,TEST_OMS',
        batch_size=10000
    )
)

codesArrayAdlas = dt.Frame(
    db.get(
        entity = 'cosasportal_labs_array_adlas',
        attributes='TEST_CODE,TEST_OMS',
        batch_size=10000
    )
)

codesArrayDarwin = dt.Frame(
    db.get(
        entity = 'cosasportal_labs_array_darwin',
        attributes='TestId'
    )
)

codesNgsAdlas = dt.Frame(
    db.get(
        entity = 'cosasportal_labs_ngs_adlas',
        attributes='TEST_CODE,TEST_OMS',
        batch_size=10000
    )
)

codesNgsDarwin = dt.Frame(
    db.get(
        entity = 'cosasportal_labs_ngs_darwin',
        attributes='TestId',
        batch_size=10000
    )
)

# remove _href column
del codesSamples['_href']
del codesArrayAdlas['_href']
del codesArrayDarwin['_href']
del codesNgsAdlas['_href']
del codesNgsDarwin['_href']

# import genetliclines emx
status_msg('Loading EMX from other projects....')
glines = dt.Frame(
    pd.read_excel(
        '_data/genticlines_EMX.xlsx',
        sheet_name = 'geneticlines_ADLAStest'
    ).replace({np.nan: None}).to_dict('records')
)[:, {
    'TEST_CODE': f.test_code,
    'TEST_OMS': f.test_description
}]

# import activeTestCodes dataset
status_msg('Loading active test codes list....')
activeTestCodes = dt.Frame(
    pd.read_excel('_data/testcodes_ngs_array.xlsx', sheet_name = 'Actieve Testcodes')
)[
    :, {'TEST_CODE': f.Testcode, 'TEST_OMS': f.Panel}
][:, first(f[:]), dt.by('TEST_CODE')]


# combine codes
status_msg('Preparing main code dataset....')
codes = dt.rbind(
    codesSamples[:, first(f[:]), dt.by('TEST_CODE')],
    codesArrayAdlas[:, first(f[:]), dt.by('TEST_CODE')],
    codesNgsAdlas[:, first(f[:]), dt.by('TEST_CODE')],
    dt.unique(codesArrayDarwin[:, {'TEST_CODE': f.TestId}]),
    dt.unique(codesNgsDarwin[:, {'TEST_CODE': f.TestId}]),
    glines,
    activeTestCodes,
    force=True
)[
    # reduce data to unique records only
    :, first(f[:]), dt.by('TEST_CODE')
][
    # rename columns
    :, {'code': f.TEST_CODE, 'description': f.TEST_OMS}
]

# merge gene lists
status_msg('Preparing gene lists....')
file = pd.ExcelFile('_data/testcodes_ngs_array.xlsx')
sheetnames = [d for d in file.sheet_names if d in codes['code'].to_list()[0]]

genes = dt.Frame()
for sheet in sheetnames:
    status_msg('Processing sheet: {}'.format(sheet))
    genes = dt.rbind(
        genes,
        dt.Frame()[:, {
            'code': sheet,
            'geneList': ','.join(
                sorted(
                    list(
                        pd.read_excel(
                            '_data/testcodes_ngs_array.xlsx',
                            sheet_name = sheet,
                            header = None,
                            index_col = False,
                            dtype = str
                        )[0]
                    )
                )
            )
        }]
    )

# merge gene list and write to file
status_msg('Join gene data with codes and saving....')
genes.key = 'code'
codes = codes[:, :, dt.join(genes)]
codes.to_csv('dist/umdm_labProcedures.csv')