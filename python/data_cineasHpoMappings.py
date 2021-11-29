#'////////////////////////////////////////////////////////////////////////////
#' FILE: data_cineas_to_hpo.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-11-29
#' MODIFIED: 2021-11-29
#' PURPOSE: Produce Cineas to HPO mapping table for new data processing
#' STATUS: stable
#' PACKAGES: pandas, datatable, re
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

import pandas as pd
from datatable import dt, f, fread, as_type, first
import re

#' Generate Data for CINEAS to HPO Mappings
#' @description Mapping script for generating a CINEAS code to HPO code dataset
#' @section Methodology:
#'
#' Using the portal table `cosasportal_diagnoses`, we need to genereate a list
#' of distinct diganostic codes and definitions. Diagnoses are split into
#' two columns: HOOFDDIAGNOSE and EXTRA_DIAGNOSE. The following code will do
#' the following.
#'
#' 1) bind HOOFDDIAGNOSE and EXTRA_DIAGNOSE
#' 2) remove missing values (i.e., "-")
#' 3) split diagnostic code and description
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

diagnoses[:,['value','code']] = dt.Frame([
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
    :, (f.value, f.description, f.codesystem, f.code, f.hpo)
][
    :, first(f[1:]), dt.by(f.value)
][:, :, dt.sort(as_type(f.value, int))]

# write to file
diagnoses.to_csv('emx/lookups/cosasrefs_cineasHpoMappings.csv')