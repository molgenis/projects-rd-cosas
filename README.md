# COSAS

COSAS &mdash; or the **C**atalogue of **S**equences, **A**rrays, and **S**amples &mdash; runs on the [Unified Model](https://github.com/molgenis/rd-datamodel). This repository contains all of the files and code required for maintaining the COSAS database, as well as additional EMX files that were built specifically for this project.

All EMX models are located in `model` folder. These models are created at build time using the [yamlemxconvert](https://pypi.org/project/yamlemxconvert/) python library. See [index.py](https://github.com/molgenis/molgenis-cosas/tree/main/src/index.py) for more information.

## Get Started

Sign in to your Molgenis instance or create a new one, and navigate to the scripts plugin. Copy the contents of the [setup.py](https://github.com/molgenis/molgenis-cosas/blob/main/cosas/setup_umdm.py) file into a new python script. Run the script. This will pull the EMX and all lookups from the GitHub repository into your Molgenis instance.

Once this has completed, a few more COSAS specific files will need to be imported. Use the [molgenis commander](https://github.com/molgenis/molgenis-tools-commander) to import the files.

```shell
# add or set the url to your Molgenis instance
mcmd config set host

# import COSAS EMX files
mcmd import -p dist/cosasportal.xlsx
mcmd import -p dist/cosasmpapings.xlsx
mcmd import -p dist/cosasreports.xlsx

# import COSAS lookups and unified model extensions
mcmd import -p lookups/cosasmappings_biospecimentype.csv
mcmd import -p lookups/cosasmappings_cineasmappings.csv
mcmd import -p lookups/cosasmappings_genderatbirth.csv
mcmd import -p lookups/cosasmappings_genderidentity.csv
mcmd import -p lookups/cosasmappings_genomebuild.csv
mcmd import -p lookups/cosasmappings_samplereason.csv
mcmd import -p lookups/cosasmappings_sequencerinfo.csv
mcmd import -p lookups/umdm_labProcedures.csv
mcmd import -p lookups/umdm_lookups_biospecimenType.csv
mcmd import -p lookups/umdm_organizations.csv
```
