# ///////////////////////////////////////////////////////////////////////////////
# FILE: data_vip_samplesheet.py
# AUTHOR: David Ruvolo
# CREATED: 2023-07-04
# MODIFIED: 2023-07-04
# PURPOSE: generate data for vip
# STATUS: in.progress
# PACKAGES: **see below**
# COMMENTS: NA
# ///////////////////////////////////////////////////////////////////////////////

from cosastools.molgenis import Molgenis
from datatable import dt, f, as_type
from os import environ
from dotenv import load_dotenv
import re
load_dotenv()

def collapseTuple(row):
  """collapse tuple"""
  return '/'.join(row) if all(row) else None

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
 
# identify subjects: based on samples
patientsDT['keep'] = dt.Frame([
  value in samplesDT['belongsToSubject'].to_list()[0]
  for value in patientsDT['subjectID'].to_list()[0]
])

# reduce dataset and attempt to identify family hierarchy
vipDT = patientsDT[f.keep, :][:, :, dt.sort(f.belongsToFamily)]

# establish patient type (i.e., index, mother, father)
vipDT[:, dt.update(type=as_type('index', dt.Type.str32))]

vipDT['type'] = dt.Frame([
  'father'
  if vipDT[(f.belongsToFather==row[0]) & (f.belongsToFamily==row[1]), :].nrows
  else row[2]
  for row in vipDT[:, (f.subjectID, f.belongsToFamily, f.type)].to_tuples()
])

vipDT['type'] = dt.Frame([
  'mother'
  if vipDT[(f.belongsToMother==row[0]) & (f.belongsToFamily==row[1]), :].nrows
  else row[2]
  for row in vipDT[:, (f.subjectID, f.belongsToFamily, f.type)].to_tuples()
])

del vipDT['keep']

#///////////////////////////////////////

# ~ 1d ~
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

# ~ 1e ~
# Get umdm_files
# Find vcfs and crams for selected patients

filesDT = dt.Frame(
  cosas.get(
    'umdm_files',
    attributes='belongsToSubject,belongsToSample,fileName,filePath,fileFormat',
    batch_size=10000
  ),
  types = {
    '_href': dt.Type.str32,
    'belongsToSubject': dt.Type.obj64,
    'belongsToSample': dt.Type.obj64,
    'fileName': dt.Type.str32,
    'filePath': dt.Type.str32,
    'fileFormat': dt.Type.str32
  }
)
del filesDT['_href']

# reduce to cram and vcfs
filesDT = filesDT[(f.fileFormat=='cram') | (f.fileFormat=='vcf'),:]

# collapse nested objects
filesDT['belongsToSubject'] = dt.Frame([
  obj['subjectID'] if obj else None
  for obj in filesDT['belongsToSubject'].to_list()[0]
])

filesDT['belongsToSample'] = dt.Frame([
  ','.join([row['sampleID'] for row in obj]) if obj else None
  for obj in filesDT['belongsToSample'].to_list()[0]
])

# merge cram
vipDT['cram'] = dt.Frame([
  collapseTuple(
    filesDT[
      (f.belongsToSubject==value) & (f.fileFormat=='cram'),
      (f.filePath, f.fileName)
    ].to_tuples()[0]
  )
  for value in vipDT['subjectID'].to_list()[0][:1]
])


# merge vcf
vipDT['vcf'] = dt.Frame([
  collapseTuple(
    filesDT[
      (f.belongsToSubject==value) & (f.fileFormat=='vcf'),
      (f.filePath, f.fileName)
    ].to_tuples()[0]
  )
  for value in vipDT['subjectID'].to_list()[0][:1]
])

# init columns that we do not have yet
vipDT[:, dt.update(
  project_id = as_type(None, dt.Type.str32),
  proband = as_type(None, dt.Type.str32),
  affected = as_type(None, dt.Type.bool8),
  assembly = as_type(None, dt.Type.str32)
)]

# rename columns
vipDT.names = {
  'subjectID': 'individual_id',
  'belongsToFamily': 'family_id',
  'genderAtBirth': 'sex',
  'observedPhenotype': 'hpo_ids',
  'belongsToFather': 'paternal_id',
  'belongsToMother': 'maternal_id',
}

# reorder dataset
vipDT = vipDT[:, (
  f.project_id,
  f.family_id,
  f.individual_id,
  f.type,
  f.sex,
  f.proband,
  f.affected,
  f.hpo_ids,
  f.paternal_id,
  f.maternal_id,
  f.assembly,
  f.vcf,
  f.cram
)]

vipDT.to_csv('private/vip_sample_sheet.csv')