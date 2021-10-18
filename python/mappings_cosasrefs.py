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

#' @title Generate Data for Diagnostic Reference Entity
#' @description  Create reference entity `cosasrefs_diagnoses`
#' @section Methodology:
#'
#' Using the portal table `cosasrefs_diagnoses`, we need to genereate a list
#' of distinct diganostic codes and definitions. Diagnoses are split into
#' two columns: HOOFDDIAGNOSE and EXTRA_DIAGNOSE. The following code will do
#' the following.
#'
#' 1) bind HOOFDDIAGNOSE and EXTRA_DIAGNOSE
#' 2) remove missing values (i.e., "-")
#' 3) separate diagnostic code and description
#' 4) create new diagnostic ID using diagnostic code
#'

# Load Datasets
# In order to build the diagnostic table, we need to pull
# data from the HPO, sorta mappings, and clinical files
phenotype = fread(file = 'emx/lookups/hpo_release_v2021-08-02.csv')
sorta = fread(file = 'emx/lookups/sorta_cineas_hpo_mappings.csv')[
    :, {
        'description': f.Name,
        'ontologyTermIRI': f.ontologyTermIRI,
        'score': f.score
    }
]


raw_clinical = dt.Frame(
    pd.read_excel('_raw/cosasportal_diagnoses.xlsx')
)[:, (f.HOOFDDIAGNOSE, f.EXTRA_DIAGNOSE)]


# not HPO codes
sorta['flagged'] = dt.Frame([
    True if re.search('obo/HP_', d) else False for d in sorta['ontologyTermIRI'].to_list()[0]
])


# Recode HPO IRIs as HPO codes
sorta['hpo'] = dt.Frame([
    d.replace(
        'http://purl.obolibrary.org/obo/HP_', 'HP:'
    ) for d in sorta['ontologyTermIRI'].to_list()[0]
])


# create flag for HPO codes that aren't in the HPO codeset
hpoCodes = phenotype['code'].to_list()[0]
sorta['hpoFlag'] = dt.Frame([
    True if d in hpoCodes else False for d in sorta['hpo'].to_list()[0]
])

# filter dataset and remove columns
sorta = sorta[(f.score >= 70) & (f.flagged == 1) & (f.hpoFlag == 1), :]
del sorta[:, ['ontologyTermIRI', 'score', 'flagged', 'hpoFlag']]


# create diagnoses reference entity
diagnoses = dt.rbind(
    raw_clinical[:, {'description': f.HOOFDDIAGNOSE}],
    raw_clinical[:, {'description': f.EXTRA_DIAGNOSE}],
)[f.description != '-', :]

diagnoses['code'] = dt.Frame([
    d.split(':')[0].strip() for d in diagnoses['description'].to_list()[0]
])

diagnoses['description'] = dt.Frame([
    d.split(':')[1].strip() for d in diagnoses['description'].to_list()[0]
])

diagnoses['codesystem'] = dt.Frame([
    'cineas' for d in diagnoses['description'].to_list()[0] 
])


# join sort and diagnoses datasets and prep for import
sorta.key = 'description'
diagnoses = diagnoses[
    :, :, dt.join(sorta)
][
    :, (f.code, f.description, f.codesystem, f.hpo)
][
    :, first(f[1:]), dt.by(f.code)
][:, :, dt.sort(as_type(f.code, int))]

# write to file
diagnoses.to_csv('emx/lookups/cosasrefs_diagnoses.csv')

#//////////////////////////////////////////////////////////////////////////////

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