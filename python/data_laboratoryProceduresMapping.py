#'////////////////////////////////////////////////////////////////////////////
#' FILE: mappings_cosasrefs.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-10-07
#' MODIFIED: 2021-10-07
#' PURPOSE: cosas reference entities mappings
#' STATUS: in.progress
#' PACKAGES: datatable
#' COMMENTS: This script should be run only if there are major updates or
#'  if the database needs to be rebuilt. This is script is designed to be run
#'  once. If new entries need to be added, then handle them independently.
#'////////////////////////////////////////////////////////////////////////////

import pandas as pd
from datatable import dt, f, fread, as_type, first
import re

# @title COSAS Test Codes Reference Entity
# @description create cosasrefs_testCodes
# @section Methodology:
#
# Most of the test metadata comes from the samples dataset. However,
# there may be some extra cases in the ADLAS and Darwin extracts.

# load datasets
glines = dt.Frame(
    pd.read_excel(
        '_raw/geneticlines2021-03-10_15_52_37.366.xlsx',
        sheet_name = 'geneticlines_ADLAStest'
    ).to_dict('records')
)[:, {
    'code': f.TEST_CODE,
    'label': f.label,
    'panel': f.panel,
    'labelPanel': f.labelPanel
}]

# recode panel (remove: nan)
glines['panel'] = dt.Frame([
    d if str(d) != 'nan' else None for d in glines['panel'].to_list()[0]
])

# set key for merge
glines.key = 'code'

# Bind columns of interest from selected datasets
testCodes = dt.rbind(
    # load samples data
    dt.Frame(pd.read_excel('_raw/cosasportal_samples.xlsx'))[
        :, {'code': f.TEST_CODE, 'description': f.TEST_OMS}
    ],
    # array data
    dt.Frame(pd.read_excel('_raw/cosasportal_array_adlas.xlsx'))[
        :, {'code': f.TEST_CODE, 'description': f.TEST_OMS}
    ],
    # ngs data
    dt.Frame(pd.read_excel('_raw/cosasportal_ngs_adlas.xlsx'))[
        :, {'code': f.TEST_CODE, 'description': f.TEST_OMS}
    ]
)[
    # sort dataset  by code
    :, :, dt.sort(f.code)
][
    # grab distinct rows by code
    :, first(f[1:]), dt.by(f.code)
]

# join geneticlines lookup table
testCodes = testCodes[:, :, dt.join(glines)]


# merge data genelists by testcode
file = pd.ExcelFile('_raw/testcodes_ngs_array.xlsx')
sheetnames = list(filter(lambda x: x in testCodes['code'].to_list()[0], file.sheet_names))
genes = dt.Frame()
for sheet in sheetnames:
    print('Processing sheet: ', sheet)
    genes = dt.rbind(
        genes,
        dt.Frame()[:, {
            'code': sheet,
            'genes': ','.join(
                sorted(
                    list(
                        pd.read_excel(
                            '_raw/testcodes_ngs_array.xlsx',
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
genes.key = 'code'

testCodes['id'] = dt.Frame([
    d.lower() for d in testCodes['code'].to_list()[0]
])

testCodes = testCodes[
    :, :, dt.join(genes)
][
    :, (f.id, f.code, f.description, f.panel, f.labelPanel, f.genes)
]

testCodes.to_csv('emx/lookups/cosasrefs_testCodes.csv')