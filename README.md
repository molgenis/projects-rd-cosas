# Samples Registry

The `molgenis-cosas` repository contains all of the code and scripts used to create the samples database. The EMX is defined in a series of `.yml` files (see `data/_emx`) and converted using the `yml_to_emx` function.

## Getting Started

This project uses a mix of python and R scripts to generate the COSAS data model. The model is written across a few yaml files, and then built using npm scripts. Before you get started, make sure R ([cran.r-project.org](https://cran.r-project.org)) is installed, and then install the [renv](https://github.com/rstudio/renv/) package.

```r
# install renv with remotes
if (!requireNamespace("remotes"))
  install.packages("remotes")

remotes::install_github("rstudio/renv")

# restore renv library
renv::restore()
```

### Building the data model

There are a number of scripts available that build parts of the data model or everything.

| script               | description                                          |
|----------------------|------------------------------------------------------|
| `molgenis-config`    | sets molgenis commander host                         |
| `build-cosas`        | compiles `cosas.yml` into EMX                        |
| `build-cosasrefs`    | compiles `cosas-refs` into EMX                       |
| `build-cosasportal`  | compiles `cosas-portal.yml` into EMX                 |
| `import-cosas`       | imports `cosas.xlsx` into COSAS                      |
| `import-cosasrefs`   | imports `cosasrefs.xlsx` into COSAS                  |
| `import-cosasportal` | imports `cosasportal.xslx` into COSAS                |
| `cosas`              | builds and imports the main COSAS tables             |
| `cosasrefs`          | builds and imports COSAS reference tables            |
| `cosasportal`        | builds and imports COSAS Portal tables               |
| `build`              | builds all EMX files (cosas, cosasrefs, cosasportal) |
| `import`             | imports all EMX files into COSAS                     |

Run each command with `npm run` or `yarn`.
