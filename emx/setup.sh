# ////////////////////////////////////////////////////////////////////////////
# FILE: setup.sh
# AUTHOR: David Ruvolo
# CREATED: 2021-12-06
# MODIFIED: 2021-12-06
# PURPOSE: import script for COSAS
# DEPENDENCIES: NA
# COMMENTS: NA
# ////////////////////////////////////////////////////////////////////////////


# <!--- start: utils_create_setup.py --->
mcmd import -u https://raw.githubusercontent.com/molgenis/rd-datamodel/main/emx/dist/urdm.xlsx
mcmd import -u https://raw.githubusercontent.com/molgenis/rd-datamodel/main/emx/lookups/urdm_lookups_anatomicalSource.csv
mcmd import -u https://raw.githubusercontent.com/molgenis/rd-datamodel/main/emx/lookups/urdm_lookups_ancestry.csv
mcmd import -u https://raw.githubusercontent.com/molgenis/rd-datamodel/main/emx/lookups/urdm_lookups_biospecimenType.csv
mcmd import -u https://raw.githubusercontent.com/molgenis/rd-datamodel/main/emx/lookups/urdm_lookups_country.csv
mcmd import -u https://raw.githubusercontent.com/molgenis/rd-datamodel/main/emx/lookups/urdm_lookups_dataUsePermissions.csv
mcmd import -u https://raw.githubusercontent.com/molgenis/rd-datamodel/main/emx/lookups/urdm_lookups_diseases.csv
mcmd import -u https://raw.githubusercontent.com/molgenis/rd-datamodel/main/emx/lookups/urdm_lookups_genomeAccessions.csv
mcmd import -u https://raw.githubusercontent.com/molgenis/rd-datamodel/main/emx/lookups/urdm_lookups_genotypicSex.csv
mcmd import -u https://raw.githubusercontent.com/molgenis/rd-datamodel/main/emx/lookups/urdm_lookups_inclusionCriteria.csv
mcmd import -u https://raw.githubusercontent.com/molgenis/rd-datamodel/main/emx/lookups/urdm_lookups_inclusionStatus.csv
mcmd import -u https://raw.githubusercontent.com/molgenis/rd-datamodel/main/emx/lookups/urdm_lookups_labIndication.csv
mcmd import -u https://raw.githubusercontent.com/molgenis/rd-datamodel/main/emx/lookups/urdm_lookups_ngsKits.csv
mcmd import -u https://raw.githubusercontent.com/molgenis/rd-datamodel/main/emx/lookups/urdm_lookups_pathologicalState.csv
mcmd import -u https://raw.githubusercontent.com/molgenis/rd-datamodel/main/emx/lookups/urdm_lookups_phenotype.csv
mcmd import -u https://raw.githubusercontent.com/molgenis/rd-datamodel/main/emx/lookups/urdm_lookups_phenotypicSex.csv
mcmd import -u https://raw.githubusercontent.com/molgenis/rd-datamodel/main/emx/lookups/urdm_lookups_sequencingInstrumentModels.csv
mcmd import -u https://raw.githubusercontent.com/molgenis/rd-datamodel/main/emx/lookups/urdm_lookups_sequencingMethods.csv
mcmd import -u https://raw.githubusercontent.com/molgenis/rd-datamodel/main/emx/lookups/urdm_lookups_sequencingPlatform.csv
mcmd import -u https://raw.githubusercontent.com/molgenis/rd-datamodel/main/emx/lookups/urdm_lookups_studyStatus.csv
# <!--- end: utils_create_setup.py --->

# import lookup tables and extensions first
mcmd import -p emx/lookups/cosas_labProcedures.csv --as urdm_labProcedures
mcmd import -p emx/lookups/cosas_lookups_biospecimenTypes_extra.csv --as urdm_lookups_biospecimenType
mcmd import -p emx/lookups/cosas_organizations.csv --as urdm_organizations

# import tables
mcmd import -p data/cosas/subjects.csv --as urdm_subjects
mcmd import -p data/cosas/clinical.csv --as urdm_clinical
mcmd import -p data/cosas/samples.csv --as urdm_samples
mcmd import -p data/cosas/samplePreparation.csv --as urdm_samplePreparation
mcmd import -p data/cosas/sequencing.csv --as urdm_sequencing


