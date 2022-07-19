#'////////////////////////////////////////////////////////////////////////////
#' FILE: data_filemetatdata_processing.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-07-18
#' MODIFIED: 2022-07-19
#' PURPOSE: initial data processing
#' STATUS: experimental
#' PACKAGES: **see below**
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

from cosas.api.molgenis_emx1_client import Molgenis
from datetime import datetime
import pytz
from dotenv import load_dotenv
from os import environ
from datatable import dt, f, fread
import re

# connect to cosas-db
load_dotenv()
host = environ['MOLGENIS_ACC_HOST']
cosas = Molgenis(host)
cosas.login(environ['MOLGENIS_ACC_USR'], environ['MOLGENIS_ACC_PWD'])

#//////////////////////////////////////////////////////////////////////////////

# ~ 0 ~
# Processing and Import of Raw Data

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

#//////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Mapping of Data into the COSAS
# Pull raw file metadata from cosasportal_files and import data into umdm_files

# ~ 1a ~
# pull file metadata and prep
filedata = dt.Frame(cosas.get('cosasportal_files', batch_size=10000))
del filedata[:, ['_href', 'id', 'familyID']]


filedata['belongsToSample'] = dt.Frame([
  re.sub(r'^(DNA)', 'DNA-', d)
  for d in filedata['dnaID'].to_list()[0]
])

filedata['filepath'] = dt.Frame([
  re.sub(r'\/{2,}', '/', d)
  for d in filedata['filepath'].to_list()[0]
])

filedata['fileFormat'] = dt.Frame([
  'gVCF' if re.search(r'(.vcf.gz)$', d) else d
  for d in filedata['filename'].to_list()[0]
])

# ~ 1b ~
# get a list of all current patient identifiers (i.e., UmcgNr)
patients = dt.Frame(cosas.get(
  entity = 'umdm_subjects',
  attributes = 'subjectID',
  batch_size=10000
))

patientIDs = patients['subjectID'].to_list()[0]

# ~ 1c ~
# get a list of all current sample identifiers (i.e., dnaNr)
samples = dt.Frame(
  cosas.get(
    entity = 'umdm_samples',
    attributes = 'sampleID',
    batch_size = 10000
  )
)

sampleIDs = samples['sampleID'].to_list()[0]


# ~ 1d ~
# Compute coverage of identifiers

filedata['patientIdExists'] = dt.Frame([
  d in patientIDs
  for d in filedata['umcgID'].to_list()[0]
])

filedata['sampleIdExists'] = dt.Frame([
  d in sampleIDs
  for d in filedata['belongsToSample'].to_list()[0]
])

filedata[:, dt.count(), dt.by(f.patientIdExists)]
filedata[:, dt.count(), dt.by(f.sampleIdExists)]
filedata[:, dt.count(), dt.by(f.patientIdExists, f.sampleIdExists)]

# ~ 0d ~ 
# Subset date for records that have a valid subject- and sample identifier

umdm_files = filedata[(f.patientIdExists) & (f.sampleIdExists), :]

umdm_files[:, dt.count(), dt.by(f.patientIdExists, f.sampleIdExists)]
del umdm_files[:, ['dnaID', 'patientIdExists', 'sampleIdExists', 'filetype']]

# rename columns
umdm_files.names = {
  'umcgID': 'belongsToSubject',
  'filepath': 'filePath',
  'dateCreated': 'dateFileCreated'
}

umdm_files['dateRecordCreated'] = datetime.now(tz=pytz.timezone('Europe/Amsterdam')).strftime('%Y-%m-%dT%H:%M:%SZ')
umdm_files['recordCreatedBy'] = 'cosasbot'

# import
cosas.importDatatableAsCsv(pkg_entity = 'umdm_files', data = umdm_files)
