# Model Schema

## Packages

| Name | Description | Parent |
|:---- |:-----------|:------|
| cosasreports | Reports on COSAS jobs, imports, and processing (v1.0.0, 2022-02-11) | - |

## Entities

| Name | Description | Package |
|:---- |:-----------|:-------|
| imports | Historical records of all new data imported into COSAS | cosasreports |
| logs | Historical records of all COSAS data processing jobs | cosasreports |
| template | - | cosasreports |
| datahandling | Basic (non-analytical) operations of some data, either a file or equivalent entity in memory, such that the same basic type of data is consumed as input and generated as output. | cosasreports |
| status | A condition or state at a particular time. | cosasreports |

## Attributes

### Entity: cosasreports_imports

Historical records of all new data imported into COSAS

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| name | - | The words or language units by which a thing is known. | string |
| databaseName | - | The name of a biological or bioinformatics database. | string |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| startTime | - | The time at which something is to start or did start. | datetime |
| endTime | - | The time when an event has ceased. | datetime |
| elapsedTime | - | The interval between two reference points in time. (in milliseconds) | string |
| numberOfRowsAdded | - | Number of rows added to a database table | compound |
| subjects | - | Number of rows added to umdm_subjects | int |
| clinical | - | Number of rows added to umdm_clinical | int |
| samples | - | Number of rows added to umdm_samples | int |
| samplePreparation | - | Number of rows added to umdm_samplePreparation | int |
| sequencing | - | Number of rows added to umdm_sequencing | int |
| files | - | Number of rows added to umdm_files | int |
| steps | - | A specific stage of progression through a sequential process. | mref |
| comment | - | A written explanation, observation or criticism added to textual material. | text |

### Entity: cosasreports_logs

Historical records of all COSAS data processing jobs

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| name | - | The words or language units by which a thing is known. | string |
| step | - | A specific stage of progression through a sequential process. | categorical |
| databaseTable | - | A database table is a set of named columns with zero or more rows composed of cells that contain column values and is part of a database. | string |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| startTime | - | The time at which something is to start or did start. | datetime |
| endTime | - | The time when an event has ceased. | datetime |
| elapsedTime | - | The interval between two reference points in time. (in milliseconds) | string |
| status | - | A condition or state at a particular time. | string |
| comment | - | A written explanation, observation or criticism added to textual material. | text |

### Entity: cosasreports_template

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| value&#8251; | - | The information contained in a data field. It may represent a numeric quantity, a textual characterization, a date or time measurement, or some other state, depending on the nature of the attribute. | string |
| description | - | A written or verbal account, representation, statement, or explanation of something | text |
| codesystem | - | A systematized collection of concepts that define corresponding codes. | string |
| code | - | A symbol or combination of symbols which is assigned to the members of a collection. | string |
| iri | - | A unique symbol that establishes identity of the resource. | hyperlink |

Note: The symbol &#8251; denotes attributes that are primary keys

