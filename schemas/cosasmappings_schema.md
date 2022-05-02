# Model Schema

## Packages

| Name | Description | Parent |
|:---- |:-----------|:------|
| cosasmappings | Mapping tables for processing raw data into unified model terminology (v2.0.0, 2022-05-02) | - |

## Entities

| Name | Description | Package |
|:---- |:-----------|:-------|
| template | attribute template for mapping tables | cosasmappings |
| genderidentity | mappings for 'Gender identity' | cosasmappings |
| genderatbirth | mappings for 'Gender at birth' | cosasmappings |
| biospecimentype | mappings for 'Biospecimen type' | cosasmappings |
| samplereason | mappings for 'Reason for sampling' | cosasmappings |
| sequencerinfo | mappings for 'Sequencer information' | cosasmappings |
| genomebuild | mappings for 'Genome build' | cosasmappings |
| cineasmappings | Cineas to HPO mappings | cosasmappings |

## Attributes

### Entity: cosasmappings_template

attribute template for mapping tables

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| from&#8251; | - | Used to indicate a specified place or time as a starting point; used to indicate a source, cause, agent, or instrument. | string |
| to | - | Used as a function word to indicate direction, purpose, or movement. | string |
| toAlternate | - | Available in place of something else. | string |

### Entity: cosasmappings_cineasmappings

Cineas to HPO mappings

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| value&#8251; | - | - | string |
| description | - | - | string |
| codesystem | - | - | string |
| code | - | - | string |
| hpo | - | - | string |

Note: The symbol &#8251; denotes attributes that are primary keys

