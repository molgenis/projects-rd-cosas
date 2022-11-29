
# Consent Data

## Tables

- Subjects
- Consent Summary (status): aggregate of "raw" consent data
- Consent Historical (raw): all signed forms by patients

## Table: summary

- identifier
- patientID
- link to raw: one_to_many
- material use: boolean
- recontact: boolean
- datausePermission: research
- incidental findings: boolean

## Table: raw

- identifier
- patientID
- consent form used
- collected by: use "geneticadiagnostiek"
- signing date
- consent withdrawn
- system

## Lookups

- For "material for research use" add another entry in the "dataUseModifiers" lookup.

## Data Processing Notes

While writing the processing script, I encountered several issues in the data. We can write methods to handle these cases, but it would be better to fix these values in the datasets before we import into COSAS.

- values that are only characters: there instances where the value in a column is a character, e.g., `,`, `/`, `?`. These cases are removed, but there are some tricker cases: e.g., `? (<some text here>)`. If these values are important, they should be resolved beforehand.
- There are some cases where dates in not in the date column. This should be fixed in the spreadsheet.
- For date columns, there are several cases where there are multiple dates separated by a character, e.g., '2022-11-01 / 2022-11-02'. Which date is the correct one? For now, I'm mapping the first date. These should be resolved in the spreadsheet along with any cases that are more information than the signing date.
- If possible, the date formatting should be fixed. The preferred format is `YYYY-mm-dd` (or `jjjj-mm-dd`). Was there an issue where dates were in multiple formats? `mm-dd-yyyy`, `dd-mm-yyyy`, etc. Was that fixed?
- After fixing the previous two issues, there were still some issues with the dates. Some date values where formatted as `mm-dd-yyy` (e.g., `11-08-202`). Is it `2020`, `2021`, or `2022`? It's best if these cases are fixed in the spreadsheet rather than writing conditions to fix all of these formatting issues. For now, I'm removing any case that does not match the format: `xx-xx-xxxx`. Other examples include: `xx-xx-209`.
