#'////////////////////////////////////////////////////////////////////////////
#' FILE: cosasrefs_create.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-07-08
#' MODIFIED: 2021-07-09
#' PURPOSE: Initial script for creating reference entities
#' STATUS: working
#' PACKAGES: NA
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

import python.utils_cosas as cosastools
import pandas as pd
import re

config = cosastools.load_yaml_config('molgenis_config.yml')

# read data from excel
def excel_to_list(path):
    data = pd.read_excel(path, engine = 'openpyxl')
    return data.to_dict('records')


# init session
cosas = cosastools.molgenis(
    url = config['hosts']['acc'],
    token = config['tokens']['acc']
)


#//////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Create reference entities for Diagnostic data
# This includes:
#   - cosasrefs_diagnostic_certainty
#   - cosasrefs_diagnoses
#
dx = excel_to_list(path = 'data/3) Diagnoses_2.xlsx')


# ~ 1a ~
# Create dataset for `cosasrefs_diagnoses`

# Combine all values into and remove values that == "-"
raw = []
for d in dx:
    dx1 = d.get('HOOFDDIAGNOSE').lower()
    dx2 = d.get('EXTRA_DIAGNOSE').lower()
    if dx1 != '-':
        raw.append(dx1)
    if dx2 != '-':
        raw.append(dx2)

del d, dx1, dx2

# Find distinct cases only
diagnoses = list(set(raw))
len(diagnoses)

# Create dataset
dx_data = []
for d in diagnoses:
    if re.match(r'^([0-9]{1,}:)', d):
        row = d.split(':')
        dx_data.append({
            'id': int(row[0]), 
            'cineas_code': row[0],
            'cineas_description': row[1]
        })

del d

dx_data = sorted(dx_data, key = lambda x: x['id'])
for d in dx_data:
    d['id'] = 'dx_' + str(d['id'])

# upload
# cosas.delete('cosasrefs_diagnoses')
cosas.add_all(
    entity = 'cosasrefs_diagnoses',
    entities = dx_data
)

del diagnoses,raw, d, row, dx_data

#//////////////////////////////////////

# ~1b ~
# create values for `cosasrefs_diagnostic_certainty`
options = list(
    set(
        cosastools.attr_flatten(
            data = dx,
            attr = 'HOOFDDIAGNOSE_ZEKERHEID',
            distinct = True
        ) + cosastools.attr_flatten(
                data = dx,
                attr = 'EXTRA_DIAGNOSE_ZEKERHEID',
                distinct = True
            )
        )
    )

options.sort()
certainty_options = []
for opt in options:
    if opt != '-':
        certainty_options.append({
            'id': opt.replace(' ', '-').lower(),
            'certainty': opt
        })

certainty_options

# upload
# cosas.delete('cosasrefs_diagnostic_certainty')
cosas.add_all(
    entity = 'cosasrefs_diagnostic_certainty',
    entities = certainty_options
)


del options, certainty_options, opt, dx

#//////////////////////////////////////////////////////////////////////////////

# ~ 2 ~
# Process Samples File

samples = excel_to_list(path = 'data/4) Monster- en adviesvraag-data_3.xlsx')

# Create reference entity for `cosasrefs_condition_codes`
codes = cosastools.attr_flatten(
    data = samples,
    attr = 'AANDOENING_CODE',
    distinct = True
)

# build data
data = []
for code in codes:
    data.append({'id': code.lower(), 'name': code})

data = sorted(data, key = lambda x: x['id'])

# upload + cleanup
cosas.add_all(entity = 'cosasrefs_condition_codes', entities = data)

del codes, data, code

#//////////////////////////////////////

# ~ 2b ~
# create reference entity for `cosasrefs_material_types`

# extract attributes and standarize values
raw_types = cosastools.dict_select(data = samples, keys = 'MATERIAAL')
for r in raw_types:
    r['type'] = r.get('MATERIAAL').lower().replace(' ', '-')

# find distinct values
types = cosastools.attr_flatten(
    data = raw_types,
    attr = 'type',
    distinct = True
)

# build dataset
material_types = []
for t in types:
    material_types.append({
        'id': t,
        'material': t.replace('-', ' ').capitalize() # reset values
    })

material_types = sorted(material_types, key = lambda x: x['id'])

# upload
cosas.add_all(entity = 'cosasrefs_material_types', entities = material_types)

del material_types, r, raw_types, t, types

#//////////////////////////////////////

# ~ 2c ~
# Create Initial Testcodes dataset


# first, pull all codes and description
raw_testcodes = cosastools.dict_select(
    data = samples,
    keys = ['TEST_CODE', 'TEST_OMS']
)

# and then find distinct entries
testcodes = cosastools.dict_unique(
    data = raw_testcodes,
    key = 'TEST_CODE'
)

# sort and map to COSAS EMX
testcodes = sorted(testcodes, key = lambda x: x['TEST_CODE'])
for t in testcodes:
    t['id'] = t.get('TEST_CODE').lower()
    t['code'] = t.pop('TEST_CODE')
    t['description'] = t.pop('TEST_OMS')

# upload and cleanup
cosas.add_all(entity = 'cosasrefs_test_codes', entities = testcodes)
del raw_testcodes, testcodes, t
del samples

#//////////////////////////////////////

# ~ 3 ~
# Build Lab Indications

# load files (indications is spread across two files)
adlas_arr = excel_to_list(path = 'data/6) Darwin array (CNV)-data_2.xlsx')
adlas_ngs = excel_to_list(path = 'data/8) Darwin NGS-data_2.xlsx')

indications = list(
    set(
        cosastools.attr_flatten(
            data = adlas_arr,
            attr = 'Indicatie',
            distinct = True
        ) +
        cosastools.attr_flatten(
            data = adlas_ngs,
            attr = 'Indicatie',
            distinct = True
        )
    )
)

# build dataset
indications.sort()
data = []
for i in indications:
    data.append({
        'id': i.replace(' ', '-').lower(),
        'indication': i
    })

# upload + cleanup
cosas.add_all(entity = 'cosasrefs_lab_indications', entities = data)
del adlas_ngs, adlas_arr, indications, i, data
