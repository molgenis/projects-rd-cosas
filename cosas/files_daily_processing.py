#///////////////////////////////////////////////////////////////////////////////
# FILE: files_daily_processing.py
# AUTHOR: David Ruvolo
# CREATED: 2023-07-04
# MODIFIED: 2023-07-04
# PURPOSE: script for daily processing of file metadata 
# STATUS: stable
# PACKAGES: **see below**
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from cosastools.molgenis import Molgenis, print2
from datatable import dt, f
from datetime import datetime
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
print2('Connecting to molgenis....')

# ~ LOCAL DEV ~
# from dotenv import load_dotenv
# from os import environ
# load_dotenv()
# cosas = Molgenis(environ['MOLGENIS_ACC_HOST'])
# cosas.login(environ['MOLGENIS_ACC_USR'], environ['MOLGENIS_ACC_PWD'])

# ~ PROD ~
cosas = Molgenis('http://localhost/api/', token='${molgenisToken}')

#///////////////////////////////////////

# ~ 0b ~
# Retrieve file and patients data
print2('Retrieving metadata....')

portaldata = dt.Frame(cosas.get('cosasportal_files',batch_size=10000))
del portaldata['_href']

# get patient IDs
patientIDs = dt.Frame(
  cosas.get(
    'umdm_subjects',
    attributes='subjectID',
    batch_size=10000
  )
)['subjectID'].to_list()[0]


# get sample IDs
sampleIDs = dt.Frame(
  cosas.get(
    'umdm_samples',
    attributes='sampleID',
    batch_size=10000
  )
)['sampleID'].to_list()[0]

#///////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Map file metadata into the COSAS
print2('Preparing file metadata...')

# pull file metadata and prep
for column in portaldata.names:
  if column in ['_href', 'id', 'familyID']:
    del portaldata[column]


# format dna nummer
print2('Formatting DNAnr....')
portaldata['belongsToSample'] = dt.Frame([
  re.sub(r'^(DNA)', 'DNA-', d)
  for d in portaldata['dnaID'].to_list()[0]
])

# recode missing or blank file names
print2('Recoding missing filenames....')
portaldata['filename'] = dt.Frame([
  None if value == 'N/A' else value
  for value in portaldata['filename'].to_list()[0]
])

# remove instances of 2 or more slashes
print2('Formatting filepaths....')
portaldata['filepath'] = dt.Frame([
  re.sub(r'\/{2,}', '/', d)
  for d in portaldata['filepath'].to_list()[0]
])

# recode file formats
# portaldata[:, dt.count(), dt.by(f.fileFormat)]
print2('Recoding file format....')
portaldata['fileFormat'] = dt.Frame([
  getFileType(value) if value else value
  for value in portaldata['filename'].to_list()[0]
])


# create file identifier
print2('Generating table identifiers')
portaldata['fileID'] = dt.Frame([
  ''.join(row) if all(row) else None
  for row in portaldata[:, ['filepath', 'filename']].to_tuples()
])

# drop empty rows
print2('Removing records where a file ID cannot be created....')
print2(f"Current row count: {portaldata.nrows}")

portaldata = portaldata[f.fileID !=None,:]

print2(f"New row count: {portaldata.nrows}")

# make sure there are unique rows
if dt.unique(portaldata['fileID']).nrows != portaldata.nrows:
  raise SystemError('Number of unique file IDs must equal total possible rows')

#///////////////////////////////////////////////////////////////////////////////

# ~ 2 ~
# Create umdm_files

# ~ 2a ~
# Validate identifiers

# check incoming patient IDs
print2('Validating incoming patientIDs....')
portaldata['patientIdExists'] = dt.Frame([
  value in patientIDs for value in portaldata['umcgID'].to_list()[0]
])

# check incoming sample IDs
print2('Validating incoming sampleIDs....')
portaldata['sampleIdExists'] = dt.Frame([
  value in sampleIDs for value in portaldata['belongsToSample'].to_list()[0]
])

#///////////////////////////////////////
 
# ~ 2b ~ 
# Subset date for records that have a valid subject- and sample identifier
print2('Filtering dataset to rows with valid patient- and sample IDs....')

umdm_files = portaldata[(f.patientIdExists) & (f.sampleIdExists), :]
del umdm_files[:, ['dnaID', 'patientIdExists', 'sampleIdExists', 'filetype']]

# rename columns
umdm_files.names = {
  'umcgID': 'belongsToSubject',
  'filename': 'fileName',
  'filepath': 'filePath',
  'dateCreated': 'dateFileCreated'
}

umdm_files['dateRecordCreated'] = datetime.today().strftime('%Y-%m-%d')
umdm_files['recordCreatedBy'] = 'cosasbot'

#///////////////////////////////////////////////////////////////////////////////

# ~ 3 ~
# import
cosas.importDatatableAsCsv('umdm_files', umdm_files)
cosas.logout()
