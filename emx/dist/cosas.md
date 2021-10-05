# Model Schema

## Packages

| Name | Description |
|:---- |:-----------|
| cosasrefs | Reference tables for COSAS (v0.9022, 2021-09-01) |
| cosas | The Catalogue of Sequence Array and Samples (v0.91, 2021-10-05) |

## Entities

| Name | Description | Package |
|:---- |:-----------|:-------|
| availabilityStatus | Categories that indicate if data is available for use | cosasrefs |
| biologicalSex | Categories for biological sex | cosasrefs |
| diagnoses | Diagnostic codes and descriptions | cosasrefs |
| inclusionStatus | Patient inclusion status categories | cosasrefs |
| labIndications | Categories for purpose of the labs | cosasrefs |
| materialTypes | Categories for material type | cosasrefs |
| phenotype | Fair Genomes Phenotype (v0.3) | cosasrefs |
| testCodes | Test codes and descriptions (e.g., NX, NG) | cosasrefs |
| patients | Patient characteristics including family members | cosas |
| clinical | Findings and circumstances relating to the examination and treatment of a patient | cosas |
| samples | Sample metadata including tests performed and results | cosas |
| labs_array | Lab information for Array | cosas |
| labs_ngs | Lab information for NGS | cosas |
| files | Metadata on files | cosas |

## Attributes

### Entity: cosasrefs_availabilityStatus

Categories that indicate if data is available for use

| Name | Label | Description | Data Type | ID Attribute |
|:---- |:-----|:-----------|:---------|:------------|
| id | ID | - | string | True |
| value | value | - | string | False |
| description | Description | - | string | False |
| codesystem | Code system | - | string | False |
| code | Code | - | string | False |
| iri | iri | - | hyperlink | False |

### Entity: cosasrefs_biologicalSex

Categories for biological sex

| Name | Label | Description | Data Type | ID Attribute |
|:---- |:-----|:-----------|:---------|:------------|
| id | ID | - | string | True |
| value | Value | - | string | False |
| description | Description | - | string | False |
| codesystem | Code system | - | string | False |
| code | Code | - | string | False |
| iri | iri | - | hyperlink | False |

### Entity: cosasrefs_diagnoses

Diagnostic codes and descriptions

| Name | Label | Description | Data Type | ID Attribute |
|:---- |:-----|:-----------|:---------|:------------|
| id | - | - | string | True |
| code | - | Cineas code | string | False |
| codesystem | - | - | string | False |
| description | - | Cineas description | string | False |
| hpo | - | - | mref | False |

### Entity: cosasrefs_inclusionStatus

Patient inclusion status categories

| Name | Label | Description | Data Type | ID Attribute |
|:---- |:-----|:-----------|:---------|:------------|
| id | ID | - | string | True |
| value | Value | FairGenomes value | string | False |
| description | Description | FairGenomes description | string | False |
| codesystem | Codesystem | FairGenomes codesystem | string | False |
| code | Code | FairGenomes code | string | False |
| iri | IRI | FairGenomes IRI | hyperlink | False |

### Entity: cosasrefs_labIndications

Categories for purpose of the labs

| Name | Label | Description | Data Type | ID Attribute |
|:---- |:-----|:-----------|:---------|:------------|
| id | ID | - | string | True |
| value | Value | - | string | False |
| description | Description | FairGenomes description | string | False |
| codesystem | Codesystem | FairGenomes codesystem | string | False |
| code | Code | FairGenomes code | string | False |
| iri | IRI | FairGenomes IRI | hyperlink | False |

### Entity: cosasrefs_materialTypes

Categories for material type

| Name | Label | Description | Data Type | ID Attribute |
|:---- |:-----|:-----------|:---------|:------------|
| id | ID | - | string | True |
| material | Material | - | string | False |
| value | Value | FairGenomes material type | string | False |
| description | Description | FairGenomes description | string | False |
| codesystem | Codesystem | FairGenomes codesystem | string | False |
| code | Code | FairGenomes code | string | False |
| iri | IRI | FairGenomes iri | hyperlink | False |

### Entity: cosasrefs_phenotype

Fair Genomes Phenotype (v0.3)

| Name | Label | Description | Data Type | ID Attribute |
|:---- |:-----|:-----------|:---------|:------------|
| value | - | - | string | False |
| description | - | - | text | False |
| codesystem | - | - | string | False |
| code | - | - | string | True |
| iri | - | - | string | False |

### Entity: cosasrefs_testCodes

Test codes and descriptions (e.g., NX, NG)

| Name | Label | Description | Data Type | ID Attribute |
|:---- |:-----|:-----------|:---------|:------------|
| id | ID | - | string | True |
| code | Code | - | string | False |
| description | Description | - | string | False |
| label | Label | - | text | False |
| panel | Panel | - | text | False |
| genes | Genes | - | text | False |

### Entity: cosas_patients

Patient characteristics including family members

| Name | Label | Description | Data Type | ID Attribute |
|:---- |:-----|:-----------|:---------|:------------|
| umcgID | UMCG Number | MDN id in EPIC | string | True |
| familyID | Family Number | - | string | False |
| dateOfBirth | Date of Birth | - | date | False |
| biologicalSex | Biological Sex | - | categorical | False |
| maternalID | Maternal ID | - | string | False |
| paternalID | Paternal ID | - | string | False |
| linkedFamilyIDs | Linked Family IDs | - | text | False |
| inclusionStatus | Status | - | categorical | False |
| dateOfDeath | Date of Death | - | date | False |
| ageAtDeath | Age at death | The age at which death occurred (in years) | decimal | False |
| consanguinity | Consanguinity | - | bool | False |
| fetusStatus | Fetus Status | - | bool | False |
| twinStatus | Twin Status | Has twin or is suspected of having a twin | bool | False |
| altPatientID | Linked UMCG number | - | string | False |
| dateLastUpdated | Date last updated | Date lasted updated in COSAS | datetime | False |

### Entity: cosas_clinical

Findings and circumstances relating to the examination and treatment of a patient

| Name | Label | Description | Data Type | ID Attribute |
|:---- |:-----|:-----------|:---------|:------------|
| umcgID | UMCG Number | MDN id in EPIC | string | True |
| provisionalPhenotype | Provisional Phenotype | This is a tentative diagnosis - still a candidate that is under consideration | mref | False |
| provisionalPhenotypeHpo | Provisional HPO | - | mref | False |
| excludedPhenotype | Excluded Phenotype | This condition has been ruled out by subsequent diagnostic and clinical evidence. | mref | False |
| excludedPhenotypeHpo | Excluded HPO | - | mref | False |
| confirmedPhenotype | Confirmed Phenotype | - | mref | False |
| dateLastUpdated | Date last updated | Date lasted updated in COSAS | datetime | False |

### Entity: cosas_samples

Sample metadata including tests performed and results

| Name | Label | Description | Data Type | ID Attribute |
|:---- |:-----|:-----------|:---------|:------------|
| umcgID | UMCG Number | MDN id in EPIC | xref | False |
| familyID | Family Number | - | string | False |
| requestID | Request ID | - | string | False |
| requestDate | Request Date | - | date | False |
| sampleID | Sample ID | - | string | False |
| dnaID | DNA number | - | string | False |
| materialType | Material type | - | string | False |
| labIndication | Lab Indication | - | xref | False |
| testCode | Test code | - | xref | False |
| testDate | Test date | - | date | False |
| result | Final results | - | text | False |
| resultDate | Final result date | - | date | False |
| requestResultID | Final result request ID | - | string | False |
| labResult | Lab Result | - | text | False |
| labResultDate | Lab result date | - | date | False |
| labResultID | Lab result ID | - | string | False |
| labResultComment | Lab result comment | - | text | False |
| labResultAvailability | Lab result availability | - | string | False |
| authorizationStatus | Authorization status | - | bool | False |
| disorderCode | Disorder code | - | string | False |
| dateLastUpdated | Date last updated | Date lasted updated in COSAS | datetime | False |
| id | id | auto generated ID | string | True |

### Entity: cosas_labs_array

Lab information for Array

| Name | Label | Description | Data Type | ID Attribute |
|:---- |:-----|:-----------|:---------|:------------|
| umcgID | UMCG Number | MDN id in EPIC | xref | False |
| familyID | Family Number | - | string | False |
| requestID | Request ID | - | string | False |
| dnaID | DNA number | - | string | False |
| labIndication | Lab Indication | - | xref | False |
| testID | Test ID | - | string | False |
| testCode | Test Code | - | xref | False |
| testDate | Test date | - | date | False |
| dateLastUpdated | Date last updated | Date lasted updated in COSAS | datetime | False |
| id | id | auto generated ID | string | True |

### Entity: cosas_labs_ngs

Lab information for NGS

| Name | Label | Description | Data Type | ID Attribute |
|:---- |:-----|:-----------|:---------|:------------|
| umcgID | UMCG Number | MDN id in EPIC | xref | False |
| familyID | Family Number | - | string | False |
| requestID | Request ID | - | string | False |
| dnaID | DNA number | - | string | False |
| labIndication | Lab Indication | - | xref | False |
| testID | Test ID | - | string | False |
| testCode | Test Code | - | xref | False |
| testDate | Test date | - | date | False |
| sequencer | Sequencer | - | string | False |
| prepKit | Prep Kit | - | string | False |
| sequencingType | Sequencing type | - | string | False |
| seqType | Seq Type | - | string | False |
| capturingKit | Capturing Kit | - | string | False |
| batchName | Batch Name | - | string | False |
| genomeBuild | Genome Build | - | string | False |
| dateLastUpdated | Date last updated | Date lasted updated in COSAS | datetime | False |
| id | id | auto generated ID | string | True |

### Entity: cosas_files

Metadata on files

| Name | Label | Description | Data Type | ID Attribute |
|:---- |:-----|:-----------|:---------|:------------|
| umcgID | UMCG Number | MDN id in EPIC | xref | False |
| familyID | Family Number | - | string | False |
| dnaID | DNA number | - | string | False |
| testID | Test ID | - | xref | False |
| filename | Filename | - | string | False |
| filepath | filepath | - | string | False |
| filetype | File type | - | string | False |
| md5 | Checksum | - | string | False |
| dateCreated | Date created | - | date | False |
| dateLastUpdated | Date last updated | Date lasted updated in COSAS | datetime | False |
| id | id | auto generated ID | string | True |
