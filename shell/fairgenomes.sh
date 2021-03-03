# ////////////////////////////////////////////////////////////////////////////
# FILE: fairgenomes.sh
# AUTHOR: David Ruvolo
# CREATED: 2021-03-03
# MODIFIED: 2021-03-03
# PURPOSE: download fairgenomes data
# DEPENDENCIES: NA
# COMMENTS: NA
# ////////////////////////////////////////////////////////////////////////////


# create local copy as import from url does not work as expected; these files
# are ignored by git
curl https://raw.githubusercontent.com/fairgenomes/fairgenomes-semantic-model/main/transformation-output/molgenis-emx/sys_md_Package.tsv -o data/fairgenomes/sys_md_Package.tsv


curl https://raw.githubusercontent.com/fairgenomes/fairgenomes-semantic-model/main/transformation-output/molgenis-emx/personal_inclusionstatus_attributes.tsv -o data/fairgenomes/personal_inclusionstatus_attributes.tsv

curl https://raw.githubusercontent.com/fairgenomes/fairgenomes-semantic-model/main/transformation-output/molgenis-emx/personal_inclusionstatus.tsv -o data/fairgenomes/personal_inclusionstatus.tsv