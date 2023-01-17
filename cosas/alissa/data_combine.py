#///////////////////////////////////////////////////////////////////////////////
# FILE: data_combine.py
# AUTHOR: David Ruvolo
# CREATED: 2023-01-13
# MODIFIED: 2023-01-13
# PURPOSE: combine test export into a csv
# STATUS: in.progress
# PACKAGES: **see below**
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from datatable import dt, f
import json

def read_json(path):
  """Read JSON
  Load the contents of a JSON file
  @param path location of the file
  @return json object
  """
  with open(path, 'r') as file:
    data = json.load(file)
  file.close()
  return data
  
def collapseNestedJsonByKey(data, property, seperator="; "):
  """Collapse nested json by key
  Collapse a nested json object where key value pairs do not matter
  
  @param data json object
  @param property name of the property that contains nested data
  @return collapsed string
  """
  values = []
  for key in data[property].keys():
    values.append(f"{key}: {data[property][key].strip()}")
  return f"{seperator}".join(values)

# read data
patients = read_json('private/alissa_export/2023_01_13/patients.json')
analyses = read_json('private/alissa_export/2023_01_13/analyses.json')
variants = read_json('private/alissa_export/2023_01_13/variants.json')

#///////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Merge data

# ~ 1a ~
# Prep patients dataset
for patient in patients:
  if not bool(patient['phenotypes']):
    patient['phenotypes'] = None
  if not bool(patient['customFields']):
    patient['customFields'] = None


# ~ 1b ~
# Prep analyses dataset
for analysis in analyses:
  if not bool(analysis['targetPanelNames']):
    analysis['targetPanelNames'] = None
  else:
    analysis['targetPanelNames'] = '; '.join(analysis['targetPanelNames'])
    
# ~ 1c ~
# Prep variants data
for variant in variants:
  if not bool(variant['variantAssessmentLabels']):
    variant['variantAssessmentLabels'] = None
  
  if not bool(variant['variantAssessmentNotes']):
    variant['variantAssessmentNotes'] = None
    
  if bool(variant['databaseReferences']):
    variant['databaseReferences'] = collapseNestedJsonByKey(
      data = variant,
      property='databaseReferences'
    )
  else:
    variant['databaseReferences'] = None

  if bool(variant['classificationTreeLabelsScore']):
    variant['classificationTreeLabelsScore'] = f"{variant['classificationTreeLabelsScore']['labels']}; scores: f{variant['classificationTreeLabelsScore']['score']}"
  else:
    variant['classificationTreeLabelsScore']

  if bool (variant['customFields']):
    fieldsCollapsed = []
    for field in variant['customFields']:
      fieldsCollapsed.append(f"{field['name']} - {field['value']}")
    variant['customFields'] = '; '.join(fieldsCollapsed)
    
  if bool(variant['externalDatabases']):
    variant['externalDatabases'] = collapseNestedJsonByKey(
      data = variant,
      property='externalDatabases'
    )
  else:
    variant['externalDatabases'] = None
    
  if bool(variant['platformDatasets']):
    variant['platformDatasets'] = collapseNestedJsonByKey(
      data=variant,
      property='platformDatasets'
    )
  else:
    variant['platformDatasets'] = None

# ~ 1c ~
# Create datatable objects
patientsDT = dt.Frame(patients)
analysesDT = dt.Frame(analyses)
variantsDT = dt.Frame(variants)

# drop columns
patientsDT.names = {'id': 'patientId' }
del patientsDT[:, [
  'createdOn',
  'createdBy',
  'lastUpdatedOn',
  'lastUpdatedBy',
  'customFields',
  'phenotypes',
  'familyIdentifier',
  'comments'
]]

analysesDT.names
del analysesDT[:, [
  'summary',
  'description',
  'createdOn',
  'createdBy',
  'lastUpdatedOn',
  'lastUpdatedBy'
]]

# ~ 1d ~
# Merge data

# join patient information
patientsDT.key = 'patientId'
variantsDT = variantsDT[:, :, dt.join(patientsDT)]

# join analyses
analysesDT.key = ['patientId', 'analysisId']
variantsDT = variantsDT[:, :, dt.join(analysesDT)]

# reord columns
variantsDT = variantsDT[:, [
  'patientId', 
  'analysisId',
  'variantExportId',
  
  # patientinfo
  'accessionNumber',
  'gender',
  'folderName',
  
  # analyses data
  'reference.0',
  'analysisType',
  'status',
  'domainName',
  'genomeBuild',
  'analysisPipelineName',
  'classificationTreeName',
  'targetPanelNames',
  
  # variant data
  'start',
  'stop',
  'gene',
  'reference',
  'allele1',
  'allele2',
  'alleleInScope',
  'allele1Frequency',
  'allele2Frequency',
  'allelicDepth1',
  'allelicDepth2',
  'readDepth',
  'type',
  'transcript',
  'location',
  'exon',
  'effect',
  'protein',
  'zygosity',
  'genotype',
  'chromosome',
  'chromosomeType',
  'toReview',
  'includeInReport',
  'variantAssessment',
  'variantAssessmentLabels',
  'variantAssessmentNotes',
  'databaseReferences',
  'classificationTreeLabelsScore',
  'geneProfileReport',
  'customFields',
  'externalDatabases',
  'platformDatasets',
  'thirdPartyStatus',
  'alleleType',
  'classification',
  'cnv',
  'cdna'
]]

variantsDT.names = {'reference.0': 'analysisReference'}

variantsDT.to_csv('private/alissa_export/2023_01_13/alissa_variants.csv')

# for name in variantsDT.names:
#   f"{name}: {variantsDT[name].type}"