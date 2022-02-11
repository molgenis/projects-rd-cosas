# Model Schema

## Packages

| Name | Description | Parent |
|:---- |:-----------|:------|
| cosasportal | Staging tables for raw data exports (v1.1.0, 2022-02-10) | - |

## Entities

| Name | Description | Package |
|:---- |:-----------|:-------|
| patients | Raw metadata for patients and families | cosasportal |
| diagnoses | Raw diagnostic metadata | cosasportal |
| samples | Raw data table for samples | cosasportal |
| labs_array_adlas | Raw array metadata from ADLAS | cosasportal |
| labs_array_darwin | Raw array metadata from Darwin | cosasportal |
| labs_ngs_adlas | Raw NGS data from ADLAS | cosasportal |
| labs_ngs_darwin | Raw NSG metadata from Darwin | cosasportal |
| bench_cnv | Staging table for CNV exports | cosasportal |

## Attributes

### Entity: cosasportal_patients

Raw metadata for patients and families

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
| processed | - | - | bool |
| dataProcessed | - | - | datetime |
| id&#8251; | - | auto generated Molgenis ID | string |

### Entity: cosasportal_diagnoses

Raw diagnostic metadata

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UMCG_NUMBER | - | - | string |
| HOOFDDIAGNOSE | - | - | string |
| HOOFDDIAGNOSE_ZEKERHEID | - | - | string |
| EXTRA_DIAGNOSE | - | - | string |
| EXTRA_DIAGNOSE_ZEKERHEID | - | - | string |
| DATUM_EERSTE_CONSULT | - | - | string |
| OND_ID | - | - | string |
| processed | - | - | bool |
| dataProcessed | - | - | datetime |
| id&#8251; | - | auto generated Molgenis ID | string |

### Entity: cosasportal_samples

Raw data table for samples

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
| processed | - | - | bool |
| dataProcessed | - | - | datetime |
| id&#8251; | - | auto generated Molgenis ID | string |

### Entity: cosasportal_labs_array_adlas

Raw array metadata from ADLAS

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
| processed | - | - | bool |
| dataProcessed | - | - | datetime |
| id&#8251; | - | auto generated Molgenis ID | string |

### Entity: cosasportal_labs_array_darwin

Raw array metadata from Darwin

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| UmcgNr | - | - | string |
| TestId | - | - | string |
| TestDatum | - | - | string |
| Indicatie | - | - | string |
| BatchNaam | - | - | string |
| CallRate | - | - | string |
| StandaardDeviatie | - | - | string |
| processed | - | - | bool |
| dataProcessed | - | - | datetime |
| id&#8251; | - | auto generated Molgenis ID | string |

### Entity: cosasportal_labs_ngs_adlas

Raw NGS data from ADLAS

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
| processed | - | - | bool |
| dataProcessed | - | - | datetime |
| id&#8251; | - | auto generated Molgenis ID | string |

### Entity: cosasportal_labs_ngs_darwin

Raw NSG metadata from Darwin

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
| GenomeBuild | - | - | string |
| CallRate | - | - | string |
| StandaardDeviatie | - | - | string |
| processed | - | - | bool |
| dataProcessed | - | - | datetime |
| id&#8251; | - | auto generated Molgenis ID | string |

### Entity: cosasportal_bench_cnv

Staging table for CNV exports

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| primid | - | UMCG Number | string |
| secid | - | Family Number | string |
| externalid | - | - | string |
| gender | - | - | string |
| comment | - | - | text |
| phenotype | - | HPO code (HPO:1234567) | text |
| created | - | - | string |
| processed | - | - | bool |
| Phenotype | - | - | string |
| dataProcessed | - | - | datetime |
| id&#8251; | - | auto generated Molgenis ID | string |

Note: The symbol &#8251; denotes attributes that are primary keys

