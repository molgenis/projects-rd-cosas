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

# run
mcmd config set host
mcmd import -p emx/sys_md_Package.tsv

mcmd import -p emx/cosas_labIndications_attributes.tsv --as attributes --in cosas
mcmd import -p emx/cosas_aandoening_attributes.tsv --as attributes --in cosas
mcmd import -p emx/cosas_analysis_attributes.tsv --as attributes --in cosas
mcmd import -p emx/cosas_patients_attributes.tsv --as attributes --in cosas
mcmd import -p emx/cosas_samples_attributes.tsv --as attributes --in cosas

mcmd import -p emx/cosas_labIndications.tsv --in cosas
mcmd import -p emx/cosas_aandoening.tsv --in cosas
mcmd import -p emx/cosas_analysis.tsv --in cosas
mcmd import -p emx/cosas_patients.tsv --in cosas
mcmd import -p emx/cosas_samples.tsv --in cosas
