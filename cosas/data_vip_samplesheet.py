# ///////////////////////////////////////////////////////////////////////////////
# FILE: data_vip_samplesheet.py
# AUTHOR: David Ruvolo
# CREATED: 2023-07-04
# MODIFIED: 2023-10-21
# PURPOSE: generate data for vip
# STATUS: stable
# PACKAGES: **see below**
# COMMENTS: NA
# ///////////////////////////////////////////////////////////////////////////////

from os import environ, path
from datetime import datetime
import re
import numpy as np
from datatable import dt, f, as_type
from tqdm import tqdm
from dotenv import load_dotenv
import pytz
from cosastools.molgenis import Molgenis
load_dotenv()

def today():
    """Return today's date in yyyy-mm-dd format"""
    return datetime.now(tz=pytz.timezone('Europe/Amsterdam')) \
        .strftime('%Y-%m-%-d')

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

#///////////////////////////////////////

# ~ 1c ~
# Get data from umdm_subjects

# retrieve patient metadata
patientsRaw = cosas.get(
  'umdm_subjects',
  attributes='subjectID,belongsToFamily,belongsToMother,belongsToFather,genderAtBirth,yearOfBirth',
  batch_size=10000
)

# convert to Frame
patientsDT = dt.Frame(
  patientsRaw,
  types = {
    'subjectID': dt.Type.str32,
    'belongsToFamily': dt.Type.str32,
    'belongsToMother': dt.Type.obj64,
    'belongsToFather': dt.Type.obj64,
    'genderAtBirth': dt.Type.obj64,
    'yearOfBirth': dt.Type.int16
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

# calcualte age
currentYear = int(datetime.now().strftime('%Y'))
patientsDT['age'] = dt.Frame([
    currentYear - value if bool(value) else None
    for value in patientsDT['yearOfBirth'].to_list()[0]
])

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

# calculate affected status: If an individual has an observedPhenotype, then
# affected status is true
hpoDT['affected'] = dt.Frame([
  bool(value) for value in hpoDT['observedPhenotype'].to_list()[0]
])

# drop Null entries
hpoDT = hpoDT[f.observedPhenotype!=None,:]

#///////////////////////////////////////

# ~ 1e ~
# Merge datasets to create all patient metadata

# remove duplicate entries
# Some individuals had multiple preparations from the same sample. At this point,
# it is not important as we only need to link the sample to an individual. Drop
# all duplicate records
openExomeDT = samplePrepDT[:, dt.first(f[:]), dt.by(f.belongsToSample)]

# Merge samples
samplesDT.key = 'sampleID'
openExomeDT.names = { 'belongsToSample': 'sampleID' }

openExomeDT = openExomeDT[:, :, dt.join(samplesDT)]

# Merge patients
# like the samples, some subjects have multiple duplicate entries. These
# can be dropped as we are interested in creating a link between subjects
# and samples.
openExomeDT = openExomeDT[:, dt.first(f[:]), dt.by(f.belongsToSubject)]

openExomeDT.names = { 'belongsToSubject' : 'subjectID' }
patientsDT.key = 'subjectID'
openExomeDT = openExomeDT[:, :, dt.join(patientsDT)]

# merge phenotypic data
hpoDT.names = { 'belongsToSubject' : 'subjectID' }
hpoDT.key = 'subjectID'
openExomeDT = openExomeDT[:, :, dt.join(hpoDT)]

# sort by family
openExomeDT = openExomeDT[:, :, dt.sort(f.belongsToFamily)]

#///////////////////////////////////////

# ~ 1f ~
# Get umdm_files
# Find vcfs and crams for selected patients

ATTRIBS = ','.join([
  'belongsToSubject',
  'fileName',
  'filePath',
  'fileFormat'
])

openExomeIDs = openExomeDT['subjectID'].to_list()[0]
for subjectID in tqdm(openExomeIDs):
    query = f"belongsToSubject=q={subjectID};(fileFormat=q=vcf,fileFormat=q=cram)"
    subjectFiles = cosas.get('umdm_files', attributes=ATTRIBS, q=query)
    if len(subjectFiles) > 0:
        subjectFiles = dt.Frame(subjectFiles, types = {
            '_href': dt.Type.str32,
            'belongsToSubject': dt.Type.obj64,        
            'fileName': dt.Type.str32,
            'filePath': dt.Type.str32,
            'fileFormat': dt.Type.str32
        })[:, ['fileName','filePath','fileFormat']]

        # add file paths if a matching record exists
        fileFormats = dt.unique(subjectFiles['fileFormat']).to_list()[0]
        if 'cram' in fileFormats:
            cram = subjectFiles[
              f.fileFormat=='cram',
              (f.filePath, f.fileName)
            ].to_tuples()[0]
            openExomeDT[f.subjectID==subjectID, 'cram'] = '/'.join(cram)

        if 'vcf' in fileFormats:
            vcf = subjectFiles[
                dt.re.match(f.fileName, '.*vcf.gz|.*vcf'),
                (f.filePath, f.fileName)
            ].to_tuples()[0]
            openExomeDT[f.subjectID==subjectID, 'vcf'] = '/'.join(vcf)

#///////////////////////////////////////////////////////////////////////////////

# ~ 2 ~
# Transform data into desired the format

# ~ 2a ~
# Filter data based on the following criteria
# Remove families where one or more family members where:
#   1. vcf or cram is unknown
#   2. the individual and maternal IDs are identical (i.e., fetus)

openExomeDT['isMissingFiles'] = dt.Frame([
   not all(row) for row in openExomeDT[:, (f.vcf, f.cram)].to_tuples()
])

openExomeDT['isFetus'] = dt.Frame([
   row[0] == row[1]
   for row in openExomeDT[:, (f.subjectID, f.belongsToMother)].to_tuples()
])

# how many records will be removed?
# openExomeDT[:, dt.count(), dt.by(f.isMissingFiles)]
# openExomeDT[:, dt.count(), dt.by(f.isFetus)]
# openExomeDT[:, dt.count(), dt.by(f.isMissingFiles,f.isFetus)]

#///////////////////////////////////////

# ~ 2b ~
# Identify familes with missing or incomplete data and remove
for subjectID in openExomeIDs:
    statuses = openExomeDT[f.subjectID==subjectID, (f.isMissingFiles, f.isFetus)]
    familyID = openExomeDT[f.subjectID==subjectID, 'belongsToFamily'].to_list()[0][0]
    if True in statuses.to_tuples()[0]:
        openExomeDT[f.belongsToFamily==familyID, 'removeFamily'] = True

# How many families will be removed?
# openExomeDT[:, dt.count(), dt.by(f.removeFamily)]
vipDT = openExomeDT[f.removeFamily!=True, :]

#///////////////////////////////////////

# ~ 2c ~
# Calculate index
# Identifying the index is somewhat possible by using affected status, the
# presence of parental identifiers, and date of birth

# start by copying affected status
vipDT['index'] = vipDT['affected']

# next, use parental identifies. If a row has a maternal and/or paternal identifier,
# then they are the index
vipDT['index'] = dt.Frame([
    True if (row[0] or row[1]) else row[2]
    for row in vipDT[:, (f.belongsToMother, f.belongsToFather, f.index)].to_tuples()
])

# next, check to see if the subjectID is in the maternal- or paternal ID columns
# this will determine if the entry is not the index
maternalIDs = vipDT[f.belongsToMother != None, 'belongsToMother'].to_list()[0]
paternalIDs = vipDT[f.belongsToFather != None, 'belongsToFather'].to_list()[0]

vipDT['index'] = dt.Frame([
    False if (row[0] in maternalIDs) or (row[0] in paternalIDs) else row[1]
    for row in vipDT[:, (f.subjectID,f.index)].to_tuples()
])

# identify families with Null index values
nullFamiles = dt.unique(vipDT[f.index==None,'belongsToFamily']).to_list()[0]
for familyID in nullFamiles:
    family = vipDT[f.belongsToFamily == familyID, :]
    for person in family['subjectID'].to_list()[0]:

        # only run if the person does not have an indication
        if family[f.subjectID==person, 'index'].to_list()[0][0] is None:

            # only run if the family has an index
            if (family[f.index == True,:].nrows>0):
                ages = family['age'].to_list()[0]
                ageAvg = np.mean(ages)
                # ageStd = np.std(ages)

                ageIndex = family[f.index==True,'age'].to_list()[0][0]
                agePerson = family[f.subjectID==person,'age'].to_list()[0][0]

                # it might be possible to calculate the parental status using the
                # age of the patient using the mean age. If the patient is older
                # than the mean, then it is possible they are the parent.
                vipDT[f.subjectID==person, 'index'] = agePerson < ageAvg
            else:
                print('Family',familyID,'does not have an index')

#///////////////////////////////////////

# ~ 2d ~
# remove familes where index is still none as it is difficult to determine the
# remaining relationships. It is highly likely that we are missing data.
familiesStillMissing = dt.unique(vipDT[f.index == None, 'belongsToFamily']).to_list()[0]
for familyID in familiesStillMissing:
    vipDT[f.belongsToFamily == familyID, 'removeFamily'] = True

vipDT = vipDT[f.removeFamily!=True,:]

#///////////////////////////////////////

# ~ 2e ~
# For indices, add missing maternal and paternal identifiers

indexIDs = vipDT[f.index==True, 'subjectID'].to_list()[0]
for subjectID in indexIDs:
    person = vipDT[f.subjectID==subjectID,:]
    familyID = person['belongsToFamily'].to_list()[0][0]

    # check to see if there are other family members
    if vipDT[f.belongsToFamily==familyID,:].nrows > 1:
        meanFamilyAge = np.mean(vipDT[f.belongsToFamily==familyID, 'age'].to_list()[0])

        if person['belongsToMother'].to_list()[0][0] is None:
            likelyMother = vipDT[
                (f.belongsToFamily == familyID) &
                (f.genderAtBirth == "female") &
                (f.age > meanFamilyAge),
                'subjectID'
            ]
            if likelyMother.nrows > 0:
                maternalID = likelyMother.to_list()[0][0]
                vipDT[f.subjectID==subjectID, 'belongsToMother'] = maternalID

        if person['belongsToFather'].to_list()[0][0] is None:
            likelyFather = vipDT[
                (f.belongsToFamily == familyID) &
                (f.genderAtBirth == "male") &
                (f.age > meanFamilyAge),
                'subjectID'
            ]
            if likelyFather.nrows > 0:
                paternalID = likelyFather.to_list()[0][0]
                vipDT[f.subjectID==subjectID, 'belongsToFather'] = paternalID

#///////////////////////////////////////

# ~ 2f ~
# Prepare dataset

# rename columns
vipDT.names = {
    'subjectID': 'individual_id',
    'belongsToFamily': 'family_id',
    'genderAtBirth': 'sex',
    'index': 'proband',
    'observedPhenotype': 'hpo_ids',
    'belongsToFather': 'paternal_id',
    'belongsToMother': 'maternal_id',
}


# copy drop columns
vipFamilyDT = vipDT.copy()
del vipFamilyDT['yearOfBirth']
del vipFamilyDT['removeFamily']
del vipFamilyDT['isMissingFiles']
del vipFamilyDT['isFetus']
del vipFamilyDT['age']
del vipFamilyDT['belongsToLabProcedure']

#///////////////////////////////////////

# update identifiers to match filename: individual, paternal, and maternal ID
vipFamilyDT['_id'] = dt.Frame([
  path.basename(value).split('.')[0] if value else None
  for value in vipFamilyDT['vcf'].to_list()[0]
])

# replace maternal identifier with the name of corresponding vcf file
for maternalID in vipFamilyDT[f.maternal_id != None, 'maternal_id'].to_list()[0]:
    person = vipFamilyDT[f.individual_id==maternalID, :]
    if person.nrows > 0:
        filename = person['_id'].to_list()[0][0]
        vipFamilyDT[f.maternal_id==maternalID, 'maternal_id'] = filename


# replace paternal identifier with the name of corresponding vcf file
for paternalID in vipFamilyDT[f.paternal_id != None, 'paternal_id'].to_list()[0]:
    person = vipFamilyDT[f.individual_id == paternalID, :]
    if person.nrows > 0:
        filename = person['_id'].to_list()[0][0]
        vipFamilyDT[f.paternal_id == paternalID, 'paternal_id'] = filename

# drop cases where there isn't a file - this information is likely missing
vipFamilyDT['maternal_id'] = dt.Frame([
    value if bool(value) and ('_' in value) else None
    for value in vipFamilyDT['maternal_id'].to_list()[0]
])

vipFamilyDT['paternal_id'] = dt.Frame([
    value if bool(value) and ('_' in value) else None
    for value in vipFamilyDT['paternal_id'].to_list()[0]
])

# create project_id
vipFamilyDT['project_id'] = dt.Frame([
    'NX154_' + value for value in vipFamilyDT['family_id'].to_list()[0]
])

# init assembly and sequencing methods always the same
vipFamilyDT['assembly'] = 'GRCh37'
vipFamilyDT['sequencing_method'] = 'WES'

# change classes: boolean -> string
vipFamilyDT['affected'] = vipFamilyDT[:, {'affected': as_type(f.affected, dt.Type.str32)}]
vipFamilyDT['proband'] = vipFamilyDT[:, {'proband': as_type(f.proband, dt.Type.str32)}]


# lowercase bool->sting columns
vipFamilyDT['affected'] = dt.Frame([
  value.lower() if value else (
      'false' if value is None else value
  )
  for value in vipFamilyDT['affected'].to_list()[0]
])

vipFamilyDT['proband'] = dt.Frame([
  value.lower() for value in vipFamilyDT['proband'].to_list()[0]
])


# replace individual_id with filename+individual_id
del vipFamilyDT['individual_id']
vipFamilyDT.names = {'_id': 'individual_id'}


# drop families with one individual
singleRecordFamiles = vipFamilyDT[
    :, dt.count(), dt.by(f.family_id)
][f.count==1, 'family_id'].to_list()[0]

vipFamilyDT['removeFamily'] = dt.Frame([
    value in singleRecordFamiles
    for value in vipFamilyDT['family_id'].to_list()[0]
])

vipFamilyDT = vipFamilyDT[f.removeFamily==False,:]

# import
# cosas.delete('cosasexports_vip')
cosas.importDatatableAsCsv('cosasexports_vip', vipFamilyDT)
