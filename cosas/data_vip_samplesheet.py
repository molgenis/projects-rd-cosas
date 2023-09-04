# ///////////////////////////////////////////////////////////////////////////////
# FILE: data_vip_samplesheet.py
# AUTHOR: David Ruvolo
# CREATED: 2023-07-04
# MODIFIED: 2023-09-04
# PURPOSE: generate data for vip
# STATUS: stable
# PACKAGES: **see below**
# COMMENTS: NA
# ///////////////////////////////////////////////////////////////////////////////

from cosastools.molgenis import Molgenis
from datatable import dt, f, as_type
from tqdm import tqdm
from os import environ, path
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import pytz
import re
load_dotenv()

def today():
  """Return today's date in yyyy-mm-dd format"""
  return datetime.now(tz=pytz.timezone('Europe/Amsterdam')).strftime('%Y-%m-%-d')

cosas = Molgenis(environ['MOLGENIS_ACC_HOST'])
cosas.login(environ['MOLGENIS_ACC_USR'], environ['MOLGENIS_ACC_PWD'])

# ///////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Retrieve data

# ~ 1a ~
# Get data from umdm_samplePreparation
# find all samples associated with a specific test code
samplePrepDT = dt.Frame(
  cosas.get(
    'umdm_samplePreparation',
    q='belongsToLabProcedure==NX154',
    attributes='belongsToSample,belongsToLabProcedure',
    batch_size=10000
  ),
  types={
    '_href': dt.Type.str32,
    'belongsToSample': dt.Type.obj64,
    'belongsToLabProcedure': dt.Type.obj64
  }
)

del samplePrepDT['_href']

# collapse object classes
samplePrepDT['belongsToSample'] = dt.Frame([
  obj['sampleID'] for obj in samplePrepDT['belongsToSample'].to_list()[0]
])

samplePrepDT['belongsToLabProcedure'] = dt.Frame([
  obj['code'] for obj in samplePrepDT['belongsToLabProcedure'].to_list()[0]
])

#///////////////////////////////////////

# ~ 1b ~
# Get data from umdm_samples
# retrieve sample metadata to find subject ID
samplesDT = dt.Frame(
  cosas.get(
    'umdm_samples',
    attributes='sampleID,belongsToSubject',
    batch_size=10000
  ),
  types={
    '_href': dt.Type.str32,
    'sampleID': dt.Type.str32,
    'belongsToSubject': dt.Type.obj64
  }
)

del samplesDT['_href']

# collapse object classes
samplesDT['belongsToSubject'] = dt.Frame([
  obj['subjectID'] for obj in samplesDT['belongsToSubject'].to_list()[0]
])

# reduce to samples identified in the previous step
samplesDT['keep'] = dt.Frame([
  value in samplePrepDT['belongsToSample'].to_list()[0]
  for value in samplesDT['sampleID'].to_list()[0]
])

samplesDT = samplesDT[f.keep, :]
del samplesDT['keep']


# merge sequencing metadata (currently unavailable)
# sequencingDT = dt.Frame(
#   cosas.get(
#     'umdm_sequencing',
#     attributes='belongsToSamplePreparation,belongsToLabProcedure,reasonForSequencing,referenceGenomeUsed',
#     q="belongsToLabProcedure=q=NX154",
#     batch_size=10000
#   ),
#   types = {
#     '_href': dt.Type.str32,
#     'belongsToSamplePreparation': dt.Type.obj64,
#     'belongsToLabProcedure': dt.Type.obj64,
#     'reasonForSequencing': dt.Type.obj64,
#     'referenceGenomeUsed': dt.Type.obj64
#   }
# )

# del sequencingDT['_href']

#///////////////////////////////////////

# ~ 1c ~
# Get data from umdm_subjects

# retrieve patient metadata
patientsDT = dt.Frame(
  cosas.get(
    'umdm_subjects',
    attributes='subjectID,belongsToFamily,belongsToMother,belongsToFather,genderAtBirth',
    batch_size=10000
  ),
  types = {
    'subjectID': dt.Type.str32,
    'belongsToFamily': dt.Type.str32,
    'belongsToMother': dt.Type.obj64,
    'belongsToFather': dt.Type.obj64,
    'genderAtBirth': dt.Type.obj64,
  }
)

del patientsDT['_href']

# collapse objects
patientsDT['belongsToMother'] = dt.Frame([
  obj['subjectID'] if bool(obj) else None
  for obj in patientsDT['belongsToMother'].to_list()[0]
])

patientsDT['belongsToFather'] = dt.Frame([
  obj['subjectID'] if bool(obj) else None
  for obj in patientsDT['belongsToFather'].to_list()[0]
])

patientsDT['genderAtBirth'] = dt.Frame([
  re.sub(r'(assigned|at birth)', '', obj['value'])
  if bool(obj) else None
  for obj in patientsDT['genderAtBirth'].to_list()[0]
])

patientsDT['genderAtBirth'] = dt.Frame([
  value.strip() if bool(value) else value
  for value in patientsDT['genderAtBirth'].to_list()[0]
])
 
#///////////////////////////////////////

# ~ 1d ~
# Select patients and parents

# identify subjects: based on samples
patientsDT['keep'] = dt.Frame([
  value in samplesDT['belongsToSubject'].to_list()[0]
  for value in patientsDT['subjectID'].to_list()[0]
])

# keep maternal and paternal identifiers
subjectsToKeep = patientsDT[f.keep,'subjectID'].to_list()[0]
for id in subjectsToKeep:
  familyID = patientsDT[f.subjectID==id, 'belongsToFamily'].to_list()[0][0]
  maternalID = patientsDT[f.subjectID==id, 'belongsToMother'].to_list()[0][0]
  paternalID = patientsDT[f.subjectID==id, 'belongsToFather'].to_list()[0][0]
  
  if bool(maternalID) or bool(paternalID):
    patientsDT[f.subjectID==id, 'type'] = 'index'
  
  if bool(maternalID):
    patientsDT[f.subjectID==maternalID, 'keep'] = True
    patientsDT[f.subjectID==maternalID, 'type'] = 'mother'
  
  if bool(paternalID):
    patientsDT[f.subjectID==paternalID, 'keep'] = True
    patientsDT[f.subjectID==paternalID, 'type'] = 'father'


# reduce dataset and attempt to identify family hierarchy
vipDT = patientsDT.copy()[f.keep, :][:, :, dt.sort(f.belongsToFamily)]

#///////////////////////////////////////

# ~ 1e ~
# Get umdm_clinical
# Merge phenotypic data with selected patients (only observedPhenotypes)

hpoDT = dt.Frame(
  cosas.get(
    'umdm_clinical',
    attributes='belongsToSubject,observedPhenotype',
    batch_size=10000
  ),
  types = {
    '_href': dt.Type.str32,
    'belongsToSubject': dt.Type.obj64,
    'observedPhenotype': dt.Type.obj64
  }
)

del hpoDT['_href']

# collapse nested objects
hpoDT['belongsToSubject'] = dt.Frame([
  obj['subjectID'] for obj in hpoDT['belongsToSubject'].to_list()[0]
])

hpoDT['observedPhenotype'] = dt.Frame([
  ','.join([row['code'] for row in obj]) if bool(obj) else None
  for obj in hpoDT['observedPhenotype'].to_list()[0]
])

# merge observed phenotypes
vipDT['observedPhenotype'] = dt.Frame([
  hpoDT[f.belongsToSubject==value, 'observedPhenotype'].to_list()[0][0]
  if value in hpoDT['belongsToSubject'].to_list()[0]
  else None
  for value in vipDT['subjectID'].to_list()[0]
])

#///////////////////////////////////////

# ~ 1f ~
# Get umdm_files
# Find vcfs and crams for selected patients

vipSubjectIDs = vipDT['subjectID'].to_list()[0]
for id in tqdm(vipSubjectIDs):
  subjectFiles = cosas.get(
    'umdm_files',
    attributes='belongsToSubject,fileName,filePath,fileFormat',
    q=f"belongsToSubject=q={id};(fileFormat=q=vcf,fileFormat=q=cram)"
  )

  if len(subjectFiles) > 0:
    subjectFiles = dt.Frame(
      subjectFiles,
      types = {
        '_href': dt.Type.str32,
        'belongsToSubject': dt.Type.obj64,        
        'fileName': dt.Type.str32,
        'filePath': dt.Type.str32,
        'fileFormat': dt.Type.str32
      }
    )[:, ['fileName','filePath','fileFormat']]

    # add file paths if a matching record exists
    fileFormats = dt.unique(subjectFiles['fileFormat']).to_list()[0] 
    if 'cram' in fileFormats:
      cram = subjectFiles[f.fileFormat=='cram', (f.filePath, f.fileName)].to_tuples()[0]
      vipDT[f.subjectID==id, 'cram'] = '/'.join(cram)

    if 'vcf' in fileFormats:
      vcf = subjectFiles[dt.re.match(f.fileName, '.*vcf.gz|.*vcf'), (f.filePath, f.fileName)].to_tuples()[0]
      vipDT[f.subjectID==id, 'vcf'] = '/'.join(vcf)

#///////////////////////////////////////////////////////////////////////////////

# ~ 2 ~
# Transform data into desired the format

# rename columns
vipDT.names = {
  'subjectID': 'individual_id',
  'belongsToFamily': 'family_id',
  'genderAtBirth': 'sex',
  'type': 'proband',
  'observedPhenotype': 'hpo_ids',
  'belongsToFather': 'paternal_id',
  'belongsToMother': 'maternal_id',
}


# ~ 2b ~
# Filter data based on the following criteria
# Remove families where one or more family members where:
#   1. vcf or cram is unknown
#   2. the individual and maternal IDs are identical (i.e., fetus)

vipDT['missingFiles'] = dt.Frame([
  not all(row) for row in vipDT[:, (f.vcf, f.cram)].to_tuples()
])

vipDT['isFetus'] = dt.Frame([
  row[0] == row[1] if all(row) else False
  for row in vipDT[:, (f.individual_id, f.maternal_id)].to_tuples()
])

# how many records will be removed?
# vipDT[:, dt.count(), dt.by(f.missingFiles)]
# vipDT[:, dt.count(), dt.by(f.isFetus)]
# vipDT[:, dt.count(), dt.by(f.missingFiles,f.isFetus)]


# set status for families
vipDT['removeFamily'] = False
for id in vipDT['individual_id'].to_list()[0]:
  row = vipDT[f.individual_id==id, (f.missingFiles, f.isFetus, f.family_id)]
  if True in row[:, (f.missingFiles, f.isFetus)].to_tuples()[0]:
    familyID = row['family_id'].to_list()[0][0]
    vipDT[f.family_id==familyID, 'removeFamily'] = True

# drop records      
vipFamilyDT = vipDT.copy()[f.removeFamily==False, :]

#///////////////////////////////////////

# update identifiers to match filename: individual, paternal, and maternal ID
vipFamilyDT['_id'] = dt.Frame([
  path.basename(value).split('.')[0] if value else None
  for value in vipFamilyDT['vcf'].to_list()[0]
])

vipFamilyDT['maternal_id'] = dt.Frame([
  vipFamilyDT[f.individual_id==value, '_id'].to_list()[0][0]
  if value else None
  for value in vipFamilyDT['maternal_id'].to_list()[0]
])

vipFamilyDT['paternal_id'] = dt.Frame([
  vipFamilyDT[f.individual_id == value, '_id'].to_list()[0][0]
  if value else None
  for value in vipFamilyDT['paternal_id'].to_list()[0]
])


# recode type to proband
vipFamilyDT['proband'] = dt.Frame([
  False if (value in ['mother', 'father']) else True
  for value in vipFamilyDT['proband'].to_list()[0]
])


# Set affected status based on proband (i.e., is index), and convert to string
vipFamilyDT['affected'] = dt.Frame([
  value is True for value in vipFamilyDT['proband'].to_list()[0]
])


# manualy create columns and change classes
vipFamilyDT[:, dt.update(
  project_id = 'NX154_' + f.family_id,
  assembly= 'GRCh37',
  sequencing_method='WES',
  affected = as_type(f.affected, dt.Type.str32),
  proband= as_type(f.proband, dt.Type.str32)
)]

# lowercase bool->sting columns
vipFamilyDT['affected'] = dt.Frame([
  value.lower() for value in vipFamilyDT['affected'].to_list()[0]
])

vipFamilyDT['proband'] = dt.Frame([
  value.lower() for value in vipFamilyDT['proband'].to_list()[0]
])


# reorder dataset
vipFamilyDT = vipFamilyDT[:, (
  f.project_id,
  f.family_id,
  f._id,
  # f.individual_id,
  f.proband,
  f.sex,
  f.affected,
  f.hpo_ids,
  f.paternal_id,
  f.maternal_id,
  f.assembly,
  f.sequencing_method,
  f.vcf,
  f.cram
)]

vipFamilyDT.names = {'_id': 'individual_id'}

file=f"private/vip_sample_sheet_{today()}.tsv"

vipFamilyDT \
  .to_pandas() \
  .to_csv(file,index=False, sep='\t', quoting=None)

# vipFamilyDT.to_csv(file, sep='\t')
