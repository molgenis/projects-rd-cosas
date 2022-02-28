# COSAS

COSAS &mdash; or the **C**atalogue of **S**equences, **A**rrays, and **S**amples &mdash; runs on the [Unified Molgenis Data Model](https://github.com/molgenis/rd-datamodel). This repository contains all of the files and code required for maintaining the COSAS database, as well as additional EMX files that were built specifically for this project.

All EMX models are located in `src/emx/`. These models are created at build time using the [yamlemxconvert](https://pypi.org/project/yamlemxconvert/) python library. See [index.py](https://github.com/molgenis/molgenis-cosas/tree/main/src/index.py) for more information.

## Get Started

Sign in to your Molgenis instance or create a new one, and navigate to the scripts plugin. Copy the contents of the [setup.py](https://github.com/molgenis/molgenis-cosas/blob/main/python/setup.py) file into a new python script. Run the script. This will pull the EMX and all lookups from the GitHub repository into your Molgenis instance. Once this has completed, a few more items will need to be imported from this repository.

```shell
# add or set the url to your Molgenis instance
mcmd config set host

# import COSAS portal files
mcmd import -p dist/cosasportal.xlsx
mcmd import -p dist/cosasportal_mappings_biospecimentype.csv
mcmd import -p dist/cosasportal_mappings_genderidentity.csv
mcmd import -p dist/cosasportal_mappings_genomebuild.csv
mcmd import -p dist/cosasportal_mappings_samplereason.csv
mcmd import -p dist/cosasportal_mappings_sequencerinfo.csv

# import COSAS extensions
mcmd import -p dist/umdm_labProcedures.csv
mcmd import -p dist/umdm_lookups_biospecimenType.csv
mcmd import -p dist/umdm_organizations.csv

# import COSAS reports module
mcmd import -p dist/cosasreports.xlsx
```
