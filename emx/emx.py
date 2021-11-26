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

# get arg if running via the command line
input = sys.argv[1]
print('Selection: {}'.format(input))


# build emx for `cosas` and `cosasrefs`
if input == 'cosas':

    try:
        cosas = Convert(
            files = [
                'emx/src/cosasrefs.yaml',
                'emx/src/cosas.yaml'
            ]
        )

        cosas.convert()
        
        # Append Phenotype
        # source comes from https://github.com/molgenis/rd-datamodel/
        # curl file and adjust file path if necessary
        cosas.data.update({
            'cosasrefs_phenotype': pd.read_csv(
                'emx/lookups/hpo_release_v2021-08-02.csv'
            ).to_dict('records')
        })
        
        # Append Internal Phenotypic codeset
        cosas.data.update({
            'cosasrefs_diagnoses': pd.read_csv(
                'emx/lookups/cosasrefs_diagnoses.csv'
            ).to_dict('records')
        })
        
        # Append Internal testCodes
        cosas.data.update({
            'cosasrefs_testCodes': pd.read_csv(
                'emx/lookups/cosasrefs_testCodes.csv'
            ).to_dict('records')
        })
        
        # write model
        cosas.write(name = 'cosas', format = 'xlsx', outDir = 'emx/dist/')
        cosas.write_schema(path = 'emx/dist/cosas.md')
        print('Built cosas EMX `emx/dist/cosas.xlsx`')
    except:
        SystemError(
            'Unable to convert emx:\n{}'
            .format(str(sys.exc_info()[0]))
        )

# build emx for `cosasportal`
if input == 'cosasportal':
    try:
        portal = Convert(files = ['emx/src/cosasportal.yaml'])
        portal.convert()
        portal.write(name = 'cosasportal', format = 'xlsx', outDir = 'emx/dist/')
        print('Built cosasportal `emx/dist/cosasportal.xslx`')
    except:
        SystemError(
            'Unable to convert emx:\n{}'
            .format(str(sys.exc_info()[0]))
        )


#//////////////////////////////////////////////////////////////////////////////

# Additional EMX Modules

# Jobs: the main jobs module is located here on GitHub (see 'jobs.xlsx')
# https://github.com/molgenis/rd-datamodel/tree/main/emx/dist
jobsModule = Convert(files = ['emx/src/jobs_results.yaml'])
jobsModule.convert()

# import pandas as pd
pd.DataFrame(jobsModule.attributes).to_csv('emx/dist/jobs_results_bamdata.csv', index = False)

# mcmd import -p emx/dist/jobs_results_bamdata.csv --as attributes --in jobs_results