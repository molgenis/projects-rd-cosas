# Model Schema

## Packages

| Name | Description | Parent |
|:---- |:-----------|:------|
| ucu | v1.0.0; 2022-05-11 | - |

## Entities

| Name | Description | Package |
|:---- |:-----------|:-------|
| patient | - | ucu |
| technique | - | ucu |
| ref | - | ucu |
| consent | - | ucu |
| file | - | ucu |
| sample_types | - | ucu |
| stage | - | ucu |
| status | - | ucu |
| type | - | ucu |
| yesno | - | ucu |

## Attributes

### Entity: ucu_patient

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | - | string |
| submitter | Submitter (KG) | - | string |
| date | Date submission | - | date |
| reason_submission | Reason for submission | - | text |
| consent | Consent given by patient: | - | categorical |
| case | Patient description | - | compound |
| umcgidentifier | UMCG ID | UMCG nr | xref |
| dnanr | DNA number | - | xref |
| sex1 | Sex | Sex at birth | string |
| dateofBirth | Date of birth | Date of birth | string |
| phenotype | Phenotype | Phenotype (i.e., HPO term or HPO ID; multiple HPO entries possible) | mref |
| addPhenotype | Additional phenotypic information | - | text |
| physical | Physical examination | - | text |
| photos | Photos (if available) | - | file |
| EPICphoto | Photos available in EPIC | - | bool |
| submitterPhoto | Photos available from submitter | - | bool |
| addinfo | Additional patient information | - | text |
| genetic_test | Genetic tests UMCG | (include test type, date of test) | text |
| genetic_testOther | Genetics Tests elsewhere | (include test type, date of test, where testing was done) | text |
| diagnosticsOther | Other diagnostics of clinical importance | - | text |
| suspect | Suspected variant/cause | - | text |
| sample_type | Sample type(s) | Which sample type(s) are available? | categorical |
| sample_type_other | If other, please specify | - | text |
| addinfo_sample | Additional sample/test Information | - | text |
| family | Family information | - | compound |
| fid | FamilyID | Family ID (FID) | string |
| mid | MaternalID | Maternal ID (MID), (when deceased, please fill: N/A) | string |
| pid | PaternalID | Paternal ID (PID), (when deceased, please fill: N/A) | string |
| addinfo_family | Additional family information | - | text |
| status | Status of the request | Will be completed by the UCU team | compound |
| status_info | Status | - | categorical |
| datestatus | Date changed status | - | date |
| reason | reason status | - | text |

### Entity: ucu_technique

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | - | string |
| submitter | Submitter (UMCG) | - | string |
| email_address | Email address (UMCG) | - | email |
| date | Date submission | - | string |
| tech | Technique description | - | compound |
| summary | Summary | Brief description including preferred phenotype (use HPO terms), variant type (i.e., splicing, nonsense, mosaicism, etc.), newly published gene/phenotype association, UniParental Disomy (UPD), etc. | text |
| suitable | Suitable for specific patients | - | categorical |
| suitableYes | If yes, please specify | - | text |
| type | Type technique | - | categorical |
| sample_tech_other | If other, please specify | - | text |
| sample_type | Which sample/data type(s) is required? | - | categorical |
| sample_type_other | If other, please specify | - | text |
| data_file | If a data file is required, what type of file is necessary? | - | categorical |
| data_file_other | If other, please specify | - | text |
| stage | Stage of development | - | categorical |
| addinfo | Additional information over stage of development | - | text |
| status | Status of the request | Will be completed by the UCU team | compound |
| status_info | Status | - | categorical |
| datestatus | Date changed status | - | date |
| reason | Reason status | - | text |

### Entity: ucu_ref

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| id&#8251; | - | - | string |
| label | - | - | string |

Note: The symbol &#8251; denotes attributes that are primary keys

