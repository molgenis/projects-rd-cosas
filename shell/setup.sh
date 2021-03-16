# ////////////////////////////////////////////////////////////////////////////
# FILE: setup.sh
# AUTHOR: David Ruvolo
# CREATED: 2021-03-01
# MODIFIED: 2021-03-01
# PURPOSE: import prototype into molgenis
# DEPENDENCIES: NA
# COMMENTS: NA
# ////////////////////////////////////////////////////////////////////////////

# init
# mcmd config add host 
# https://cosas-acc.gcc.rug.nl/
mcmd config set host


# import Fair Genomes
mcmd import -p data/fairgenomes/sys_md_Package.tsv
mcmd import -p data/fairgenomes/personal_inclusionstatus_attributes.tsv --as attributes --in fair-genomes
mcmd import -p data/fairgenomes/personal_inclusionstatus.tsv --as fair-genomes_personal_inclusionstatus --in fair-genomes


# import cosas mappings
mcmd import -p data/cosas-mappings/sys_md_Package.tsv
mcmd import -p data/cosas-mappings/cosasmaps_inclusionStatus_attributes.tsv --as attributes --in cosasmaps
mcmd import -p data/cosas-mappings/cosasmaps_inclusionStatus.tsv --as cosasmaps_inclusionStatus

# import cosas lookups
mcmd import -p data/cosas-lookups/sys_md_Package.tsv
mcmd import -p data/cosas-lookups/cosasrefs_diagnosis_attributes.tsv --as attributes --in cosasrefs
mcmd import -p data/cosas-lookups/cosasrefs_labIndications_attributes.tsv --as attributes --in cosasrefs
mcmd import -p data/cosas-lookups/cosasrefs_diagnosis.tsv --as cosasrefs_diagnosis
mcmd import -p data/cosas-lookups/cosasrefs_labIndications.tsv --as cosasrefs_labIndications


# import cosas db
mcmd import -p data/cosas/sys_md_Package.tsv
mcmd import -p data/cosas/cosas_patients_attributes.tsv --as attributes --in cosas
mcmd import -p data/cosas/cosas_samples_attributes.tsv --as attributes --in cosas
mcmd import -p data/cosas/cosas_labinfo_attributes.tsv --as attributes --in cosas
mcmd import -p data/cosas/cosas_files_attributes.tsv --as attributes --in cosas

# mcmd import -p data/cosas/cosas_analysis.tsv --in cosas
# mcmd import -p data/cosas/cosas_patients.tsv --in cosas
# mcmd import -p data/cosas/cosas_samples.tsv --in cosas