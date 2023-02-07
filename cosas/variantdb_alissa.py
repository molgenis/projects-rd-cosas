#//////////////////////////////////////////////////////////////////////////////
# FILE: alissa.py
# AUTHOR: David Ruvolo
# CREATED: 2022-04-19
# MODIFIED: 2023-02-07
# PURPOSE: fetch data from alissa
# STATUS: experimental
# PACKAGES: cosas.api.alissa, dotenv, os, requests
# COMMENTS: The purpose of this script is to extract variant information for
# all patients, or a subset of patients, from the UMCG instance of Alissa
# Interpret. To extract classifications, you must run a series of requests.
# These steps are outlined below.
# 
# 1. Get internal patient identifiers (run `variantdb_alissa_prep.py`)
# 2. Get analyses and analysis identifiers for each patient
# 3. Get all variant export identifiers for each analysis identifier
# 4. Using the patient-, analysis-, and variant export identifier, extract
#    the variant information.
#
# This script usese a mini Alissa client for extracting this information.
# All methods were designed according to the Alissa Interpret Public API
# (v5.3) documentation. All request parameters that are defined in the official
# are supported.
#
# NOTE: The Alissa client contains methods specific to the extracting variant
# information. Only a handful of the methods defined in the API documentation
# are available in this python script.
#//////////////////////////////////////////////////////////////////////////////

from cosas.api.molgenis2 import Molgenis
from cosas.alissa.client import Alissa
from dotenv import load_dotenv
from datetime import datetime
from datatable import dt, f, as_type
from os import environ
from tqdm import tqdm
import requests
import json
import re
load_dotenv()

def now():
  return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  
def today():
  return datetime.today().strftime('%Y-%m-%d')
  
def cleanKeyName(value):
  val = re.sub(r'[()\+]', '', value)
  return re.sub(r'(\s+|[-/])', '_', val)

# Connect to COSAS database
cosas = Molgenis(environ['MOLGENIS_ACC_HOST'])
cosas.login(environ['MOLGENIS_ACC_USR'], environ['MOLGENIS_ACC_PWD'])

# Connect to the UMCG instance of Alissa Interpret
# NOTE: Credentials are stored in the vault, but you will need your own API
# username and password. This information can be generated if you have been
# given admin rights in Alissa. Contact agilent support if you have any
# questions or if you encounter any issues.

alissa = Alissa(
  host=environ['ALISSA_HOST'],
  clientId=environ['ALISSA_CLIENT_ID'],
  clientSecret=environ['ALISSA_CLIENT_SECRET'],
  username=environ['ALISSA_API_USR'],
  password=environ['ALISSA_API_PWD']
)

#///////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# GET ANALYSES ASSOCIATED WITH EACH PATIENT
# Using the information stored in `alissa_patients`, retrieve a list of
# analysis identifiers associated with each patient

# pull patient info from the database
patientsDT = dt.Frame(
  cosas.get(
    'alissa_patients',
    q="hasError==false",
    batch_size=10000
  )
)

del patientsDT['_href']

# isolate Alissa Internal IDs
patientIdentifiers=patientsDT['alissaInternalID'].to_list()[0]

# GET ANALYSES BY PATIENT
# For all patient identifiers that were extracted in the previous step, return
# all analysis identifiers. The analysis ID is required in order to retrieve the
# molecular variant report identifier. Since we are are only interested in the
# analysis ID, at this point anyways, every analysis ID are returned. If you
# would like to get information for a specific analysis type, then apply
# filters in the 'for' loop. If no analyses were found for patient, then they
# aren't included in the remaining steps.

analysesByPatient = []
for id in tqdm(patientIdentifiers):
  analysisResponse = alissa.getPatientAnalyses(patientId=id)
  if analysisResponse:
    for analysis in analysisResponse:
      analysis['analysisId'] = analysis['id']
      del analysis['id']
      analysesByPatient.append(analysis)


#///////////////////////////////////////////////////////////////////////////////
            
# ~ 3 ~
# GET VARIANT EXPORT IDs
#
# Using the patient-analysis identifier, get all variant export identifiers.
# This step will create an object where each row is one patient, analysis, and
# variant export (long format). I am not sure if an analysis can have more than
# one export. I'm not sure if analyses of a patient can have more than one
# export identifier (I just don't know how their database is structured), but
# if the response is type list, the data can be handled accordingly.
#
# The reason for the try-except is that a patient may have a valid analysis
# identifier but not records at the molecular export endpoint. If this is the
# case, the server throws a 404 error. This is most likely the reason for the
# error. Either way, the patient and analysis IDs are printed so you can
# follow up with this. These patients-analyses aren't included in the
# remaining steps.

variantExportsByAnalyses = []
for analysisRow in tqdm(analysesByPatient):
  try:
    variantResponse = alissa.getPatientVariantExportId(
      analysisId=analysisRow['analysisId'],
      markedForReview=True,
      markedIncludeInReport=False
    )
    if variantResponse:
      if isinstance(variantResponse, dict):
        variantResponse['patientId'] = analysisRow['patientId']
        variantResponse['analysisId'] = analysisRow['analysisId']
        variantResponse['dateRetrieved'] = now()
        variantExportsByAnalyses.append(variantResponse)
      if isinstance(variantResponse, list):
        for record in variantResponse:
          record['patientId'] = analysisRow['patientId']
          record['analysisId'] = analysisRow['analysisId']
          record['dateRetreived'] = now()
          variantExportsByAnalyses.append(record)
  except requests.exceptions.HTTPError as error:
    pass


#///////////////////////////////////////////////////////////////////////////////

# ~ 4 ~
# GET VARIANT EXPORT REPORTS
# Now that a list of variant export reports has been compiled, it is possible
# to retrieve the variant export report for the patient and analysis.

variantExport = []
for variantRow in tqdm(variantExportsByAnalyses):
  try:
    exportResponse = alissa.getPatientVariantExportData(
      analysisId=variantRow['analysisId'],
      exportId=variantRow['exportId']
    )
    if exportResponse:
      if isinstance(exportResponse, dict):
        exportResponse['patientId'] = variantRow['patientId']
        exportResponse['analysisId'] = variantRow['analysisId']
        exportResponse['variantExportId'] = variantRow['exportId']
        variantExport.append(exportResponse)
      if isinstance(exportResponse, list):
        for export in exportResponse:
          export['patientId'] = variantRow['patientId']
          export['analysisId'] = variantRow['analysisId']
          export['variantExportId'] = variantRow['exportId']
          variantExport.append(export)
  except requests.exceptions.HTTPError as error:
    pass

# save to file so you don't have to rerun the script
# with open('private/alissa_variant_export_20220206.json', 'w') as file:
#   json.dump(variantExport,file)

#///////////////////////////////////////////////////////////////////////////////

# ~ 5 ~
# PROCESS VARIANT EXPORT DATA
# Even though you may have retrieved a variant export identifier for all
# analyses, variant data may not be retrievable. If this is the case, note the
# error and store it in the table.

# with open('private/alissa_variant_export_20220206.json', 'r') as file:
#   variantExport = json.load(file)
# file.close()

variantdata = []

for row in tqdm(variantExport):
  
  # log errors in the table
  if 'errorCode' in row.keys():
    newRow = {
      'patientId': row['patientId'],
      'analysisId': row['analysisId'],
      'variantExportId': row['variantExportId'],
      'hasError': True,
      'error.type': row['errorCode'],
      'dateFirstRun': today(),
      'dateLastUpdated': today(),
      'comments': row['errorMessage']
    }
    variantdata.append(newRow)
    
  # process results
  else:
    newRow = row
    if not bool(newRow['variantAssessmentLabels']):
      newRow['variantAssessmentLabels'] = None
    
    if not bool(newRow['variantAssessmentNotes']):
      newRow['variantAssessmentNotes'] = None
    
    # flatten databaseReferences
    if 'databaseReferences' in newRow:
      if bool(newRow['databaseReferences']):
        for key in newRow['databaseReferences'].keys():
          newRow[f'databaseReferences_{key}'] = newRow['databaseReferences'][key]
        del newRow['databaseReferences']
    
    # flatten classification tree labels
    if 'classificationTreeLabelsScore' in newRow:
      if bool(newRow['classificationTreeLabelsScore']):
        newRow['classificationTreeLabels'] = newRow['classificationTreeLabelsScore']['labels']
        newRow['classificationTreeScores'] = newRow['classificationTreeLabelsScore']['score']
        del newRow['classificationTreeLabelsScore']
      
    # for now, convert customfields to a json stringified object
    if 'customFields' in newRow:
      if bool(newRow['customFields']):
        newRow['customFields'] = json.dumps(newRow['customFields'])
    
    # flatten externalDatabases
    if 'externalDatabases' in newRow:
      if bool(newRow['externalDatabases']):
        for key in newRow['externalDatabases'].keys():
          newKey = cleanKeyName(key)
          newRow[f'_{newKey}'] = newRow['externalDatabases'][key]
        del newRow['externalDatabases']
    
    # flatten platformDatasets
    if 'platformDatasets' in newRow:
      if bool(newRow['platformDatasets']):
        for key in newRow['platformDatasets'].keys():
          newKey = cleanKeyName(key)
          newRow[f'_{newKey}'] = newRow['platformDatasets'][key]
        del newRow['platformDatasets']
  
    # set api records
    newRow['hasError'] = False
    newRow['dateFirstRun'] = today()
    newRow['dateLastUpdated'] = today()

    variantdata.append(newRow)
    
# convert to datatable object
variantsDT = dt.Frame(variantdata)
variantsDT[:, dt.update(patientId=as_type(f.patientId, str))]

#///////////////////////////////////////////////////////////////////////////////

# ~ 6 ~ 
# Merge datasets

# ~ 6a ~
# merge patient info
patientIDs = patientsDT['alissaInternalID'].to_list()[0]
variantPatientIDs = variantsDT['patientId'].to_list()[0]

for id in tqdm(variantPatientIDs):
  if id in patientIDs:
    refRow = patientsDT[f.alissaInternalID==id, :]
    variantsDT[f.patientId==id,'umcgNr'] = refRow['umcgNr'].to_list()[0]
    variantsDT[f.patientId==id,'accessionNumber'] = refRow['accessionNr'].to_list()[0]
  else:
    raise SystemError(f'Error: {id} not found in patients dataset')

# ~ 6b ~
# merge analysis info

# prep analyses dataset
for row in analysesByPatient:
  if 'targetPanelNames' in row:
    if isinstance(row['targetPanelNames'], list):
      row['targetPanelNames'] = ','.join(row['targetPanelNames'])
analysisDT = dt.Frame(analysesByPatient)


analysisDT[:, dt.update(analysisId = as_type(f.analysisId, str))]
variantsDT[:, dt.update(analysisId = as_type(f.analysisId, str))]

analysisIDs = analysisDT['analysisId'].to_list()[0]
variantAnalysisIDs = variantsDT['analysisId'].to_list()[0]


for id in tqdm(variantAnalysisIDs):
  if id in analysisIDs:
    refRow = analysisDT[f.analysisId==id,:]
    variantsDT[f.analysisId==id,'analysisReference'] = refRow['reference'].to_list()[0]
    variantsDT[f.analysisId==id,'analysisType'] = refRow['analysisType'].to_list()[0]
    variantsDT[f.analysisId==id,'status'] = refRow['status'].to_list()[0]
    variantsDT[f.analysisId==id,'domainName'] = refRow['domainName'].to_list()[0]
    variantsDT[f.analysisId==id,'genomeBuild'] = refRow['genomeBuild'].to_list()[0]
    variantsDT[f.analysisId==id,'analysisPipelineName'] = refRow['analysisPipelineName'].to_list()[0]
    variantsDT[f.analysisId==id,'classificationTreeName'] = refRow['classificationTreeName'].to_list()[0]
    variantsDT[f.analysisId==id,'targetPanelNames'] = refRow['targetPanelNames'].to_list()[0]
  else:
    raise SystemError(f"Error '{id}' not found in analysis dataset")

variantsDT['dateRetrieved'] = today()

# import 
# cosas.delete('alissa_variantexports')
cosas.importDatatableAsCsv(
  pkg_entity='alissa_variantexports',
  data = variantsDT
)