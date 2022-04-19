#//////////////////////////////////////////////////////////////////////////////
# FILE: alissa.py
# AUTHOR: David Ruvolo
# CREATED: 2022-04-19
# MODIFIED: 2022-04-19
# PURPOSE: fetch data from alissa
# STATUS: experimental
# PACKAGES: 
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

# for dev only
from dotenv import load_dotenv
from os import environ
load_dotenv()

db = Alissa(environ['ALISSA_HOST'])
db.login(username='druvolo',password=environ['ALISSA_PASSWORD'])


# ~ 1 ~
# GET PATIENTS
# In the UMCG of Alissa, extract all identifiers of patients registered in the
# system. Add additional request paramaters as needed or filter data after
# the request has completed.

patients = db.getPatients()

# ~ 2 ~
# GET ANALYSES BY PATIENT
# For all patients defined in the previous step, extract all available analysis
# information

# TODO: What is the name of patient- and analysis identifier attribute?
analysesByPatient = []
for patient in patients:
    response = db.getPatientAnalyses(patientId=patient[''])
    if response.get(''):
        for analysis in response.get():
            analysesByPatient.append({
                'patientId': patient[''],
                'analysisId': analysis['']
            })
            
# ~ 3 ~
# GET VARIANT EXPORT IDs
# Using the patient-analysis identifier, get all variant export identifiers.
# This step will create an object where each row is one patient, analysis, and
# variant export (long format).

# TODO: what are the attribute names for patient and analysis identifier?
variantExportsByAnalyses = []
for analysis in analysesByPatient:
    response = db.getPatientVariantExportId(analysisId=analysis['analysisId'])
    if response:
        for export in response:
            variantExportsByAnalyses.append({
                'patientId': analysis.get('patientId'),
                'analysisId': analysis.get('analysisId'),
                'exportId': export.get('exportId')
            })

# ~ 4 ~
# GET VARIANT EXPORT REPORTS
# Now that a list of variant export reports has been compiled, it is possible
# to retrieve the variant export report for the patient and analysis.

variantExport = []
for variantExport in variantExportsByAnalyses:
    response = db.getPatientVariantExportData(
        analysisId=variantExport['analysisId'],
        exportId=variantExport['exportId']
    )
    if response:
        response['patientId'] = variantExport['patientId']
        response['analysisId'] = variantExport['analysisId']
        response['exportId'] = variantExport['exportId']
        variantExport.append(response)
