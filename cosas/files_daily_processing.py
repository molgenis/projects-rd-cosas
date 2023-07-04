#///////////////////////////////////////////////////////////////////////////////
# FILE: files_daily_processing.py
# AUTHOR: David Ruvolo
# CREATED: 2023-07-04
# MODIFIED: 2023-07-04
# PURPOSE: script for daily processing of file metadata 
# STATUS: in.progress
# PACKAGES: **see below**
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from cosastools.molgenis import Molgenis, print2, now
from datatable import dt, f
import re

def getFileType(value): 
  if re.search(r'(vcf.gz(.tbi)?)|(.vcf)|(vcf.bgz.tbi)$', value):
    value = 'vcf'
  elif re.search(r'.bam.cram$', value):
    value = 'cram'
  elif re.search(r'.bam$', value):
    value = 'bam'
  elif re.search(r'.fq.gz$', value):
    value = 'fastq'
  else:
    value = None
  return value

#///////////////////////////////////////////////////////////////////////////////

# ~ 0 ~
# Connect and retrieve metadata

# ~ LOCAL DEV ~
# from dotenv import load_dotenv
# from os import environ
# load_dotenv()
# cosas = Molgenis(environ['MOLGENIS_ACC_HOST'])
# cosas.login(environ['MOLGENIS_ACC_USR'], environ['MOLGENIS_ACC_PWD'])

# ~ PROD ~
cosas = Molgenis('http://localhost/api/', token='${molgenisToken}')


# retrieve raw file metadata
portaldata = dt.Frame(cosas.get('cosasportal_files',batch_size=10000))
del portaldata['_href']

# get list of existing patient IDs
patientsDT = dt.Frame(
  cosas.get(
    'umdm_subjects',
    attributes='subjectID',
    batch_size=10000
  )
)

patientIDs = patientsDT['subjectID'].to_list()[0]

#///////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Map file metadata into the COSAS

# ~ 1a ~
# pull file metadata and prep
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

umdm_files['dateRecordCreated'] = now()
umdm_files['recordCreatedBy'] = 'cosasbot'

# import
# cosas.delete('umdm_files')
cosas.importDatatableAsCsv(pkg_entity = 'umdm_files', data = umdm_files)
