# COSAS Datatables

COSAS has several tables that is populated by data from Darwin.

- Samples
- Sample Preparations
- Sequencing

## Samples

This table provides a summary of all samples in ADLAS associated with a patient. Each row in the table is a distinct patient and sample. Each row (i.e., samples) are linked to the record in the patients table.

This table should be fine, except that we do not have adviesvraag and indicatie.

- DNAnumr
- MDN_UMCGnr
- Adviesvraag: comma separated string
- Indicatie: comma separated string
- BiologischeMateriaal

## Sample Preparation

The purpose of this table is to link samples to a lab procedure (i.e., test code). Each row is a distinct sample, test codes, and adviesvraag. (Array and all NGS.)

- DNAnumr
- Test Code
- Adviesvraag
- library Preparation Kit: prep kit
- target enrichment kit
- barcode: dna sequence
- batch numr: comma separated string

## Sequencing

This table should also show all NGS tests.

- DNAnumr
- Test code
- Advisevraag
- Indicatie
- Test Date: date entered the system
- sequencing platform
- sequencer
- (sequencing method: derived from test code)
- reference genome used (always GRCh37)

Columns for future consideration

- average read depth
- observed read length
- observed insert size
- percentage Q30
- percentage TR20
