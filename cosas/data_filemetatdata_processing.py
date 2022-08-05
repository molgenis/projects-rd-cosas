#'////////////////////////////////////////////////////////////////////////////
#' FILE: data_filemetatdata_processing.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-07-18
#' MODIFIED: 2022-07-28
#' PURPOSE: initial data processing
#' STATUS: experimental
#' PACKAGES: **see below**
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

from cosas.api.molgenis2 import Molgenis
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


def getFileType(value):
  if re.search(r'(vcf.gz(.tbi)?)|(.vcf)|(vcf.bgz.tbi)$', value):
    return 'vcf'
  elif re.search(r'.bam.cram$', value):
    return 'cram'
  elif re.search(r'.bam$', value):
    return 'bam'
  else:
    return None

#//////////////////////////////////////////////////////////////////////////////

# ~ 0 ~
# Processing and Import of Raw Data

# load file
portaldata = fread('~/Downloads/COSAS.txt')

# drop uncessary columns
del portaldata[:, ['id', 'testID', 'md5']]


# NOTE: The following steps are applied to speed up the testing and development
# of the filemetadata script. Cases that do not meet the following criteria
# should be reviewed before including in the main job.

# remove rows where the umcgID does not meet the expected format
portaldata['hasValidUmcgId'] = dt.Frame([
  re.search(r'^([0-9]{2,})', d) and not re.search(r'^([0]{1,})$', d)
  for d in portaldata[:, f.umcgID].to_list()[0]
])

# remove rows where the dnaID does not meet the expected format
portaldata['hasValidDnaId'] = dt.Frame([
  bool(re.search(r'^(DNA[0-9]{2,})$', d)) if bool(d) else False
  for d in portaldata[:, f.dnaID].to_list()[0]
])


# reduce data to valid umcg- and dna IDs only
portaldata = portaldata[(f.hasValidUmcgId) & (f.hasValidDnaId), :]
del portaldata[:, ['hasValidUmcgId', 'hasValidDnaId']]


cosas.delete('cosasportal_files')
cosas.importDatatableAsCsv('cosasportal_files', portaldata)

#//////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Mapping of Data into the COSAS
# Pull raw file metadata from cosasportal_files and import data into umdm_files

# ~ 1a ~
# pull file metadata and prep
# portaldata = dt.Frame(cosas.get('cosasportal_files', batch_size=10000))

for column in portaldata.names:
  if column in ['_href', 'id', 'familyID']:
    del portaldata[column]


portaldata['belongsToSample'] = dt.Frame([
  re.sub(r'^(DNA)', 'DNA-', d)
  for d in portaldata['dnaID'].to_list()[0]
])

portaldata['filepath'] = dt.Frame([
  re.sub(r'\/{2,}', '/', d)
  for d in portaldata['filepath'].to_list()[0]
])

portaldata['fileFormat'] = dt.Frame([
  getFileType(d)
  for d in portaldata['filename'].to_list()[0]
])

# dt.unique(portaldata['fileFormat'])
# portaldata[:, :, dt.sort(f.fileFormat, reverse=True)][:, (f.filename, f.fileFormat)]

portaldata['fileID'] = dt.Frame([
  ''.join(d)
  for d in portaldata[:, ['filepath', 'filename']].to_tuples()
])

if dt.unique(portaldata['fileID']).nrows != portaldata.nrows:
  raise SystemError('Number of unique file IDs must equal total possible rows')
  
# filedata['countOfDuplicates'] = dt.Frame([
#   filedata[f.fileID == d, :].nrows
#   for d in filedata['fileID'].to_list()[0]
# ])

# ~ 1b ~
# get a list of all current patient identifiers (i.e., UmcgNr)
patients = dt.Frame(cosas.get('umdm_subjects', attributes='subjectID', batch_size=10000))
patientIDs = patients['subjectID'].to_list()[0]

# ~ 1c ~
# get a list of all current sample identifiers (i.e., dnaNr)
samples = dt.Frame(cosas.get('umdm_samples', attributes='sampleID', batch_size=10000))
sampleIDs = samples['sampleID'].to_list()[0]

# ~ 1d ~
# Compute coverage of identifiers

portaldata['patientIdExists'] = dt.Frame([
  d in patientIDs
  for d in portaldata['umcgID'].to_list()[0]
])

portaldata['sampleIdExists'] = dt.Frame([
  d in sampleIDs
  for d in portaldata['belongsToSample'].to_list()[0]
])

# portaldata[:, dt.count(), dt.by(f.sampleIdExists)]
portaldata[:, dt.count(), dt.by(f.patientIdExists)]
portaldata[:, dt.count(), dt.by(f.patientIdExists, f.sampleIdExists)]
portaldata[f.patientIdExists & f.sampleIdExists==False, :]

# ~ 0d ~ 
# Subset date for records that have a valid subject- and sample identifier

# umdm_files = portaldata[(f.patientIdExists) & (f.sampleIdExists), :]
umdm_files = portaldata[(f.patientIdExists), :]

umdm_files[:, dt.count(), dt.by(f.patientIdExists, f.sampleIdExists)]
del umdm_files[:, ['dnaID', 'patientIdExists', 'sampleIdExists', 'filetype']]

# rename columns
umdm_files.names = {
  'umcgID': 'belongsToSubject',
  'filename': 'fileName',
  'filepath': 'filePath',
  'dateCreated': 'dateFileCreated'
}

umdm_files['dateRecordCreated'] = datetime.now(tz=pytz.timezone('Europe/Amsterdam')).strftime('%Y-%m-%dT%H:%M:%SZ')
umdm_files['recordCreatedBy'] = 'cosasbot'

# import
# cosas.delete('umdm_files')
cosas.importDatatableAsCsv(pkg_entity = 'umdm_files', data = umdm_files)
