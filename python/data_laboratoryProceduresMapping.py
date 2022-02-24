#'////////////////////////////////////////////////////////////////////////////
#' FILE: mappings_cosasrefs.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-10-07
#' MODIFIED: 2022-02-24
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
from os import environ
import pandas as pd

load_dotenv()
host = environ['MOLGENIS_HOST_ACC']
token = environ['MOLGENIS_TOKEN_ACC']

db = molgenis(url=host, token=token)

#//////////////////////////////////////

# ~ 1 ~
# Pull data from the portal and combine

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

# process objects
del codesSamples['_href']
del codesArrayAdlas['_href']
del codesArrayDarwin['_href']
del codesNgsAdlas['_href']
del codesNgsDarwin['_href']


# combine codes
codes = dt.rbind(
    codesSamples[:, first(f[:]), dt.by('TEST_CODE')],
    codesArrayAdlas[:, first(f[:]), dt.by('TEST_CODE')],
    codesNgsAdlas[:, first(f[:]), dt.by('TEST_CODE')],
    dt.unique(codesArrayDarwin[:, {'TEST_CODE': f.TestId}]),
    dt.unique(codesNgsDarwin[:, {'TEST_CODE': f.TestId}]),
    force=True
)[
    # reduce data to unique records only
    :, first(f[:]), dt.by('TEST_CODE')
][
    # rename columns
    :, {'code': f.TEST_CODE, 'description': f.TEST_OMS}
]


# load datasets
# glines = dt.Frame(
#     pd.read_excel(
#         '_raw/geneticlines2021-03-10_15_52_37.366.xlsx',
#         sheet_name = 'geneticlines_ADLAStest'
#     ).to_dict('records')
# )[:, {
#     'code': f.TEST_CODE,
#     'description': f.label,
#     'category': f.panel,
#     'subcategory': f.labelPanel
# }]

# # recode panel (remove: nan)
# glines['category'] = dt.Frame([
#     d if str(d) != 'nan' else None for d in glines['category'].to_list()[0]
# ])

# set key for merge
# glines.key = 'code'

# # Bind columns of interest from selected datasets
# testCodes = dt.rbind(
#     # load samples data
#     dt.Frame(pd.read_excel('_raw/cosasportal_samples.xlsx'))[
#         :, {'code': f.TEST_CODE, 'description': f.TEST_OMS}
#     ],
#     # array data
#     dt.Frame(pd.read_excel('_raw/cosasportal_array_adlas.xlsx'))[
#         :, {'code': f.TEST_CODE, 'description': f.TEST_OMS}
#     ],
#     # ngs data
#     dt.Frame(pd.read_excel('_raw/cosasportal_ngs_adlas.xlsx'))[
#         :, {'code': f.TEST_CODE, 'description': f.TEST_OMS}
#     ]
# )[
#     # sort dataset  by code
#     :, :, dt.sort(f.code)
# ][
#     # grab distinct rows by code
#     :, first(f[1:]), dt.by(f.code)
# ]

# # join geneticlines lookup table
# testCodes = testCodes[:, :, dt.join(glines)]


# merge data genelists by testcode
# file = pd.ExcelFile('_raw/testcodes_ngs_array.xlsx')
# sheetnames = list(filter(lambda x: x in testCodes['code'].to_list()[0], file.sheet_names))
# genes = dt.Frame()
# for sheet in sheetnames:
#     print('Processing sheet: ', sheet)
#     genes = dt.rbind(
#         genes,
#         dt.Frame()[:, {
#             'code': sheet,
#             'geneList': ','.join(
#                 sorted(
#                     list(
#                         pd.read_excel(
#                             '_raw/testcodes_ngs_array.xlsx',
#                             sheet_name = sheet,
#                             header = None,
#                             index_col = False,
#                             dtype = str
#                         )[0]
#                     )
#                 )
#             )
#         }]
#     )

# # merge gene list and write to file
# genes.key = 'code'
# testCodes = testCodes[
#     :, :, dt.join(genes)
# ][
#     :, (f.code, f.description, f.category, f.subcategory, f.geneList)
# ]

# testCodes.to_csv('emx/lookups/cosasrefs_laboratoryProcedures.csv')