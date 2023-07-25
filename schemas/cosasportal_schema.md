# Model Schema

## Packages

| Name | Description | Parent |
|:---- |:-----------|:------|
| cosasportal | Staging tables for raw data exports (v2.1.0, 2023-07-24) | - |

## Entities

| Name | Description | Package |
|:---- |:-----------|:-------|
| template | attribute template for staging tables | cosasportal |
| cartagenia | Processed Cartagenia CNV bench data | cosasportal |
| consent | Raw consent information open-exoom en 5PGM | cosasportal |
| diagnoses | Raw diagnostic metadata | cosasportal |
| export | - | cosasportal |
| files | Raw file metadata | cosasportal |
| labs_array_adlas | Raw array metadata from ADLAS | cosasportal |
| labs_array_darwin | Raw array metadata from Darwin | cosasportal |
| labs_ngs_adlas | Raw NGS data from ADLAS | cosasportal |
| labs_ngs_darwin | Raw NSG metadata from Darwin | cosasportal |
| patients | Raw metadata for patients and families | cosasportal |
| samples | Raw data table for samples | cosasportal |

## Attributes

### Entity: cosasportal_template

attribute template for staging tables

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | auto generated row identifier | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | auto generated row identifier | string |
| recordMetadata | - | metadata is data that provides information about data. | compound |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | auto generated row identifier | string |
| recordMetadata | - | metadata is data that provides information about data. | compound |
| processed | - | The data which is modified and processed for analysis or other experiments. If True, data from the row has been imported into COSAS. | bool |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | auto generated row identifier | string |
| recordMetadata | - | metadata is data that provides information about data. | compound |
| processed | - | The data which is modified and processed for analysis or other experiments. If True, data from the row has been imported into COSAS. | bool |
| dateRecordCreated | - | The date on which the activity or entity is created. | datetime |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | auto generated row identifier | string |
| recordMetadata | - | metadata is data that provides information about data. | compound |
| processed | - | The data which is modified and processed for analysis or other experiments. If True, data from the row has been imported into COSAS. | bool |
| dateRecordCreated | - | The date on which the activity or entity is created. | datetime |
| recordCreatedBy | - | Indicates the person or authoritative body who brought the item into existence. | string |

### Entity: cosasportal_cartagenia

Processed Cartagenia CNV bench data

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | Cartagenia identifier | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | Cartagenia identifier | string |
| subjectID | - | parsed UMCG number | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | Cartagenia identifier | string |
| subjectID | - | parsed UMCG number | string |
| belongsToMother | - | parsed maternal ID (UMCG Number) | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | Cartagenia identifier | string |
| subjectID | - | parsed UMCG number | string |
| belongsToMother | - | parsed maternal ID (UMCG Number) | string |
| belongsToFamily | - | family number (may not be accurate) | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | Cartagenia identifier | string |
| subjectID | - | parsed UMCG number | string |
| belongsToMother | - | parsed maternal ID (UMCG Number) | string |
| belongsToFamily | - | family number (may not be accurate) | string |
| isFetus | - | computed fetus status | bool |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | Cartagenia identifier | string |
| subjectID | - | parsed UMCG number | string |
| belongsToMother | - | parsed maternal ID (UMCG Number) | string |
| belongsToFamily | - | family number (may not be accurate) | string |
| isFetus | - | computed fetus status | bool |
| alternativeIdentifiers | - | additional UMCG numbers detected in column 'id' | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | Cartagenia identifier | string |
| subjectID | - | parsed UMCG number | string |
| belongsToMother | - | parsed maternal ID (UMCG Number) | string |
| belongsToFamily | - | family number (may not be accurate) | string |
| isFetus | - | computed fetus status | bool |
| alternativeIdentifiers | - | additional UMCG numbers detected in column 'id' | string |
| observedPhenotype | - | HPO terms provided by Cartagenia | text |

### Entity: cosasportal_consent

Raw consent information open-exoom en 5PGM

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| analysis | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| analysis | - | - | string |
| datefilled | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| analysis | - | - | string |
| datefilled | - | - | string |
| MDN_umcgnr | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| analysis | - | - | string |
| datefilled | - | - | string |
| MDN_umcgnr | - | - | string |
| familienummer | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| analysis | - | - | string |
| datefilled | - | - | string |
| MDN_umcgnr | - | - | string |
| familienummer | - | - | string |
| request_consent_material | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| analysis | - | - | string |
| datefilled | - | - | string |
| MDN_umcgnr | - | - | string |
| familienummer | - | - | string |
| request_consent_material | - | - | string |
| request_form | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| analysis | - | - | string |
| datefilled | - | - | string |
| MDN_umcgnr | - | - | string |
| familienummer | - | - | string |
| request_consent_material | - | - | string |
| request_form | - | - | string |
| request_date_signed | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| analysis | - | - | string |
| datefilled | - | - | string |
| MDN_umcgnr | - | - | string |
| familienummer | - | - | string |
| request_consent_material | - | - | string |
| request_form | - | - | string |
| request_date_signed | - | - | string |
| consent_recontact | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| analysis | - | - | string |
| datefilled | - | - | string |
| MDN_umcgnr | - | - | string |
| familienummer | - | - | string |
| request_consent_material | - | - | string |
| request_form | - | - | string |
| request_date_signed | - | - | string |
| consent_recontact | - | - | string |
| consent_research | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| analysis | - | - | string |
| datefilled | - | - | string |
| MDN_umcgnr | - | - | string |
| familienummer | - | - | string |
| request_consent_material | - | - | string |
| request_form | - | - | string |
| request_date_signed | - | - | string |
| consent_recontact | - | - | string |
| consent_research | - | - | string |
| consent_system | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| analysis | - | - | string |
| datefilled | - | - | string |
| MDN_umcgnr | - | - | string |
| familienummer | - | - | string |
| request_consent_material | - | - | string |
| request_form | - | - | string |
| request_date_signed | - | - | string |
| consent_recontact | - | - | string |
| consent_research | - | - | string |
| consent_system | - | - | string |
| consent_form | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| analysis | - | - | string |
| datefilled | - | - | string |
| MDN_umcgnr | - | - | string |
| familienummer | - | - | string |
| request_consent_material | - | - | string |
| request_form | - | - | string |
| request_date_signed | - | - | string |
| consent_recontact | - | - | string |
| consent_research | - | - | string |
| consent_system | - | - | string |
| consent_form | - | - | string |
| consent_doctor | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| analysis | - | - | string |
| datefilled | - | - | string |
| MDN_umcgnr | - | - | string |
| familienummer | - | - | string |
| request_consent_material | - | - | string |
| request_form | - | - | string |
| request_date_signed | - | - | string |
| consent_recontact | - | - | string |
| consent_research | - | - | string |
| consent_system | - | - | string |
| consent_form | - | - | string |
| consent_doctor | - | - | string |
| consent_date_signed | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| analysis | - | - | string |
| datefilled | - | - | string |
| MDN_umcgnr | - | - | string |
| familienummer | - | - | string |
| request_consent_material | - | - | string |
| request_form | - | - | string |
| request_date_signed | - | - | string |
| consent_recontact | - | - | string |
| consent_research | - | - | string |
| consent_system | - | - | string |
| consent_form | - | - | string |
| consent_doctor | - | - | string |
| consent_date_signed | - | - | string |
| consent_folder | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| analysis | - | - | string |
| datefilled | - | - | string |
| MDN_umcgnr | - | - | string |
| familienummer | - | - | string |
| request_consent_material | - | - | string |
| request_form | - | - | string |
| request_date_signed | - | - | string |
| consent_recontact | - | - | string |
| consent_research | - | - | string |
| consent_system | - | - | string |
| consent_form | - | - | string |
| consent_doctor | - | - | string |
| consent_date_signed | - | - | string |
| consent_folder | - | - | string |
| incidental_consent_recontact | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| analysis | - | - | string |
| datefilled | - | - | string |
| MDN_umcgnr | - | - | string |
| familienummer | - | - | string |
| request_consent_material | - | - | string |
| request_form | - | - | string |
| request_date_signed | - | - | string |
| consent_recontact | - | - | string |
| consent_research | - | - | string |
| consent_system | - | - | string |
| consent_form | - | - | string |
| consent_doctor | - | - | string |
| consent_date_signed | - | - | string |
| consent_folder | - | - | string |
| incidental_consent_recontact | - | - | string |
| incidental_form | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| analysis | - | - | string |
| datefilled | - | - | string |
| MDN_umcgnr | - | - | string |
| familienummer | - | - | string |
| request_consent_material | - | - | string |
| request_form | - | - | string |
| request_date_signed | - | - | string |
| consent_recontact | - | - | string |
| consent_research | - | - | string |
| consent_system | - | - | string |
| consent_form | - | - | string |
| consent_doctor | - | - | string |
| consent_date_signed | - | - | string |
| consent_folder | - | - | string |
| incidental_consent_recontact | - | - | string |
| incidental_form | - | - | string |
| incidental_date_signed | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| analysis | - | - | string |
| datefilled | - | - | string |
| MDN_umcgnr | - | - | string |
| familienummer | - | - | string |
| request_consent_material | - | - | string |
| request_form | - | - | string |
| request_date_signed | - | - | string |
| consent_recontact | - | - | string |
| consent_research | - | - | string |
| consent_system | - | - | string |
| consent_form | - | - | string |
| consent_doctor | - | - | string |
| consent_date_signed | - | - | string |
| consent_folder | - | - | string |
| incidental_consent_recontact | - | - | string |
| incidental_form | - | - | string |
| incidental_date_signed | - | - | string |
| id&#8251; | - | - | string |

### Entity: cosasportal_diagnoses

Raw diagnostic metadata

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| HOOFDDIAGNOSE | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| HOOFDDIAGNOSE | - | - | string |
| HOOFDDIAGNOSE_ZEKERHEID | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| HOOFDDIAGNOSE | - | - | string |
| HOOFDDIAGNOSE_ZEKERHEID | - | - | string |
| EXTRA_DIAGNOSE | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| HOOFDDIAGNOSE | - | - | string |
| HOOFDDIAGNOSE_ZEKERHEID | - | - | string |
| EXTRA_DIAGNOSE | - | - | string |
| EXTRA_DIAGNOSE_ZEKERHEID | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| HOOFDDIAGNOSE | - | - | string |
| HOOFDDIAGNOSE_ZEKERHEID | - | - | string |
| EXTRA_DIAGNOSE | - | - | string |
| EXTRA_DIAGNOSE_ZEKERHEID | - | - | string |
| DATUM_EERSTE_CONSULT | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| HOOFDDIAGNOSE | - | - | string |
| HOOFDDIAGNOSE_ZEKERHEID | - | - | string |
| EXTRA_DIAGNOSE | - | - | string |
| EXTRA_DIAGNOSE_ZEKERHEID | - | - | string |
| DATUM_EERSTE_CONSULT | - | - | string |
| OND_ID | - | - | string |

### Entity: cosasportal_export

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| datumTijd | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| datumTijd | - | - | string |
| vraag | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| datumTijd | - | - | string |
| vraag | - | - | string |
| antwoordregel | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| datumTijd | - | - | string |
| vraag | - | - | string |
| antwoordregel | - | - | string |
| antwoord | - | - | text |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| datumTijd | - | - | string |
| vraag | - | - | string |
| antwoordregel | - | - | string |
| antwoord | - | - | text |
| UMCGnr | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| datumTijd | - | - | string |
| vraag | - | - | string |
| antwoordregel | - | - | string |
| antwoord | - | - | text |
| UMCGnr | - | - | string |
| dateOfBirth | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| datumTijd | - | - | string |
| vraag | - | - | string |
| antwoordregel | - | - | string |
| antwoord | - | - | text |
| UMCGnr | - | - | string |
| dateOfBirth | - | - | string |
| dateOfDeath | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| datumTijd | - | - | string |
| vraag | - | - | string |
| antwoordregel | - | - | string |
| antwoord | - | - | text |
| UMCGnr | - | - | string |
| dateOfBirth | - | - | string |
| dateOfDeath | - | - | string |
| isFetus | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| datumTijd | - | - | string |
| vraag | - | - | string |
| antwoordregel | - | - | string |
| antwoord | - | - | text |
| UMCGnr | - | - | string |
| dateOfBirth | - | - | string |
| dateOfDeath | - | - | string |
| isFetus | - | - | string |
| biologicalSex | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| datumTijd | - | - | string |
| vraag | - | - | string |
| antwoordregel | - | - | string |
| antwoord | - | - | text |
| UMCGnr | - | - | string |
| dateOfBirth | - | - | string |
| dateOfDeath | - | - | string |
| isFetus | - | - | string |
| biologicalSex | - | - | string |
| firstConsultDate | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| datumTijd | - | - | string |
| vraag | - | - | string |
| antwoordregel | - | - | string |
| antwoord | - | - | text |
| UMCGnr | - | - | string |
| dateOfBirth | - | - | string |
| dateOfDeath | - | - | string |
| isFetus | - | - | string |
| biologicalSex | - | - | string |
| firstConsultDate | - | - | string |
| isTwin | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| datumTijd | - | - | string |
| vraag | - | - | string |
| antwoordregel | - | - | string |
| antwoord | - | - | text |
| UMCGnr | - | - | string |
| dateOfBirth | - | - | string |
| dateOfDeath | - | - | string |
| isFetus | - | - | string |
| biologicalSex | - | - | string |
| firstConsultDate | - | - | string |
| isTwin | - | - | string |
| polihoofdbehandelaar | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| datumTijd | - | - | string |
| vraag | - | - | string |
| antwoordregel | - | - | string |
| antwoord | - | - | text |
| UMCGnr | - | - | string |
| dateOfBirth | - | - | string |
| dateOfDeath | - | - | string |
| isFetus | - | - | string |
| biologicalSex | - | - | string |
| firstConsultDate | - | - | string |
| isTwin | - | - | string |
| polihoofdbehandelaar | - | - | string |
| _id&#8251; | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| datumTijd | - | - | string |
| vraag | - | - | string |
| antwoordregel | - | - | string |
| antwoord | - | - | text |
| UMCGnr | - | - | string |
| dateOfBirth | - | - | string |
| dateOfDeath | - | - | string |
| isFetus | - | - | string |
| biologicalSex | - | - | string |
| firstConsultDate | - | - | string |
| isTwin | - | - | string |
| polihoofdbehandelaar | - | - | string |
| _id&#8251; | - | - | string |
| _importedOn | - | - | date |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| datumTijd | - | - | string |
| vraag | - | - | string |
| antwoordregel | - | - | string |
| antwoord | - | - | text |
| UMCGnr | - | - | string |
| dateOfBirth | - | - | string |
| dateOfDeath | - | - | string |
| isFetus | - | - | string |
| biologicalSex | - | - | string |
| firstConsultDate | - | - | string |
| isTwin | - | - | string |
| polihoofdbehandelaar | - | - | string |
| _id&#8251; | - | - | string |
| _importedOn | - | - | date |
| _processed | - | - | bool |

### Entity: cosasportal_files

Raw file metadata

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | auto generated identifier | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | auto generated identifier | string |
| umcgID | - | Internal patient identifier | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | auto generated identifier | string |
| umcgID | - | Internal patient identifier | string |
| familyID | - | family identifier of the patient | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | auto generated identifier | string |
| umcgID | - | Internal patient identifier | string |
| familyID | - | family identifier of the patient | string |
| dnaID | - | sample identifier | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | auto generated identifier | string |
| umcgID | - | Internal patient identifier | string |
| familyID | - | family identifier of the patient | string |
| dnaID | - | sample identifier | string |
| testID | - | test code that indicates the lab procedure | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | auto generated identifier | string |
| umcgID | - | Internal patient identifier | string |
| familyID | - | family identifier of the patient | string |
| dnaID | - | sample identifier | string |
| testID | - | test code that indicates the lab procedure | string |
| filename | - | name of the file | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | auto generated identifier | string |
| umcgID | - | Internal patient identifier | string |
| familyID | - | family identifier of the patient | string |
| dnaID | - | sample identifier | string |
| testID | - | test code that indicates the lab procedure | string |
| filename | - | name of the file | string |
| filepath | - | location of the file | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | auto generated identifier | string |
| umcgID | - | Internal patient identifier | string |
| familyID | - | family identifier of the patient | string |
| dnaID | - | sample identifier | string |
| testID | - | test code that indicates the lab procedure | string |
| filename | - | name of the file | string |
| filepath | - | location of the file | string |
| filetype | - | file format | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | auto generated identifier | string |
| umcgID | - | Internal patient identifier | string |
| familyID | - | family identifier of the patient | string |
| dnaID | - | sample identifier | string |
| testID | - | test code that indicates the lab procedure | string |
| filename | - | name of the file | string |
| filepath | - | location of the file | string |
| filetype | - | file format | string |
| md5 | - | checksum of the file | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | auto generated identifier | string |
| umcgID | - | Internal patient identifier | string |
| familyID | - | family identifier of the patient | string |
| dnaID | - | sample identifier | string |
| testID | - | test code that indicates the lab procedure | string |
| filename | - | name of the file | string |
| filepath | - | location of the file | string |
| filetype | - | file format | string |
| md5 | - | checksum of the file | string |
| dateCreated | - | date the file was created | string |

### Entity: cosasportal_labs_array_adlas

Raw array metadata from ADLAS

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| SGA_CLASSIFICATION | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| SGA_CLASSIFICATION | - | - | string |
| SGA_CYTOBAND | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| SGA_CLASSIFICATION | - | - | string |
| SGA_CYTOBAND | - | - | string |
| SGA_DECIPHER_SYNDROMES | - | - | text |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| SGA_CLASSIFICATION | - | - | string |
| SGA_CYTOBAND | - | - | string |
| SGA_DECIPHER_SYNDROMES | - | - | text |
| SGA_DGV_SIMILARITY | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| SGA_CLASSIFICATION | - | - | string |
| SGA_CYTOBAND | - | - | string |
| SGA_DECIPHER_SYNDROMES | - | - | text |
| SGA_DGV_SIMILARITY | - | - | string |
| SGA_EVENT | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| SGA_CLASSIFICATION | - | - | string |
| SGA_CYTOBAND | - | - | string |
| SGA_DECIPHER_SYNDROMES | - | - | text |
| SGA_DGV_SIMILARITY | - | - | string |
| SGA_EVENT | - | - | string |
| SGA_EVIDENCE_SCORE | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| SGA_CLASSIFICATION | - | - | string |
| SGA_CYTOBAND | - | - | string |
| SGA_DECIPHER_SYNDROMES | - | - | text |
| SGA_DGV_SIMILARITY | - | - | string |
| SGA_EVENT | - | - | string |
| SGA_EVIDENCE_SCORE | - | - | string |
| SGA_HMRELATED_GENES | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| SGA_CLASSIFICATION | - | - | string |
| SGA_CYTOBAND | - | - | string |
| SGA_DECIPHER_SYNDROMES | - | - | text |
| SGA_DGV_SIMILARITY | - | - | string |
| SGA_EVENT | - | - | string |
| SGA_EVIDENCE_SCORE | - | - | string |
| SGA_HMRELATED_GENES | - | - | string |
| SGA_HMRELATED_GENES_COUNT | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| SGA_CLASSIFICATION | - | - | string |
| SGA_CYTOBAND | - | - | string |
| SGA_DECIPHER_SYNDROMES | - | - | text |
| SGA_DGV_SIMILARITY | - | - | string |
| SGA_EVENT | - | - | string |
| SGA_EVIDENCE_SCORE | - | - | string |
| SGA_HMRELATED_GENES | - | - | string |
| SGA_HMRELATED_GENES_COUNT | - | - | string |
| SGA_LENGTH | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| SGA_CLASSIFICATION | - | - | string |
| SGA_CYTOBAND | - | - | string |
| SGA_DECIPHER_SYNDROMES | - | - | text |
| SGA_DGV_SIMILARITY | - | - | string |
| SGA_EVENT | - | - | string |
| SGA_EVIDENCE_SCORE | - | - | string |
| SGA_HMRELATED_GENES | - | - | string |
| SGA_HMRELATED_GENES_COUNT | - | - | string |
| SGA_LENGTH | - | - | string |
| SGA_MOSAIC | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| SGA_CLASSIFICATION | - | - | string |
| SGA_CYTOBAND | - | - | string |
| SGA_DECIPHER_SYNDROMES | - | - | text |
| SGA_DGV_SIMILARITY | - | - | string |
| SGA_EVENT | - | - | string |
| SGA_EVIDENCE_SCORE | - | - | string |
| SGA_HMRELATED_GENES | - | - | string |
| SGA_HMRELATED_GENES_COUNT | - | - | string |
| SGA_LENGTH | - | - | string |
| SGA_MOSAIC | - | - | string |
| SGA_MOSAIC_PERCENTAGE | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| SGA_CLASSIFICATION | - | - | string |
| SGA_CYTOBAND | - | - | string |
| SGA_DECIPHER_SYNDROMES | - | - | text |
| SGA_DGV_SIMILARITY | - | - | string |
| SGA_EVENT | - | - | string |
| SGA_EVIDENCE_SCORE | - | - | string |
| SGA_HMRELATED_GENES | - | - | string |
| SGA_HMRELATED_GENES_COUNT | - | - | string |
| SGA_LENGTH | - | - | string |
| SGA_MOSAIC | - | - | string |
| SGA_MOSAIC_PERCENTAGE | - | - | string |
| SGA_NO_OF_PROBES | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| SGA_CLASSIFICATION | - | - | string |
| SGA_CYTOBAND | - | - | string |
| SGA_DECIPHER_SYNDROMES | - | - | text |
| SGA_DGV_SIMILARITY | - | - | string |
| SGA_EVENT | - | - | string |
| SGA_EVIDENCE_SCORE | - | - | string |
| SGA_HMRELATED_GENES | - | - | string |
| SGA_HMRELATED_GENES_COUNT | - | - | string |
| SGA_LENGTH | - | - | string |
| SGA_MOSAIC | - | - | string |
| SGA_MOSAIC_PERCENTAGE | - | - | string |
| SGA_NO_OF_PROBES | - | - | string |
| SGA_NOTES | - | - | text |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| SGA_CLASSIFICATION | - | - | string |
| SGA_CYTOBAND | - | - | string |
| SGA_DECIPHER_SYNDROMES | - | - | text |
| SGA_DGV_SIMILARITY | - | - | string |
| SGA_EVENT | - | - | string |
| SGA_EVIDENCE_SCORE | - | - | string |
| SGA_HMRELATED_GENES | - | - | string |
| SGA_HMRELATED_GENES_COUNT | - | - | string |
| SGA_LENGTH | - | - | string |
| SGA_MOSAIC | - | - | string |
| SGA_MOSAIC_PERCENTAGE | - | - | string |
| SGA_NO_OF_PROBES | - | - | string |
| SGA_NOTES | - | - | text |
| SGA_OMIM_MORBID_MAP | - | - | text |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| SGA_CLASSIFICATION | - | - | string |
| SGA_CYTOBAND | - | - | string |
| SGA_DECIPHER_SYNDROMES | - | - | text |
| SGA_DGV_SIMILARITY | - | - | string |
| SGA_EVENT | - | - | string |
| SGA_EVIDENCE_SCORE | - | - | string |
| SGA_HMRELATED_GENES | - | - | string |
| SGA_HMRELATED_GENES_COUNT | - | - | string |
| SGA_LENGTH | - | - | string |
| SGA_MOSAIC | - | - | string |
| SGA_MOSAIC_PERCENTAGE | - | - | string |
| SGA_NO_OF_PROBES | - | - | string |
| SGA_NOTES | - | - | text |
| SGA_OMIM_MORBID_MAP | - | - | text |
| SGA_OMIM_MORBIDMAP_COUNT | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| SGA_CLASSIFICATION | - | - | string |
| SGA_CYTOBAND | - | - | string |
| SGA_DECIPHER_SYNDROMES | - | - | text |
| SGA_DGV_SIMILARITY | - | - | string |
| SGA_EVENT | - | - | string |
| SGA_EVIDENCE_SCORE | - | - | string |
| SGA_HMRELATED_GENES | - | - | string |
| SGA_HMRELATED_GENES_COUNT | - | - | string |
| SGA_LENGTH | - | - | string |
| SGA_MOSAIC | - | - | string |
| SGA_MOSAIC_PERCENTAGE | - | - | string |
| SGA_NO_OF_PROBES | - | - | string |
| SGA_NOTES | - | - | text |
| SGA_OMIM_MORBID_MAP | - | - | text |
| SGA_OMIM_MORBIDMAP_COUNT | - | - | string |
| SGA_PROBE_MEDIAN | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| SGA_CLASSIFICATION | - | - | string |
| SGA_CYTOBAND | - | - | string |
| SGA_DECIPHER_SYNDROMES | - | - | text |
| SGA_DGV_SIMILARITY | - | - | string |
| SGA_EVENT | - | - | string |
| SGA_EVIDENCE_SCORE | - | - | string |
| SGA_HMRELATED_GENES | - | - | string |
| SGA_HMRELATED_GENES_COUNT | - | - | string |
| SGA_LENGTH | - | - | string |
| SGA_MOSAIC | - | - | string |
| SGA_MOSAIC_PERCENTAGE | - | - | string |
| SGA_NO_OF_PROBES | - | - | string |
| SGA_NOTES | - | - | text |
| SGA_OMIM_MORBID_MAP | - | - | text |
| SGA_OMIM_MORBIDMAP_COUNT | - | - | string |
| SGA_PROBE_MEDIAN | - | - | string |
| SGA_REFSEQ_CODING_GENES | - | - | text |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| SGA_CLASSIFICATION | - | - | string |
| SGA_CYTOBAND | - | - | string |
| SGA_DECIPHER_SYNDROMES | - | - | text |
| SGA_DGV_SIMILARITY | - | - | string |
| SGA_EVENT | - | - | string |
| SGA_EVIDENCE_SCORE | - | - | string |
| SGA_HMRELATED_GENES | - | - | string |
| SGA_HMRELATED_GENES_COUNT | - | - | string |
| SGA_LENGTH | - | - | string |
| SGA_MOSAIC | - | - | string |
| SGA_MOSAIC_PERCENTAGE | - | - | string |
| SGA_NO_OF_PROBES | - | - | string |
| SGA_NOTES | - | - | text |
| SGA_OMIM_MORBID_MAP | - | - | text |
| SGA_OMIM_MORBIDMAP_COUNT | - | - | string |
| SGA_PROBE_MEDIAN | - | - | string |
| SGA_REFSEQ_CODING_GENES | - | - | text |
| SGA_REFSEQ_CODING_GENES_COUNT | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| SGA_CLASSIFICATION | - | - | string |
| SGA_CYTOBAND | - | - | string |
| SGA_DECIPHER_SYNDROMES | - | - | text |
| SGA_DGV_SIMILARITY | - | - | string |
| SGA_EVENT | - | - | string |
| SGA_EVIDENCE_SCORE | - | - | string |
| SGA_HMRELATED_GENES | - | - | string |
| SGA_HMRELATED_GENES_COUNT | - | - | string |
| SGA_LENGTH | - | - | string |
| SGA_MOSAIC | - | - | string |
| SGA_MOSAIC_PERCENTAGE | - | - | string |
| SGA_NO_OF_PROBES | - | - | string |
| SGA_NOTES | - | - | text |
| SGA_OMIM_MORBID_MAP | - | - | text |
| SGA_OMIM_MORBIDMAP_COUNT | - | - | string |
| SGA_PROBE_MEDIAN | - | - | string |
| SGA_REFSEQ_CODING_GENES | - | - | text |
| SGA_REFSEQ_CODING_GENES_COUNT | - | - | string |
| SGA_REGIONS_UMCG_CNV_NL_COUNT | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| SGA_CLASSIFICATION | - | - | string |
| SGA_CYTOBAND | - | - | string |
| SGA_DECIPHER_SYNDROMES | - | - | text |
| SGA_DGV_SIMILARITY | - | - | string |
| SGA_EVENT | - | - | string |
| SGA_EVIDENCE_SCORE | - | - | string |
| SGA_HMRELATED_GENES | - | - | string |
| SGA_HMRELATED_GENES_COUNT | - | - | string |
| SGA_LENGTH | - | - | string |
| SGA_MOSAIC | - | - | string |
| SGA_MOSAIC_PERCENTAGE | - | - | string |
| SGA_NO_OF_PROBES | - | - | string |
| SGA_NOTES | - | - | text |
| SGA_OMIM_MORBID_MAP | - | - | text |
| SGA_OMIM_MORBIDMAP_COUNT | - | - | string |
| SGA_PROBE_MEDIAN | - | - | string |
| SGA_REFSEQ_CODING_GENES | - | - | text |
| SGA_REFSEQ_CODING_GENES_COUNT | - | - | string |
| SGA_REGIONS_UMCG_CNV_NL_COUNT | - | - | string |
| SGA_SIMILAR_PREVIOUS_CASES | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| SGA_CLASSIFICATION | - | - | string |
| SGA_CYTOBAND | - | - | string |
| SGA_DECIPHER_SYNDROMES | - | - | text |
| SGA_DGV_SIMILARITY | - | - | string |
| SGA_EVENT | - | - | string |
| SGA_EVIDENCE_SCORE | - | - | string |
| SGA_HMRELATED_GENES | - | - | string |
| SGA_HMRELATED_GENES_COUNT | - | - | string |
| SGA_LENGTH | - | - | string |
| SGA_MOSAIC | - | - | string |
| SGA_MOSAIC_PERCENTAGE | - | - | string |
| SGA_NO_OF_PROBES | - | - | string |
| SGA_NOTES | - | - | text |
| SGA_OMIM_MORBID_MAP | - | - | text |
| SGA_OMIM_MORBIDMAP_COUNT | - | - | string |
| SGA_PROBE_MEDIAN | - | - | string |
| SGA_REFSEQ_CODING_GENES | - | - | text |
| SGA_REFSEQ_CODING_GENES_COUNT | - | - | string |
| SGA_REGIONS_UMCG_CNV_NL_COUNT | - | - | string |
| SGA_SIMILAR_PREVIOUS_CASES | - | - | string |
| SGA_OVERERVING | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| SGA_CHROMOSOME_REGION | - | - | string |
| SGA_CLASSIFICATION | - | - | string |
| SGA_CYTOBAND | - | - | string |
| SGA_DECIPHER_SYNDROMES | - | - | text |
| SGA_DGV_SIMILARITY | - | - | string |
| SGA_EVENT | - | - | string |
| SGA_EVIDENCE_SCORE | - | - | string |
| SGA_HMRELATED_GENES | - | - | string |
| SGA_HMRELATED_GENES_COUNT | - | - | string |
| SGA_LENGTH | - | - | string |
| SGA_MOSAIC | - | - | string |
| SGA_MOSAIC_PERCENTAGE | - | - | string |
| SGA_NO_OF_PROBES | - | - | string |
| SGA_NOTES | - | - | text |
| SGA_OMIM_MORBID_MAP | - | - | text |
| SGA_OMIM_MORBIDMAP_COUNT | - | - | string |
| SGA_PROBE_MEDIAN | - | - | string |
| SGA_REFSEQ_CODING_GENES | - | - | text |
| SGA_REFSEQ_CODING_GENES_COUNT | - | - | string |
| SGA_REGIONS_UMCG_CNV_NL_COUNT | - | - | string |
| SGA_SIMILAR_PREVIOUS_CASES | - | - | string |
| SGA_OVERERVING | - | - | string |
| FOETUS_ID | - | - | string |

### Entity: cosasportal_labs_array_darwin

Raw array metadata from Darwin

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| TestId | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| TestId | - | - | string |
| TestDatum | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| TestId | - | - | string |
| TestDatum | - | - | string |
| Indicatie | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| TestId | - | - | string |
| TestDatum | - | - | string |
| Indicatie | - | - | string |
| BatchNaam | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| TestId | - | - | string |
| TestDatum | - | - | string |
| Indicatie | - | - | string |
| BatchNaam | - | - | string |
| CallRate | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| TestId | - | - | string |
| TestDatum | - | - | string |
| Indicatie | - | - | string |
| BatchNaam | - | - | string |
| CallRate | - | - | string |
| StandaardDeviatie | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| TestId | - | - | string |
| TestDatum | - | - | string |
| Indicatie | - | - | string |
| BatchNaam | - | - | string |
| CallRate | - | - | string |
| StandaardDeviatie | - | - | string |
| Foetus_Id | - | - | string |

### Entity: cosasportal_labs_ngs_adlas

Raw NGS data from ADLAS

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| GEN | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| GEN | - | - | string |
| MUTATIE | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| GEN | - | - | string |
| MUTATIE | - | - | string |
| KLASSE | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| GEN | - | - | string |
| MUTATIE | - | - | string |
| KLASSE | - | - | string |
| NM_NUMMER | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| GEN | - | - | string |
| MUTATIE | - | - | string |
| KLASSE | - | - | string |
| NM_NUMMER | - | - | string |
| LRGS_NUMMER | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| GEN | - | - | string |
| MUTATIE | - | - | string |
| KLASSE | - | - | string |
| NM_NUMMER | - | - | string |
| LRGS_NUMMER | - | - | string |
| AMPLICON | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| GEN | - | - | string |
| MUTATIE | - | - | string |
| KLASSE | - | - | string |
| NM_NUMMER | - | - | string |
| LRGS_NUMMER | - | - | string |
| AMPLICON | - | - | string |
| ALLELFREQUENTIE | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| GEN | - | - | string |
| MUTATIE | - | - | string |
| KLASSE | - | - | string |
| NM_NUMMER | - | - | string |
| LRGS_NUMMER | - | - | string |
| AMPLICON | - | - | string |
| ALLELFREQUENTIE | - | - | string |
| OVERERVING | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| ADVVRG_ID | - | - | string |
| DNA_NUMMER | - | - | string |
| TEST_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | string |
| GEN | - | - | string |
| MUTATIE | - | - | string |
| KLASSE | - | - | string |
| NM_NUMMER | - | - | string |
| LRGS_NUMMER | - | - | string |
| AMPLICON | - | - | string |
| ALLELFREQUENTIE | - | - | string |
| OVERERVING | - | - | string |
| FOETUS_ID | - | - | string |

### Entity: cosasportal_labs_ngs_darwin

Raw NSG metadata from Darwin

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| TestId | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| TestId | - | - | string |
| TestDatum | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| TestId | - | - | string |
| TestDatum | - | - | string |
| Indicatie | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| TestId | - | - | string |
| TestDatum | - | - | string |
| Indicatie | - | - | string |
| Sequencer | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| TestId | - | - | string |
| TestDatum | - | - | string |
| Indicatie | - | - | string |
| Sequencer | - | - | string |
| PrepKit | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| TestId | - | - | string |
| TestDatum | - | - | string |
| Indicatie | - | - | string |
| Sequencer | - | - | string |
| PrepKit | - | - | string |
| SequencingType | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| TestId | - | - | string |
| TestDatum | - | - | string |
| Indicatie | - | - | string |
| Sequencer | - | - | string |
| PrepKit | - | - | string |
| SequencingType | - | - | string |
| SeqType | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| TestId | - | - | string |
| TestDatum | - | - | string |
| Indicatie | - | - | string |
| Sequencer | - | - | string |
| PrepKit | - | - | string |
| SequencingType | - | - | string |
| SeqType | - | - | string |
| CapturingKit | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| TestId | - | - | string |
| TestDatum | - | - | string |
| Indicatie | - | - | string |
| Sequencer | - | - | string |
| PrepKit | - | - | string |
| SequencingType | - | - | string |
| SeqType | - | - | string |
| CapturingKit | - | - | string |
| BatchNaam | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| TestId | - | - | string |
| TestDatum | - | - | string |
| Indicatie | - | - | string |
| Sequencer | - | - | string |
| PrepKit | - | - | string |
| SequencingType | - | - | string |
| SeqType | - | - | string |
| CapturingKit | - | - | string |
| BatchNaam | - | - | string |
| Project_Name | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| TestId | - | - | string |
| TestDatum | - | - | string |
| Indicatie | - | - | string |
| Sequencer | - | - | string |
| PrepKit | - | - | string |
| SequencingType | - | - | string |
| SeqType | - | - | string |
| CapturingKit | - | - | string |
| BatchNaam | - | - | string |
| Project_Name | - | - | string |
| GenomeBuild | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| TestId | - | - | string |
| TestDatum | - | - | string |
| Indicatie | - | - | string |
| Sequencer | - | - | string |
| PrepKit | - | - | string |
| SequencingType | - | - | string |
| SeqType | - | - | string |
| CapturingKit | - | - | string |
| BatchNaam | - | - | string |
| Project_Name | - | - | string |
| GenomeBuild | - | - | string |
| CallRate | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| TestId | - | - | string |
| TestDatum | - | - | string |
| Indicatie | - | - | string |
| Sequencer | - | - | string |
| PrepKit | - | - | string |
| SequencingType | - | - | string |
| SeqType | - | - | string |
| CapturingKit | - | - | string |
| BatchNaam | - | - | string |
| Project_Name | - | - | string |
| GenomeBuild | - | - | string |
| CallRate | - | - | string |
| StandaardDeviatie | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| TestId | - | - | string |
| TestDatum | - | - | string |
| Indicatie | - | - | string |
| Sequencer | - | - | string |
| PrepKit | - | - | string |
| SequencingType | - | - | string |
| SeqType | - | - | string |
| CapturingKit | - | - | string |
| BatchNaam | - | - | string |
| Project_Name | - | - | string |
| GenomeBuild | - | - | string |
| CallRate | - | - | string |
| StandaardDeviatie | - | - | string |
| Foetus_Id | - | - | string |

### Entity: cosasportal_patients

Raw metadata for patients and families

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| OVERLIJDENSDATUM | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| OVERLIJDENSDATUM | - | - | string |
| FAMILIENUMMER | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| OVERLIJDENSDATUM | - | - | string |
| FAMILIENUMMER | - | - | string |
| GEBOORTEDATUM | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| OVERLIJDENSDATUM | - | - | string |
| FAMILIENUMMER | - | - | string |
| GEBOORTEDATUM | - | - | string |
| GESLACHT | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| OVERLIJDENSDATUM | - | - | string |
| FAMILIENUMMER | - | - | string |
| GEBOORTEDATUM | - | - | string |
| GESLACHT | - | - | string |
| FAMILIELEDEN | - | - | text |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| OVERLIJDENSDATUM | - | - | string |
| FAMILIENUMMER | - | - | string |
| GEBOORTEDATUM | - | - | string |
| GESLACHT | - | - | string |
| FAMILIELEDEN | - | - | text |
| UMCG_MOEDER | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| OVERLIJDENSDATUM | - | - | string |
| FAMILIENUMMER | - | - | string |
| GEBOORTEDATUM | - | - | string |
| GESLACHT | - | - | string |
| FAMILIELEDEN | - | - | text |
| UMCG_MOEDER | - | - | string |
| UMCG_VADER | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| OVERLIJDENSDATUM | - | - | string |
| FAMILIENUMMER | - | - | string |
| GEBOORTEDATUM | - | - | string |
| GESLACHT | - | - | string |
| FAMILIELEDEN | - | - | text |
| UMCG_MOEDER | - | - | string |
| UMCG_VADER | - | - | string |
| FOETUS_ID | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| OVERLIJDENSDATUM | - | - | string |
| FAMILIENUMMER | - | - | string |
| GEBOORTEDATUM | - | - | string |
| GESLACHT | - | - | string |
| FAMILIELEDEN | - | - | text |
| UMCG_MOEDER | - | - | string |
| UMCG_VADER | - | - | string |
| FOETUS_ID | - | - | string |
| SAMPLEDATE | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| OVERLIJDENSDATUM | - | - | string |
| FAMILIENUMMER | - | - | string |
| GEBOORTEDATUM | - | - | string |
| GESLACHT | - | - | string |
| FAMILIELEDEN | - | - | text |
| UMCG_MOEDER | - | - | string |
| UMCG_VADER | - | - | string |
| FOETUS_ID | - | - | string |
| SAMPLEDATE | - | - | string |
| DISEASED | - | - | string |

### Entity: cosasportal_samples

Raw data table for samples

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMMER | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMMER | - | - | string |
| ADVVRG_ID | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMMER | - | - | string |
| ADVVRG_ID | - | - | string |
| ADVIESVRAAG_DATUM | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMMER | - | - | string |
| ADVVRG_ID | - | - | string |
| ADVIESVRAAG_DATUM | - | - | string |
| MONSTER_ID | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMMER | - | - | string |
| ADVVRG_ID | - | - | string |
| ADVIESVRAAG_DATUM | - | - | string |
| MONSTER_ID | - | - | string |
| TEST_CODE | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMMER | - | - | string |
| ADVVRG_ID | - | - | string |
| ADVIESVRAAG_DATUM | - | - | string |
| MONSTER_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | text |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMMER | - | - | string |
| ADVVRG_ID | - | - | string |
| ADVIESVRAAG_DATUM | - | - | string |
| MONSTER_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | text |
| DNA_NUMMER | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMMER | - | - | string |
| ADVVRG_ID | - | - | string |
| ADVIESVRAAG_DATUM | - | - | string |
| MONSTER_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | text |
| DNA_NUMMER | - | - | string |
| MATERIAAL | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMMER | - | - | string |
| ADVVRG_ID | - | - | string |
| ADVIESVRAAG_DATUM | - | - | string |
| MONSTER_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | text |
| DNA_NUMMER | - | - | string |
| MATERIAAL | - | - | string |
| EINDUITSLAGTEKST | - | - | text |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMMER | - | - | string |
| ADVVRG_ID | - | - | string |
| ADVIESVRAAG_DATUM | - | - | string |
| MONSTER_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | text |
| DNA_NUMMER | - | - | string |
| MATERIAAL | - | - | string |
| EINDUITSLAGTEKST | - | - | text |
| EINDUITSLAG_DATUM | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMMER | - | - | string |
| ADVVRG_ID | - | - | string |
| ADVIESVRAAG_DATUM | - | - | string |
| MONSTER_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | text |
| DNA_NUMMER | - | - | string |
| MATERIAAL | - | - | string |
| EINDUITSLAGTEKST | - | - | text |
| EINDUITSLAG_DATUM | - | - | string |
| ADVIESVRAAGUITSLAG_ID | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMMER | - | - | string |
| ADVVRG_ID | - | - | string |
| ADVIESVRAAG_DATUM | - | - | string |
| MONSTER_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | text |
| DNA_NUMMER | - | - | string |
| MATERIAAL | - | - | string |
| EINDUITSLAGTEKST | - | - | text |
| EINDUITSLAG_DATUM | - | - | string |
| ADVIESVRAAGUITSLAG_ID | - | - | string |
| ADVIESVRAAGUITSLAG_CODE | - | - | text |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMMER | - | - | string |
| ADVVRG_ID | - | - | string |
| ADVIESVRAAG_DATUM | - | - | string |
| MONSTER_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | text |
| DNA_NUMMER | - | - | string |
| MATERIAAL | - | - | string |
| EINDUITSLAGTEKST | - | - | text |
| EINDUITSLAG_DATUM | - | - | string |
| ADVIESVRAAGUITSLAG_ID | - | - | string |
| ADVIESVRAAGUITSLAG_CODE | - | - | text |
| AANDOENING_CODE | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMMER | - | - | string |
| ADVVRG_ID | - | - | string |
| ADVIESVRAAG_DATUM | - | - | string |
| MONSTER_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | text |
| DNA_NUMMER | - | - | string |
| MATERIAAL | - | - | string |
| EINDUITSLAGTEKST | - | - | text |
| EINDUITSLAG_DATUM | - | - | string |
| ADVIESVRAAGUITSLAG_ID | - | - | string |
| ADVIESVRAAGUITSLAG_CODE | - | - | text |
| AANDOENING_CODE | - | - | string |
| LABUITSLAGTEKST | - | - | text |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMMER | - | - | string |
| ADVVRG_ID | - | - | string |
| ADVIESVRAAG_DATUM | - | - | string |
| MONSTER_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | text |
| DNA_NUMMER | - | - | string |
| MATERIAAL | - | - | string |
| EINDUITSLAGTEKST | - | - | text |
| EINDUITSLAG_DATUM | - | - | string |
| ADVIESVRAAGUITSLAG_ID | - | - | string |
| ADVIESVRAAGUITSLAG_CODE | - | - | text |
| AANDOENING_CODE | - | - | string |
| LABUITSLAGTEKST | - | - | text |
| LABUITSLAG_COMMENTAAR | - | - | text |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMMER | - | - | string |
| ADVVRG_ID | - | - | string |
| ADVIESVRAAG_DATUM | - | - | string |
| MONSTER_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | text |
| DNA_NUMMER | - | - | string |
| MATERIAAL | - | - | string |
| EINDUITSLAGTEKST | - | - | text |
| EINDUITSLAG_DATUM | - | - | string |
| ADVIESVRAAGUITSLAG_ID | - | - | string |
| ADVIESVRAAGUITSLAG_CODE | - | - | text |
| AANDOENING_CODE | - | - | string |
| LABUITSLAGTEKST | - | - | text |
| LABUITSLAG_COMMENTAAR | - | - | text |
| LABUITSLAG_DATUM | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMMER | - | - | string |
| ADVVRG_ID | - | - | string |
| ADVIESVRAAG_DATUM | - | - | string |
| MONSTER_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | text |
| DNA_NUMMER | - | - | string |
| MATERIAAL | - | - | string |
| EINDUITSLAGTEKST | - | - | text |
| EINDUITSLAG_DATUM | - | - | string |
| ADVIESVRAAGUITSLAG_ID | - | - | string |
| ADVIESVRAAGUITSLAG_CODE | - | - | text |
| AANDOENING_CODE | - | - | string |
| LABUITSLAGTEKST | - | - | text |
| LABUITSLAG_COMMENTAAR | - | - | text |
| LABUITSLAG_DATUM | - | - | string |
| LABUITSLAG_ID | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMMER | - | - | string |
| ADVVRG_ID | - | - | string |
| ADVIESVRAAG_DATUM | - | - | string |
| MONSTER_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | text |
| DNA_NUMMER | - | - | string |
| MATERIAAL | - | - | string |
| EINDUITSLAGTEKST | - | - | text |
| EINDUITSLAG_DATUM | - | - | string |
| ADVIESVRAAGUITSLAG_ID | - | - | string |
| ADVIESVRAAGUITSLAG_CODE | - | - | text |
| AANDOENING_CODE | - | - | string |
| LABUITSLAGTEKST | - | - | text |
| LABUITSLAG_COMMENTAAR | - | - | text |
| LABUITSLAG_DATUM | - | - | string |
| LABUITSLAG_ID | - | - | string |
| LABUITSLAG_CODE | - | - | text |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMMER | - | - | string |
| ADVVRG_ID | - | - | string |
| ADVIESVRAAG_DATUM | - | - | string |
| MONSTER_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | text |
| DNA_NUMMER | - | - | string |
| MATERIAAL | - | - | string |
| EINDUITSLAGTEKST | - | - | text |
| EINDUITSLAG_DATUM | - | - | string |
| ADVIESVRAAGUITSLAG_ID | - | - | string |
| ADVIESVRAAGUITSLAG_CODE | - | - | text |
| AANDOENING_CODE | - | - | string |
| LABUITSLAGTEKST | - | - | text |
| LABUITSLAG_COMMENTAAR | - | - | text |
| LABUITSLAG_DATUM | - | - | string |
| LABUITSLAG_ID | - | - | string |
| LABUITSLAG_CODE | - | - | text |
| LABRESULTS | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMMER | - | - | string |
| ADVVRG_ID | - | - | string |
| ADVIESVRAAG_DATUM | - | - | string |
| MONSTER_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | text |
| DNA_NUMMER | - | - | string |
| MATERIAAL | - | - | string |
| EINDUITSLAGTEKST | - | - | text |
| EINDUITSLAG_DATUM | - | - | string |
| ADVIESVRAAGUITSLAG_ID | - | - | string |
| ADVIESVRAAGUITSLAG_CODE | - | - | text |
| AANDOENING_CODE | - | - | string |
| LABUITSLAGTEKST | - | - | text |
| LABUITSLAG_COMMENTAAR | - | - | text |
| LABUITSLAG_DATUM | - | - | string |
| LABUITSLAG_ID | - | - | string |
| LABUITSLAG_CODE | - | - | text |
| LABRESULTS | - | - | string |
| AUTHORISED | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMMER | - | - | string |
| ADVVRG_ID | - | - | string |
| ADVIESVRAAG_DATUM | - | - | string |
| MONSTER_ID | - | - | string |
| TEST_CODE | - | - | string |
| TEST_OMS | - | - | text |
| DNA_NUMMER | - | - | string |
| MATERIAAL | - | - | string |
| EINDUITSLAGTEKST | - | - | text |
| EINDUITSLAG_DATUM | - | - | string |
| ADVIESVRAAGUITSLAG_ID | - | - | string |
| ADVIESVRAAGUITSLAG_CODE | - | - | text |
| AANDOENING_CODE | - | - | string |
| LABUITSLAGTEKST | - | - | text |
| LABUITSLAG_COMMENTAAR | - | - | text |
| LABUITSLAG_DATUM | - | - | string |
| LABUITSLAG_ID | - | - | string |
| LABUITSLAG_CODE | - | - | text |
| LABRESULTS | - | - | string |
| AUTHORISED | - | - | string |
| FOETUS_ID | - | - | string |

Note: The symbol &#8251; denotes attributes that are primary keys

