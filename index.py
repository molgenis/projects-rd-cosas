#'////////////////////////////////////////////////////////////////////////////
#' FILE: emx.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-10-05
#' MODIFIED: 2022-02-17
#' PURPOSE: generate emx files for COSAS
#' STATUS: working
#' PACKAGES: emxconvert
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

from yamlemxconvert import Convert
from src.python.utils_emx import buildEmxTags

# render umdm portal
cosas = Convert(files = ['src/emx/cosas_portal.yaml'])
cosas.convert()
cosas.write('cosasportal', format='xlsx', outDir='dist')
cosas.write_schema(path = 'dist/schema_cosasportal.md')


# render reports emx
reports = Convert(files = ['src/emx/cosasreports.yaml'])
reports.convert()

# build tags
tags = reports.tags
tags.extend(buildEmxTags(reports.packages))
tags.extend(buildEmxTags(reports.entities))
tags.extend(buildEmxTags(reports.attributes))
tags = list({d['identifier']: d for d in tags}.values())
reports.tags = sorted(tags, key = lambda d: d['identifier'])

# write
reports.write('cosasreports', format='xlsx', outDir='dist')
reports.write_schema(path='dist/schema_cosasreports.md')

# Jobs: the main jobs module is located here on GitHub (see 'jobs.xlsx')
# https://github.com/molgenis/rd-datamodel/tree/main/emx/dist
# jobsModule = Convert(files = ['emx/src/jobs_results.yaml'])
# jobsModule.convert()
# pd.DataFrame(jobsModule.attributes).to_csv('emx/dist/jobs_results_bamdata.csv', index = False)

# mcmd import -p emx/dist/jobs_results_bamdata.csv --as attributes --in jobs_results

#//////////////////////////////////////

# ~ 1 ~ 
# Tests

# from src.python.emx2_client import Molgenis
# from dotenv import load_dotenv
# from os import environ

# import pandas as pd

# load_dotenv()

# host = environ['EMX2_HOST']
# database = environ['EMX2_DB_PRIMARY']

# db = Molgenis(url = host, database = database)
# db.signin(email=environ['EMX2_USERNAME'],password=environ['EMX2_PASSWORD'])

# data = pd.read_csv('dist/cosas_organizations.csv').to_csv(index=False)
# db.importData(table = 'organizations', data = data)
# db.importCsvFile(table ='organizations', filename='dist/cosas_organizations.csv')
