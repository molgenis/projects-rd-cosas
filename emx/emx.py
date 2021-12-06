#'////////////////////////////////////////////////////////////////////////////
#' FILE: emx.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-10-05
#' MODIFIED: 2021-10-05
#' PURPOSE: generate emx files for COSAS
#' STATUS: working
#' PACKAGES: emxconvert
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

import sys
from yamlemxconvert import Convert
# from datatable import fread
import pandas as pd

# Jobs: the main jobs module is located here on GitHub (see 'jobs.xlsx')
# https://github.com/molgenis/rd-datamodel/tree/main/emx/dist
jobsModule = Convert(files = ['emx/src/jobs_results.yaml'])
jobsModule.convert()

# import pandas as pd
pd.DataFrame(jobsModule.attributes).to_csv('emx/dist/jobs_results_bamdata.csv', index = False)

# mcmd import -p emx/dist/jobs_results_bamdata.csv --as attributes --in jobs_results