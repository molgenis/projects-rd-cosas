#'////////////////////////////////////////////////////////////////////////////
#' FILE: cosasreports_attribute_summary.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-04-19
#' MODIFIED: 2022-07-29
#' PURPOSE: generate a coverage report of all attributes in COSAS
#' STATUS: stable
#' PACKAGES: **see below**
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

import molgenis.client as molgenis
from datetime import datetime
from datatable import dt,f
import numpy as np
import re

# for local dev
# from dotenv import load_dotenv
# from os import environ
# load_dotenv()
# host=environ['MOLGENIS_ACC_HOST']
# token=environ['MOLGENIS_ACC_TOKEN']
# cosas= molgenis.Session(host)
# cosas.login(environ['MOLGENIS_ACC_USR'], environ['MOLGENIS_ACC_PWD'])

host='http://localhost/api'
token='${molgenisToken}'

def summarizeData(tablename, data) -> dict:
  """Summarize Data
  For all columns in a datatable object, get the count of non-NoneType vaues
  and the total number of values (i.e., rows)
  
  @param tablename name of the table
  @param data a datatable object
  
  @return dictionary
  """
  datatable = data
  data = []
  for column in datatable.names:
    data.append({
      'databaseTable': tablename,
      'databaseColumn': column,
      'countOfValues': len([x for x in datatable[:, [column]].to_list()[0] if x is not None]),
      'totalValues': datatable[:, [column]].nrows
    })
  return data
  
def getAttributeLabel(pkg, table, column):
  response = cosas.get(
    entity = 'sys_md_Attribute',
    q = f'entity=={pkg}_{table};name=={column}'
  )
  try:
    return response[0]['label']
  except KeyError as error:
    print('Column', column, 'does not exist in', pkg,'_',table, '\n',str(error))
    return None
  except IndexError as error:
    print('No results found for "',column,'" in', pkg,'_',table, '\n',str(error))
    return None

# define attributes that are currently used
cosasTables={
  'subjects': [
    'subjectID',
    'belongsToFamily',
    'belongsToMother',
    'belongsToFather',
    'belongsWithFamilyMembers',
    'subjectStatus',
    'dateOfBirth',
    'yearOfBirth',
    'dateOfDeath',
    'ageAtDeath',
    'genderAtBirth',
    'primaryOrganization'
  ],
  'clinical': [
    'clinicalID',
    'belongsToSubject',
    'observedPhenotype',
    'unobservedPhenotype',
    'provisionalPhenotype',
  ],
  'samples': [
    'sampleID',
    'belongsToSubject',
    'biospecimenType'  
  ],
  'samplePreparation': [
    'samplePreparationID',
    'belongsToSample',
    'belongsToLabProcedure',
    'belongsToRequest',
    'belongsToBatch',
  ],
  'sequencing': [
    'sequencingID',
    'belongsToLabProcedure',
    'belongsToSamplePreparation',
    'reasonForSequencing',
    'sequencingDate',
    'sequencingFacilityOrganization',
    'sequencingPlatform',
    'sequencingInstrumentModel',
    'referenceGenomeUsed',
  ]
}

#//////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# GET INPUT DATA
# Fetch all data from the UMDM schema and flatten attributes

print('Preparing data....')
cosas=molgenis.Session(url=host,token=token)


# ~ 1a ~
# Get Data
print('Fetching COSAS data....')

subjectData = cosas.get(
    entity='umdm_subjects',
    batch_size=10000,
    attributes= ','.join(cosasTables['subjects'])
)

clinicalData = cosas.get(
    entity='umdm_clinical',
    batch_size=10000,
    attributes=','.join(cosasTables['clinical'])
)

samplesData = cosas.get(
    entity='umdm_samples',
    batch_size=10000,
    attributes=','.join(cosasTables['samples'])
)

samplePrepData = cosas.get(
    entity='umdm_samplePreparation',
    batch_size=10000,
    attributes=','.join(cosasTables['samplePreparation'])
)

sequencingData = cosas.get(
    entity='umdm_sequencing',
    batch_size=10000,
    attributes=','.join(cosasTables['sequencing'])
)

# ~ 1b ~
# Flatten attributes
print('Flattening nested attributes....')

for row in subjectData:
    row['belongsToMother'] = row.get('belongsToMother',{}).get('subjectID')
    row['belongsToFather'] = row.get('belongsToFather',{}).get('subjectID')
    row['subjectStatus'] = row.get('subjectStatus',{}).get('value')
    row['genderAtBirth'] = row.get('genderAtBirth',{}).get('value')
    row['primaryOrganization'] = row.get('primaryOrganization',{}).get('value')

for row in clinicalData:
    row['belongsToSubject'] = row.get('belongsToSubject',{}).get('subjectID')
    row['observedPhenotype'] = len(row.get('observedPhenotype')) if row.get('observedPhenotype') is not None else None
    row['unobservedPhenotype'] = len(row.get('unobservedPhenotype')) if row.get('unobservedPhenotype') is not None else None
    row['provisionalPhenotype'] = len(row.get('provisionalPhenotype')) if row.get('provisionalPhenotype') is not None else None
    
for row in samplesData:
    row['belongsToSubject'] = row.get('belongsToSubject',{}).get('subjectID')
    row['biospecimenType'] = row.get('biospecimenType', {}).get('value')

for row in samplePrepData:
    row['belongsToSample'] = row.get('belongsToSample', {}).get('sampleID')
    row['belongsToLabProcedure'] = row.get('belongsToLabProcedure', {}).get('code')
    row['belongsToRequest'] = row.get('belongsToRequest')
    row['belongsToBatch'] = row.get('belongsToBatch')

for row in sequencingData:
    row['belongsToLabProcedure'] = row.get('belongsToLabProcedure', {}).get('code')
    row['belongsToSamplePreparation'] = row.get('belongsToSamplePreparation', {}).get('sampleID')
    row['reasonForSequencing'] = row.get('reasonForSequencing', {}).get('value')
    row['sequencingFacilityOrganization'] = row.get('sequencingFacilityOrganization', {}).get('value')
    row['sequencingPlatform'] = row.get('sequencingPlatform', {}).get('value')
    row['sequencingInstrumentModel'] = row.get('sequencingInstrumentModel', {}).get('value')
    row['referenceGenomeUsed'] = row.get('referenceGenomeUsed', {}).get('value')

# ~ 1c ~
# Convert to DataTable object
print('Converting objects to datatables....')

subjects = dt.Frame(subjectData)
clinical = dt.Frame(clinicalData)
samples = dt.Frame(samplesData)
samplePrep = dt.Frame(samplePrepData)
sequencing = dt.Frame(sequencingData)

del subjects['_href']
del clinical['_href']
del samples['_href']
del samplePrep['_href']
del sequencing['_href']

#//////////////////////////////////////////////////////////////////////////////

# ~ 2 ~
# Summarize Data

print('Summarizing data....')
cosasSummary=summarizeData('subjects', subjects)
cosasSummary.extend(summarizeData('clinical', clinical))
cosasSummary.extend(summarizeData('samples', samples))
cosasSummary.extend(summarizeData('samplePreparation', samplePrep))
cosasSummary.extend(summarizeData('sequencing', sequencing))

cosasSummaryDT = dt.Frame(cosasSummary)

# ~ 2b ~
# Add and transform columns

# add row identifier
print('Setting unique identifiers....')
cosasSummaryDT['identifier'] = dt.Frame([
    f'{row[0]}_{row[1]}'
    for row in cosasSummaryDT[:, (f.databaseTable, f.databaseColumn)].to_tuples()
])

# find the number of missing values (i.e., None)
print('Calculating difference in values (total - count)....')
cosasSummaryDT['differenceInValues'] = dt.Frame([
    row[1] - row[0]
    for row in cosasSummaryDT[:, (f.countOfValues, f.totalValues)].to_tuples()
])

# calculate the percentage of coverage (i.e., how many values out of the total)
print('Calculating percentage of coverage (count / total)....')
cosasSummaryDT['percentComplete'] = dt.Frame([
    round(row[0] / row[1], 2)
    for row in cosasSummaryDT[:, (f.countOfValues, f.totalValues)].to_tuples()
])


# set key type based on the presence of 'belongs' and 'ID'
print('Determining key type....')
cosasSummaryDT['databaseKey'] = dt.Frame([
    'foreign database key' if re.search(r'(belong|Phenotype|Organization|subjectStatus|reference|sequencingInstrument|sequencingPlatform|Type|reasonFor)', value) else (
        'primary database key' if re.search(r'(ID)$', value) else None
    )
    for value in cosasSummaryDT[:, f.databaseColumn].to_list()[0]
])

# set display name
cosasSummaryDT['displayName'] = dt.Frame([
  getAttributeLabel(pkg='umdm', table=d[0], column=d[1])
  for d in cosasSummaryDT[:, ['databaseTable', 'databaseColumn']].to_tuples()
])

cosasSummaryDT['displayName'] = dt.Frame([
  d[1] if d[0] is None else d[0]
  for d in cosasSummaryDT[:, ['displayName', 'databaseColumn']].to_tuples()
])

# set date last updated
cosasSummaryDT['dateLastUpdated'] = datetime.utcnow().strftime('%Y-%m-%d')

#//////////////////////////////////////////////////////////////////////////////

# ~ 3 ~
# Import

# cosasSummaryDT.to_csv('_data/cosasreports_attributesummary.csv')

print('Importing data....')
importData = cosasSummaryDT.to_pandas().replace({np.nan: None}).to_dict('records')
cosas.delete(entity='cosasreports_attributesummary')
cosas.add_all(entity='cosasreports_attributesummary', entities=importData)
