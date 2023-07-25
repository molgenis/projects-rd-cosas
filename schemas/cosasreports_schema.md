# Model Schema

## Packages

| Name | Description | Parent |
|:---- |:-----------|:------|
| cosasreports | Reports on COSAS jobs, imports, and processing (v1.8.1, 2023-07-25) | - |
| cosasreports_refs | Reference tables for COSAS Reports | cosasreports |

## Entities

| Name | Description | Package |
|:---- |:-----------|:-------|
| imports | Historical records of daily COSAS imports | cosasreports |
| processingsteps | Historical records of steps involved in the processing of daily cosas jobs | cosasreports |
| attributesummary | Summary of attributes used by COSAS table and the percentage of available data | cosasreports |
| datasources | Overview on the data sources connected to COSAS | cosasreports |
| jobs | Overview on scheduled jobs | cosasreports |
| template | - | cosasreports_refs |
| datahandling | Basic (non-analytical) operations of some data, either a file or equivalent entity in memory, such that the same basic type of data is consumed as input and generated as output. | cosasreports_refs |
| status | A condition or state at a particular time. | cosasreports_refs |
| keytypes | A database key is an informational entity whose value is constructed from one or more database columns. | cosasreports_refs |

## Attributes

### Entity: cosasreports_imports

Historical records of daily COSAS imports

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| name | - | The words or language units by which a thing is known. | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| name | - | The words or language units by which a thing is known. | string |
| databaseName | - | The name of a biological or bioinformatics database. | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| name | - | The words or language units by which a thing is known. | string |
| databaseName | - | The name of a biological or bioinformatics database. | string |
| hasCompleted | - | completed is that status of a process that successfully unfolds. | bool |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| name | - | The words or language units by which a thing is known. | string |
| databaseName | - | The name of a biological or bioinformatics database. | string |
| hasCompleted | - | completed is that status of a process that successfully unfolds. | bool |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| name | - | The words or language units by which a thing is known. | string |
| databaseName | - | The name of a biological or bioinformatics database. | string |
| hasCompleted | - | completed is that status of a process that successfully unfolds. | bool |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| startTime | - | The time at which something is to start or did start. | datetime |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| name | - | The words or language units by which a thing is known. | string |
| databaseName | - | The name of a biological or bioinformatics database. | string |
| hasCompleted | - | completed is that status of a process that successfully unfolds. | bool |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| startTime | - | The time at which something is to start or did start. | datetime |
| endTime | - | The time when an event has ceased. | datetime |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| name | - | The words or language units by which a thing is known. | string |
| databaseName | - | The name of a biological or bioinformatics database. | string |
| hasCompleted | - | completed is that status of a process that successfully unfolds. | bool |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| startTime | - | The time at which something is to start or did start. | datetime |
| endTime | - | The time when an event has ceased. | datetime |
| elapsedTime | - | The interval between two reference points in time. (in seconds) | decimal |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| name | - | The words or language units by which a thing is known. | string |
| databaseName | - | The name of a biological or bioinformatics database. | string |
| hasCompleted | - | completed is that status of a process that successfully unfolds. | bool |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| startTime | - | The time at which something is to start or did start. | datetime |
| endTime | - | The time when an event has ceased. | datetime |
| elapsedTime | - | The interval between two reference points in time. (in seconds) | decimal |
| numberOfRowsAdded | - | Number of rows added to a database table | compound |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| name | - | The words or language units by which a thing is known. | string |
| databaseName | - | The name of a biological or bioinformatics database. | string |
| hasCompleted | - | completed is that status of a process that successfully unfolds. | bool |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| startTime | - | The time at which something is to start or did start. | datetime |
| endTime | - | The time when an event has ceased. | datetime |
| elapsedTime | - | The interval between two reference points in time. (in seconds) | decimal |
| numberOfRowsAdded | - | Number of rows added to a database table | compound |
| subjects | - | Number of rows added to umdm_subjects | int |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| name | - | The words or language units by which a thing is known. | string |
| databaseName | - | The name of a biological or bioinformatics database. | string |
| hasCompleted | - | completed is that status of a process that successfully unfolds. | bool |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| startTime | - | The time at which something is to start or did start. | datetime |
| endTime | - | The time when an event has ceased. | datetime |
| elapsedTime | - | The interval between two reference points in time. (in seconds) | decimal |
| numberOfRowsAdded | - | Number of rows added to a database table | compound |
| subjects | - | Number of rows added to umdm_subjects | int |
| clinical | - | Number of rows added to umdm_clinical | int |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| name | - | The words or language units by which a thing is known. | string |
| databaseName | - | The name of a biological or bioinformatics database. | string |
| hasCompleted | - | completed is that status of a process that successfully unfolds. | bool |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| startTime | - | The time at which something is to start or did start. | datetime |
| endTime | - | The time when an event has ceased. | datetime |
| elapsedTime | - | The interval between two reference points in time. (in seconds) | decimal |
| numberOfRowsAdded | - | Number of rows added to a database table | compound |
| subjects | - | Number of rows added to umdm_subjects | int |
| clinical | - | Number of rows added to umdm_clinical | int |
| samples | - | Number of rows added to umdm_samples | int |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| name | - | The words or language units by which a thing is known. | string |
| databaseName | - | The name of a biological or bioinformatics database. | string |
| hasCompleted | - | completed is that status of a process that successfully unfolds. | bool |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| startTime | - | The time at which something is to start or did start. | datetime |
| endTime | - | The time when an event has ceased. | datetime |
| elapsedTime | - | The interval between two reference points in time. (in seconds) | decimal |
| numberOfRowsAdded | - | Number of rows added to a database table | compound |
| subjects | - | Number of rows added to umdm_subjects | int |
| clinical | - | Number of rows added to umdm_clinical | int |
| samples | - | Number of rows added to umdm_samples | int |
| samplePreparation | - | Number of rows added to umdm_samplePreparation | int |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| name | - | The words or language units by which a thing is known. | string |
| databaseName | - | The name of a biological or bioinformatics database. | string |
| hasCompleted | - | completed is that status of a process that successfully unfolds. | bool |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| startTime | - | The time at which something is to start or did start. | datetime |
| endTime | - | The time when an event has ceased. | datetime |
| elapsedTime | - | The interval between two reference points in time. (in seconds) | decimal |
| numberOfRowsAdded | - | Number of rows added to a database table | compound |
| subjects | - | Number of rows added to umdm_subjects | int |
| clinical | - | Number of rows added to umdm_clinical | int |
| samples | - | Number of rows added to umdm_samples | int |
| samplePreparation | - | Number of rows added to umdm_samplePreparation | int |
| sequencing | - | Number of rows added to umdm_sequencing | int |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| name | - | The words or language units by which a thing is known. | string |
| databaseName | - | The name of a biological or bioinformatics database. | string |
| hasCompleted | - | completed is that status of a process that successfully unfolds. | bool |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| startTime | - | The time at which something is to start or did start. | datetime |
| endTime | - | The time when an event has ceased. | datetime |
| elapsedTime | - | The interval between two reference points in time. (in seconds) | decimal |
| numberOfRowsAdded | - | Number of rows added to a database table | compound |
| subjects | - | Number of rows added to umdm_subjects | int |
| clinical | - | Number of rows added to umdm_clinical | int |
| samples | - | Number of rows added to umdm_samples | int |
| samplePreparation | - | Number of rows added to umdm_samplePreparation | int |
| sequencing | - | Number of rows added to umdm_sequencing | int |
| files | - | Number of rows added to umdm_files | int |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| name | - | The words or language units by which a thing is known. | string |
| databaseName | - | The name of a biological or bioinformatics database. | string |
| hasCompleted | - | completed is that status of a process that successfully unfolds. | bool |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| startTime | - | The time at which something is to start or did start. | datetime |
| endTime | - | The time when an event has ceased. | datetime |
| elapsedTime | - | The interval between two reference points in time. (in seconds) | decimal |
| numberOfRowsAdded | - | Number of rows added to a database table | compound |
| subjects | - | Number of rows added to umdm_subjects | int |
| clinical | - | Number of rows added to umdm_clinical | int |
| samples | - | Number of rows added to umdm_samples | int |
| samplePreparation | - | Number of rows added to umdm_samplePreparation | int |
| sequencing | - | Number of rows added to umdm_sequencing | int |
| files | - | Number of rows added to umdm_files | int |
| steps | - | A specific stage of progression through a sequential process. | mref |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| name | - | The words or language units by which a thing is known. | string |
| databaseName | - | The name of a biological or bioinformatics database. | string |
| hasCompleted | - | completed is that status of a process that successfully unfolds. | bool |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| startTime | - | The time at which something is to start or did start. | datetime |
| endTime | - | The time when an event has ceased. | datetime |
| elapsedTime | - | The interval between two reference points in time. (in seconds) | decimal |
| numberOfRowsAdded | - | Number of rows added to a database table | compound |
| subjects | - | Number of rows added to umdm_subjects | int |
| clinical | - | Number of rows added to umdm_clinical | int |
| samples | - | Number of rows added to umdm_samples | int |
| samplePreparation | - | Number of rows added to umdm_samplePreparation | int |
| sequencing | - | Number of rows added to umdm_sequencing | int |
| files | - | Number of rows added to umdm_files | int |
| steps | - | A specific stage of progression through a sequential process. | mref |
| comment | - | A written explanation, observation or criticism added to textual material. | text |

### Entity: cosasreports_processingsteps

Historical records of steps involved in the processing of daily cosas jobs

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | int |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | int |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | int |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| name | - | The words or language units by which a thing is known. | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | int |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| name | - | The words or language units by which a thing is known. | string |
| step | - | A specific stage of progression through a sequential process. | categorical |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | int |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| name | - | The words or language units by which a thing is known. | string |
| step | - | A specific stage of progression through a sequential process. | categorical |
| databaseTable | - | A database table is a set of named columns with zero or more rows composed of cells that contain column values and is part of a database. | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | int |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| name | - | The words or language units by which a thing is known. | string |
| step | - | A specific stage of progression through a sequential process. | categorical |
| databaseTable | - | A database table is a set of named columns with zero or more rows composed of cells that contain column values and is part of a database. | string |
| startTime | - | The time at which something is to start or did start. | datetime |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | int |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| name | - | The words or language units by which a thing is known. | string |
| step | - | A specific stage of progression through a sequential process. | categorical |
| databaseTable | - | A database table is a set of named columns with zero or more rows composed of cells that contain column values and is part of a database. | string |
| startTime | - | The time at which something is to start or did start. | datetime |
| endTime | - | The time when an event has ceased. | datetime |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | int |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| name | - | The words or language units by which a thing is known. | string |
| step | - | A specific stage of progression through a sequential process. | categorical |
| databaseTable | - | A database table is a set of named columns with zero or more rows composed of cells that contain column values and is part of a database. | string |
| startTime | - | The time at which something is to start or did start. | datetime |
| endTime | - | The time when an event has ceased. | datetime |
| elapsedTime | - | The interval between two reference points in time. (in milliseconds) | decimal |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | int |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| name | - | The words or language units by which a thing is known. | string |
| step | - | A specific stage of progression through a sequential process. | categorical |
| databaseTable | - | A database table is a set of named columns with zero or more rows composed of cells that contain column values and is part of a database. | string |
| startTime | - | The time at which something is to start or did start. | datetime |
| endTime | - | The time when an event has ceased. | datetime |
| elapsedTime | - | The interval between two reference points in time. (in milliseconds) | decimal |
| status | - | A condition or state at a particular time. | xref |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | int |
| date | - | The particular day, month and year an event has happened or will happen. | date |
| name | - | The words or language units by which a thing is known. | string |
| step | - | A specific stage of progression through a sequential process. | categorical |
| databaseTable | - | A database table is a set of named columns with zero or more rows composed of cells that contain column values and is part of a database. | string |
| startTime | - | The time at which something is to start or did start. | datetime |
| endTime | - | The time when an event has ceased. | datetime |
| elapsedTime | - | The interval between two reference points in time. (in milliseconds) | decimal |
| status | - | A condition or state at a particular time. | xref |
| comment | - | A written explanation, observation or criticism added to textual material. | text |

### Entity: cosasreports_attributesummary

Summary of attributes used by COSAS table and the percentage of available data

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| dateLastUpdated | - | A data item that indicates the time when data about the sample collection was last updated in a database. | date |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| dateLastUpdated | - | A data item that indicates the time when data about the sample collection was last updated in a database. | date |
| databaseTable | - | A database table is a set of named columns with zero or more rows composed of cells that contain column values and is part of a database. | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| dateLastUpdated | - | A data item that indicates the time when data about the sample collection was last updated in a database. | date |
| databaseTable | - | A database table is a set of named columns with zero or more rows composed of cells that contain column values and is part of a database. | string |
| databaseColumn | - | A database collumn is a column in a database table. | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| dateLastUpdated | - | A data item that indicates the time when data about the sample collection was last updated in a database. | date |
| databaseTable | - | A database table is a set of named columns with zero or more rows composed of cells that contain column values and is part of a database. | string |
| databaseColumn | - | A database collumn is a column in a database table. | string |
| displayName | - | The standardized text associated with a code in a particular code system. | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| dateLastUpdated | - | A data item that indicates the time when data about the sample collection was last updated in a database. | date |
| databaseTable | - | A database table is a set of named columns with zero or more rows composed of cells that contain column values and is part of a database. | string |
| databaseColumn | - | A database collumn is a column in a database table. | string |
| displayName | - | The standardized text associated with a code in a particular code system. | string |
| databaseKey | - | A database key is an informational entity whose value is constructed from one or more database columns. | xref |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| dateLastUpdated | - | A data item that indicates the time when data about the sample collection was last updated in a database. | date |
| databaseTable | - | A database table is a set of named columns with zero or more rows composed of cells that contain column values and is part of a database. | string |
| databaseColumn | - | A database collumn is a column in a database table. | string |
| displayName | - | The standardized text associated with a code in a particular code system. | string |
| databaseKey | - | A database key is an informational entity whose value is constructed from one or more database columns. | xref |
| countOfValues | - | Determining the number or amount of something. | int |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| dateLastUpdated | - | A data item that indicates the time when data about the sample collection was last updated in a database. | date |
| databaseTable | - | A database table is a set of named columns with zero or more rows composed of cells that contain column values and is part of a database. | string |
| databaseColumn | - | A database collumn is a column in a database table. | string |
| displayName | - | The standardized text associated with a code in a particular code system. | string |
| databaseKey | - | A database key is an informational entity whose value is constructed from one or more database columns. | xref |
| countOfValues | - | Determining the number or amount of something. | int |
| totalValues | - | Pertaining to an entirety or whole, also constituting the full quantity or extent; complete; derived by addition. | int |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| dateLastUpdated | - | A data item that indicates the time when data about the sample collection was last updated in a database. | date |
| databaseTable | - | A database table is a set of named columns with zero or more rows composed of cells that contain column values and is part of a database. | string |
| databaseColumn | - | A database collumn is a column in a database table. | string |
| displayName | - | The standardized text associated with a code in a particular code system. | string |
| databaseKey | - | A database key is an informational entity whose value is constructed from one or more database columns. | xref |
| countOfValues | - | Determining the number or amount of something. | int |
| totalValues | - | Pertaining to an entirety or whole, also constituting the full quantity or extent; complete; derived by addition. | int |
| differenceInValues | - | The quality of being unlike or dissimilar. | int |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| identifier&#8251; | - | One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing. | string |
| dateLastUpdated | - | A data item that indicates the time when data about the sample collection was last updated in a database. | date |
| databaseTable | - | A database table is a set of named columns with zero or more rows composed of cells that contain column values and is part of a database. | string |
| databaseColumn | - | A database collumn is a column in a database table. | string |
| displayName | - | The standardized text associated with a code in a particular code system. | string |
| databaseKey | - | A database key is an informational entity whose value is constructed from one or more database columns. | xref |
| countOfValues | - | Determining the number or amount of something. | int |
| totalValues | - | Pertaining to an entirety or whole, also constituting the full quantity or extent; complete; derived by addition. | int |
| differenceInValues | - | The quality of being unlike or dissimilar. | int |
| percentComplete | - | A fraction or ratio with 100 understood as the denominator. | decimal |

### Entity: cosasreports_datasources

Overview on the data sources connected to COSAS

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| source&#8251; | - | name of the source connected to COSAS | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| source&#8251; | - | name of the source connected to COSAS | string |
| type | - | Indication if the source is internal or external | enum |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| source&#8251; | - | name of the source connected to COSAS | string |
| type | - | Indication if the source is internal or external | enum |
| metadata | - | overivew of data provided | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| source&#8251; | - | name of the source connected to COSAS | string |
| type | - | Indication if the source is internal or external | enum |
| metadata | - | overivew of data provided | string |
| status | - | indication if the data source status (1: online/connected, -1: offline/not connected, 0: not activated) | int |

### Entity: cosasreports_jobs

Overview on scheduled jobs

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| name&#8251; | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| name&#8251; | - | - | string |
| description | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| name&#8251; | - | - | string |
| description | - | - | string |
| cron | - | - | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| name&#8251; | - | - | string |
| description | - | - | string |
| cron | - | - | string |
| isActive | - | - | bool |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| name&#8251; | - | - | string |
| description | - | - | string |
| cron | - | - | string |
| isActive | - | - | bool |
| dateLastRun | - | - | date |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| name&#8251; | - | - | string |
| description | - | - | string |
| cron | - | - | string |
| isActive | - | - | bool |
| dateLastRun | - | - | date |
| isStable | - | - | bool |

### Entity: cosasreports_refs_template

| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| value&#8251; | - | The information contained in a data field. It may represent a numeric quantity, a textual characterization, a date or time measurement, or some other state, depending on the nature of the attribute. | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| value&#8251; | - | The information contained in a data field. It may represent a numeric quantity, a textual characterization, a date or time measurement, or some other state, depending on the nature of the attribute. | string |
| description | - | A written or verbal account, representation, statement, or explanation of something | text |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| value&#8251; | - | The information contained in a data field. It may represent a numeric quantity, a textual characterization, a date or time measurement, or some other state, depending on the nature of the attribute. | string |
| description | - | A written or verbal account, representation, statement, or explanation of something | text |
| codesystem | - | A systematized collection of concepts that define corresponding codes. | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| value&#8251; | - | The information contained in a data field. It may represent a numeric quantity, a textual characterization, a date or time measurement, or some other state, depending on the nature of the attribute. | string |
| description | - | A written or verbal account, representation, statement, or explanation of something | text |
| codesystem | - | A systematized collection of concepts that define corresponding codes. | string |
| code | - | A symbol or combination of symbols which is assigned to the members of a collection. | string |
| Name | Label | Description | Data Type |
|:---- |:-----|:-----------|:---------|
| value&#8251; | - | The information contained in a data field. It may represent a numeric quantity, a textual characterization, a date or time measurement, or some other state, depending on the nature of the attribute. | string |
| description | - | A written or verbal account, representation, statement, or explanation of something | text |
| codesystem | - | A systematized collection of concepts that define corresponding codes. | string |
| code | - | A symbol or combination of symbols which is assigned to the members of a collection. | string |
| iri | - | A unique symbol that establishes identity of the resource. | hyperlink |

Note: The symbol &#8251; denotes attributes that are primary keys

