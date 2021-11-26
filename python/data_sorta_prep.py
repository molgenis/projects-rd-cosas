#'////////////////////////////////////////////////////////////////////////////
#' FILE: data_sorta_prep.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-11-08
#' MODIFIED: 2021-11-08
#' PURPOSE: prep data for SORTA
#' STATUS: in.progress
#' PACKAGES: NA
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

import pandas as pd
from datatable import dt, f
import re

raw_clinical = dt.Frame(
    pd.read_excel('_raw/cosasportal_diagnoses.xlsx')
)[:, (f.HOOFDDIAGNOSE, f.EXTRA_DIAGNOSE)]


diagnoses = dt.rbind(
    raw_clinical[:, {'description': f.HOOFDDIAGNOSE}],
    raw_clinical[:, {'description': f.EXTRA_DIAGNOSE}],
)[f.description != '-', :]

diagnoses['description'] = dt.Frame([
    d.split(':')[1].strip() for d in diagnoses['description'].to_list()[0]
])

data = dt.unique(diagnoses).to_pandas().rename(columns = {'description': 'Name'})
data.to_csv('data/cineas_codes.txt',sep=';',index=False)