#'////////////////////////////////////////////////////////////////////////////
#' FILE: build_emx.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-03-16
#' MODIFIED: 2021-09-01
#' PURPOSE: convert EMX yaml into CSVs
#' STATUS: working; ongoing
#' PACKAGES: dplyr; magrittr; openxlsx; cli
#' COMMENTS:
#'
#' This script can be run either block by block or using npm
#' In the package.json file, create a script that executes this script with
#' a single argument.
#'
#' The function `library2` can be found in the .Rprofile. This function
#' suppresses all startup messages.
#'
#'////////////////////////////////////////////////////////////////////////////


library2("dplyr")
library2("magrittr")
library2("openxlsx")
library2("cli")
source("R/utils_yaml_convert.R")


# get args from command
# when running the script, supply 1 argument: the entity ID
args <- commandArgs(trailingOnly = TRUE)


#' @name remove.files
#' @description Remove all files in a given directory
#' @param dir path to folder
# remove.files <- function(dir) {
#     invisible(sapply(list.files(dir, full.names = TRUE), file.remove))
# }


#'//////////////////////////////////////

#' ~ 1 ~
#' Convert COSAS Portal

if (args == "cosasportal") {
    cli_alert_info("Generating EMX for {.val cosasportal}")

    input <- "emx/src/cosas-portal.yml"
    output <- "emx/cosas-portal/cosasportal.xlsx"

    # compile emx
    tryCatch({
        cosas_portal <- yml_to_emx(path = input)
        cosas_portal$attributes <- cosas_portal$attributes %>%
            rename(`description-nl` = description.nl)
        cli_alert_success("Compiled {.file {input}}")
    }, warning = function(warn) {
        cli_alert_warning("Unable to compile {.file {input}}: \n {.val {warn}}")
    }, error = function(err) {
        cli_alert_danger("Unable to compile {.file {input}}: \n {.val {err}}")
    })

    # write emx
    tryCatch({
        invisible(
            createWorkbook() %T>%
            addWorksheet(., "packages") %T>%
            addWorksheet(., "entities") %T>%
            addWorksheet(., "attributes") %T>%
            writeData(., "packages", cosas_portal$packages) %T>%
            writeData(., "entities", cosas_portal$entities) %T>%
            writeData(., "attributes", cosas_portal$attributes) %T>%
            saveWorkbook(., output, overwrite = TRUE)
        )
        cli_alert_success("Saved {.file {output}}")
    }, warning = function(warn) {
        cli_alert_warning("Failed to save {.file {output}}:\n{.val {warn}}")
    }, error = function(err) {
        cli_alert_danger("Failed to save {.file {output}}:\n{.val {err}}")
    })
}

#'//////////////////////////////////////

#' ~ 2 ~
#' Convert COSAS References

if (args == "cosasrefs") {
    cli_alert_info("Generating EMX for {.val cosasrefs}")

    cli::cli_alert_info("Loading portal data...(warnings can be ignored)")
    source("R/_load.R")

    input <- "emx/src/cosas-refs.yml"
    output <- "emx/cosas-refs/cosasrefs.xlsx"

    # compile emx
    tryCatch({
        cosasrefs <- yml_to_emx(path = input)
        cosasrefs$attributes <- cosasrefs$attributes %>%
            rename(`label-nl` = label.nl, `description-nl` = description.nl)
        cli_alert_success("Compiled {.file {input}}")
    }, warning = function(warn) {
        cli_alert_warning("Unable to compile {.file {input}}: \n {.val {warn}}")
    }, error = function(err) {
        cli_alert_danger("Unable to compile {.file {input}}: \n {.val {err}}")
    })


    # write emx
    tryCatch({

        # compile data for lookup tables
        source("R/mapping_cosasrefs.R")

        # saving data
        invisible({
            wb <- createWorkbook()
            addWorksheet(wb, "packages")
            addWorksheet(wb, "entities")
            addWorksheet(wb, "attributes")
            addWorksheet(wb, "cosasrefs_availabilityStatus")
            addWorksheet(wb, "cosasrefs_biologicalSex")
            addWorksheet(wb, "cosasrefs_inclusionStatus")
            addWorksheet(wb, "cosasrefs_labIndications")
            addWorksheet(wb, "cosasrefs_diagnoses")
            addWorksheet(wb, "cosasrefs_testCodes")
            addWorksheet(wb, "cosasrefs_phenotype")
            writeData(wb, "packages", cosasrefs$packages)
            writeData(wb, "entities", cosasrefs$entities)
            writeData(wb, "attributes", cosasrefs$attributes)
            writeData(
                wb,
                "cosasrefs_availabilityStatus",
                cosasrefs$cosasrefs_availabilityStatus
            )
            writeData(
                wb,
                "cosasrefs_biologicalSex",
                cosasrefs$cosasrefs_biologicalSex
            )
            writeData(
                wb,
                "cosasrefs_inclusionStatus",
                cosasrefs$cosasrefs_inclusionStatus
            )
            writeData(
                wb,
                "cosasrefs_labIndications",
                cosasrefs$cosasrefs_labIndications
            )
            writeData(wb, "cosasrefs_diagnoses", cosasrefs_diagnoses)
            writeData(wb, "cosasrefs_testCodes", cosasrefs_testCodes)
            writeData(wb, "cosasrefs_phenotype", phenotypes)
            saveWorkbook(wb, output, overwrite = TRUE)
        })

        cli_alert_success("Saved {.file {output}}")
    }, warning = function(warn) {
        cli_alert_danger("Failed to save {.file {output}}:\n{.val {warn}}")
    }, error = function(err) {
        cli_alert_danger("Failed to save {.file {output}}:\n{.val {err}}")
    })
}

#'//////////////////////////////////////

#' ~ 3 ~
#' Convert COSAS package

if (args == "cosas") {
    cli_alert_info("Generating EMX for {.val cosas}")

    input <- "emx/src/cosas.yml"
    output <- "emx/cosas/cosas.xlsx"

    # compile emx
    tryCatch({
        cosas <- yml_to_emx(path = input)
        cosas$attributes <- cosas$attributes %>%
            rename(`label-nl` = label.nl, `description-nl` = description.nl)
        cli_alert_success("Compiled {.file {input}}")
    }, warning = function(warn) {
        cli_alert_warning("Unable to compile {.file {input}}: \n {.val {warn}}")
    }, error = function(err) {
        cli_alert_danger("Unable to compile {.file {input}}: \n {.val {err}}")
    })

    # write emx
    tryCatch({
        invisible(
            createWorkbook() %T>%
            addWorksheet(., "packages") %T>%
            addWorksheet(., "entities") %T>%
            addWorksheet(., "attributes") %T>%
            writeData(., "packages", cosas$packages) %T>%
            writeData(., "entities", cosas$entities) %T>%
            writeData(., "attributes", cosas$attributes) %T>%
            saveWorkbook(., output, overwrite = TRUE)
        )
        cli_alert_success("Saved {.file {output}}")
    }, warning = function(warn) {
        cli_alert_warning("Failed to save {.file {output}}:\n{.val {warn}}")
    }, error = function(err) {
        cli_alert_danger("Failed to save {.file {output}}:\n{.val {err}}")
    })
}
