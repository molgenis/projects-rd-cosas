#//////////////////////////////////////////////////////////////////////////////
# FILE: alissa.py
# AUTHOR: David Ruvolo
# CREATED: 2022-04-19
# MODIFIED: 2022-05-19
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

from cosas.api.alissa import Alissa
from dotenv import load_dotenv
from os import environ
import requests
load_dotenv()

# Connect to the UMCG instance of Alissa Interpret
#
# NOTE: Credentials are stored in the vault, but you will need your own API
# username and password. This information can be generated if you have been
# given admin rights in Alissa.
#   
alissa = Alissa(
    host=environ['ALISSA_HOST'],
    clientId=environ['ALISSA_CLIENT_ID'],
    clientSecret=environ['ALISSA_CLIENT_SECRET'],
    username=environ['ALISSA_USERNAME'],
    password=environ['ALISSA_PASSWORD']
)


# ~ 1 ~
# GET PATIENTS
# In the UMCG of Alissa, extract all identifiers of patients registered in the
# system. Add additional request paramaters as needed or filter data after
# the request has completed.

# for now, grab a subset patients using ISO 8601 date-time. Make sure you pick
# a datetime range far enough in the past so it wont effect current records.
patients = alissa.getPatients(
    createdAfter="2019-01-01T00:00:00.000+00:00",
    createdBefore="2019-01-02T00:00:00.000+00:00"
)

# extract the identifiers. These values aren't the actual 'patient identifiers',
# they are the internal record identifiers that Alissa generates. This is
# required in order to retrieve any other information.
patientIdentifiers=[patient['id'] for patient in patients]


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
for id in patientIdentifiers:
    response = alissa.getPatientAnalyses(patientId=id)
    if response:
        for analysis in response:
            analysesByPatient.append({
                'patientId': id,
                'analysisId': analysis['id']
            })

            
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
for row in analysesByPatient:
    try:
        response = alissa.getPatientVariantExportId(
            analysisId=row['analysisId'],
            markedForReview=True,
            markedIncludeInReport=True
        )
    except requests.exceptions.HTTPError as error:
        print(
            'For patient',row['patientId'],', the analysisId',
            row['analysisId'],'exists, but no information could be retrieved.'
        )
    if response:
        if isinstance(response, dict):
            variantExportsByAnalyses.append({
                'patientId': row['patientId'],
                'analysisId': row['analysisId'],
                'exportId': response['exportId']
            })
        elif isinstance(response, list):
            for record in response:
                variantExportsByAnalyses.append({
                    'patientId': row['patientId'],
                    'analysisId': row['analysisId'],
                    'exportId': record['exportId']
                })

# ~ 4 ~
# GET VARIANT EXPORT REPORTS
# Now that a list of variant export reports has been compiled, it is possible
# to retrieve the variant export report for the patient and analysis.

variantExport = []
for row in variantExportsByAnalyses[:2]:
    try:
        response = alissa.getPatientVariantExportData(
            analysisId=row['analysisId'],
            exportId=row['exportId']
        )
    except requests.exceptions.HTTPError as error:
        print(
            'For patient',row['patientId'],', the analysisId',
            row['analysisId'],'and exportId exists, but something went wrong.'
        )
    
    if response:
        variantExport.extend(response)
