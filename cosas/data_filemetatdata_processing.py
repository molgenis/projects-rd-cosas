#'////////////////////////////////////////////////////////////////////////////
#' FILE: data_filemetatdata_processing.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-07-18
#' MODIFIED: 2022-07-18
#' PURPOSE: initial data processing
#' STATUS: experimental
#' PACKAGES: **see below**
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

from cosas.api.molgenis_emx1_client import Molgenis
from dotenv import load_dotenv
from os import environ
from datatable import dt, f, fread
import re

# connect to cosas-db
load_dotenv()
host = environ['MOLGENIS_ACC_HOST']
cosas = Molgenis(host)
cosas.login(environ['MOLGENIS_ACC_USR'], environ['MOLGENIS_ACC_PWD'])


# load file
filedata = fread('~/Downloads/COSAS.txt')

# drop uncessary columns
del filedata[:, ['id', 'testID', 'md5']]


# NOTE: The following steps are applied to speed up the testing and development
# of the filemetadata script. Cases that do not meet the following criteria
# should be reviewed before including in the main job.

# remove rows where the umcgID does not meet the expected format
filedata['hasValidUmcgId'] = dt.Frame([
  re.search(r'^([0-9]{2,})', d) and not re.search(r'^([0]{1,})$', d)
  for d in filedata[:, f.umcgID].to_list()[0]
])

# remove rows where the dnaID does not meet the expected format
filedata['hasValidDnaId'] = dt.Frame([
  bool(re.search(r'^(DNA[0-9]{2,})$', d)) if bool(d) else False
  for d in filedata[:, f.dnaID].to_list()[0]
])


# reduce data to valid umcg- and dna IDs only
finalData = filedata[(f.hasValidUmcgId) & (f.hasValidDnaId), :]
del finalData[:, ['hasValidUmcgId', 'hasValidDnaId']]


cosas.importDatatableAsCsv('cosasportal_files', finalData, 'cosasportal_files')