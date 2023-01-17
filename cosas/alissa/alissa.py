#//////////////////////////////////////////////////////////////////////////////
# FILE: alissa.py
# AUTHOR: David Ruvolo
# CREATED: 2022-04-19
# MODIFIED: 2023-01-13
# PURPOSE: fetch data from alissa
# STATUS: experimental
# PACKAGES: cosas.api.alissa, dotenv, os, requests
# COMMENTS: The purpose of this script is to extract variant information for
# all patients, or a subset of patients, from the UMCG instance of Alissa
# Interpret. To extract classifications, you must run a series of requests.
# These steps are outlined below.
# 
# 1. Get patients
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

from cosas.alissa.client import Alissa
from dotenv import load_dotenv
from datetime import datetime
from os import environ
from tqdm import tqdm
import requests
import json
load_dotenv()

def to_json(path, data):
  """Write data to json format"""
  with open(path,'w') as file:
    json.dump(data, file)
  file.close()

def now():
  """Timestamp"""
  return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# define object to store logs
messages = {'variantExportId': [], 'variantExportData': []}

# Connect to the UMCG instance of Alissa Interpret
#
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
# GET PATIENTS
# In the UMCG of Alissa, extract all identifiers of patients registered in the
# system. Add additional request paramaters as needed or filter data after
# the request has completed.

# ~ Standard Approach ~
# for now, grab a subset patients using ISO 8601 date-time. Make sure you pick
# a datetime range far enough in the past so it wont effect current records.
# patients = alissa.getPatients(
#   createdAfter="2020-02-25T00:00:00.000+00:00",
#   createdBefore="2020-02-26T00:00:00.000+00:00"
# )

# extract the identifiers. These values aren't the actual 'patient identifiers',
# they are the internal record identifiers that Alissa generates. This is
# required in order to retrieve any other information.
# patientIdentifiers=[patient['id'] for patient in patients]

# ~ Manualy Approach ~
# alternatively, manually enter IDs
patientIdentifiers=[  ]

patientInfo = []
for id in tqdm(patientIdentifiers):
  patientResponse = alissa.getPatientByInternalId(patientId=id)
  if patientResponse:
    patientInfo.append(patientResponse)

# ~ 2 ~
# GET ANALYSES BY PATIENT
#
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
    msg = f"For patient {analysisRow['patientId']} and analysis {analysisRow['analysisId']}, an ID exists, but no information could be retrieved."
    if not (msg in messages['variantExportId']):
      messages['variantExportId'].append(msg)
      del msg

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
        variantExport.append(export)
      if isinstance(exportResponse, list):
        for export in exportResponse:
          export['patientId'] = variantRow['patientId']
          export['analysisId'] = variantRow['analysisId']
          export['variantExportId'] = variantRow['exportId']
          variantExport.append(export)
  except requests.exceptions.HTTPError as error:
    msg=f"For patient {variantRow['patientId']} and analysis {variantRow['analysisId']}, an exportId exists, but no information could be retrieved."
    if not (msg in messages['variantExportData']):
      messages['variantExportData'].append(msg)

#///////////////////////////////////////////////////////////////////////////////

# save data
to_json('private/alissa_export/2023_01_13/patients.json', patientInfo)
to_json('private/alissa_export/2023_01_13/analyses.json', analysesByPatient)
to_json('private/alissa_export/2023_01_13/variantIds.json', variantExportsByAnalyses)
to_json('private/alissa_export/2023_01_13/variants.json', variantExport)
to_json('private/alissa_export/2023_01_13/logs.json', messages)
