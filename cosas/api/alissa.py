# ////////////////////////////////////////////////////////////////////////////
# FILE: alissa.py
# AUTHOR: David Ruvolo
# CREATED: 2022-04-13
# MODIFIED: 2022-04-13
# PURPOSE: custom Alissa public api client
# STATUS: experimental
# PACKAGES: requests
# COMMENTS: mini client for the Alissa Interpret Public API (v5.3) to get
# molecular variant information per patient. The `Alissa` class is designed to
# run in several steps that are controlled by the user. In order to extract
# the data, you must execute these methods in the following way.
#
#   1. `login`: Login
#   2. `getPatients`: Get all patients and extract patient IDs
#   3. `getPatientAnalyses`: For each patient, get all analyses and extract
#           analysis identifiers
#   4. `getPatientVariantExportId`: For each analysis, get all variant exports
#           and extract all export identifiers
#   5. `getPatientVariantExportData`: For each export identifier, get variant
#           data.
#
# Steps 3 to 5 can be run only if you have the patient, analysis, and export
# identifiers.
#
# All Alissa Public API parameters listed in the documentation are supported.
# Each method returns all records unless filters have been supplied. Additional
# processing can be done in between each request.
# ////////////////////////////////////////////////////////////////////////////

import requests
import json


class Alissa:
    def __init__(self, host):
        """Alissa Interpret Public API (v5.3)
        A mini api client to get molecular variant information per patient.

        @param host The url of your Alissa Interpret instance
        @return class
        """
        self.session = requests.Session()
        self.host = host
        self.endpoints = {
            'login': f'{self.host}/auth/oauth/token',
            'patients': f'{self.host}/api/2/patients',
            'patient_analyses': f'{self.host}/api/2/patient_analyses/'
        }
        self._headers = {}

    def _argsToStringParameters(self, parameters: dict) -> str:
        return '&'.join(
            f'q={key}={parameters[key]}'
            for key in parameters.keys()
            if (key != 'self') and (parameters[key] is not None)
        )

    def login(self, username: str, password: str):
        """Login
        Get Auth token.

        @param username client ID
        @param password client secret

        @return status, string containing authorization token
        """
        try:
            response = self.session.post(
                url=self.endpoints.get('login'),
                headers={
                    'Content-Types': 'multipart/form-data',
                    'Authorization': f'Basic {password}'
                },
                data={
                    'grant_type': 'password',
                    'username': username,
                    'password': password
                }
            )
            response.raise_for_status()
            if response.status_code // 100 == 2:
                print('Logged in as', username)
                data = response.json()
                self._token = data.get('access_token')
                self._headers = {
                    'Authorization': f"{data.get('token_type')} {data.get('access_token')}"
                }
        except requests.exceptions.HTTPError as error:
            raise SystemError(error)

    def getPatients(
        self,
        accessionNumber: str = None,
        createdAfter: str = None,
        createdBefore: str = None,
        createdBy: str = None,
        familyIdentifier: str = None,
        lastUpdatedAfter: str = None,
        lastUpdatedBefore: str = None,
        lastUpdatedBy: str = None
    ) -> dict:
        """Get Patients
        Get all patients. When filter criteria are provided, the result is
        limited to the patients matching the criteria.

        @param accessionNumber The unique identifier of the patient
        @param createdAfter Filter patients with a creation date after the
            specific date time (ISO 8601 date time format)
        @param createdBefore Filter patients with a creation date before the
            specific date time (ISO 8601 date time format)
        @param createdBy User that created the patient
        @param familyIdentifier The unique identifier of the family.
        @param lastUpdatedAfter Filter patients with a last updated date after
            the specified date time (ISO 8601 date time format)
        @param lastUpdatedBefore Filter patients with a last updated date before
            the specified date time (ISO 8601 date time format)
        @param lastUpdatedBy User that updated the patient.

        @return dictionary containing one or more patient records
        """
        apiQueryString = self._argsToStringParameters(locals())
        url = self.endpoints.get('patients')
        if apiQueryString:
            url = f'{url}?{apiQueryString}'

        try:
            response = self.session.get(
                url=url,
                headers=self._headers
            )
            response.raise_for_status()
            if response.status_code // 100 == 2:
                data = response.json()
                print('Returned', len(data), 'records')
                return data
        except requests.exceptions.HTTPError as error:
            raise SystemError(error)

    def getPatientAnalyses(self, patientId: str) -> dict:
        """Get Analyses of Patient
        Get all analyses of a patient

        @param patientId The unique internal identifier of the patient

        @return dictionary containing metadata for one or more analyses
        """
        url = f"{self.endpoints.get('patients')}/patientId/analyses"
        try:
            response = self.session.get(url=url, headers=self._headers)
            response.raise_for_status()
            if response.status_code // 100 == 2:
                data = response.json()
                print('Returned', len(data), 'records')
                return data
        except requests.exceptions.HTTPError as error:
            raise SystemError(error)

    def getPatientVariantExportId(self, analysisId: int, markedForReview: bool = None, markedIncludeInReport: bool = None) -> dict:
        """Request Patient Molecular Variants Export
        Request an export of all variants. When filter criteria are provided,
        the result is limited to the variants matching the criteria.

        @param analysisId ID of the analysis
        @param markedForReview Is the variant marked for review
        @param markedIncludeInReport Is the variant included in the report

        @param dictionary containing the export identifier
        """
        url = f"{self.endpoints.get('patient_analyses')}/{analysisId}/molecular_variants/exports"

        data = {}
        if markedForReview is not None:
            data['markedForReview'] = markedForReview
        if markedIncludeInReport is not None:
            data['markedIncludeInReport'] = markedIncludeInReport

        try:
            response = self.session.post(
                url=url,
                headers=self._headers,
                data=json.dumps(data)
            )
            response.raise_for_status()
            if response.status_code // 100 == 2:
                data = response.json()
                return data.get('exportId')
        except requests.exceptions.HTTPError as error:
            raise SystemError(error)

    def getPatientVariantExportData(self, analysisId: int, exportId: str) -> dict:
        """Get Patient Molecular Variants Export
        Get the exported variants of a patient analysis via the export ID
        returned when requesting the export.

        @param analysisId The unique internal identifier of an analysis
        @param exportId The unique internal identifier of the export

        @return dictionary containing the molecular variant export data from a
            single analysis of one patient
        """
        url = f"{self.endpoints.get('patient_analyses')}/{analysisId}/molecular_variants/exports/{exportId}"
        try:
            response = self.session.get(url=url, headers=self._headers)
            response.raise_for_status()
            if response.status_code // 100 == 2:
                return response.json()
        except requests.exceptions.HTTPError as error:
            raise SystemError(error)
