#'////////////////////////////////////////////////////////////////////////////
#' FILE: build_emx.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-03-16
#' MODIFIED: 2021-08-30
#' PURPOSE: convert EMX yaml into CSVs
#' STATUS: working
#' PACKAGES: dplyr; magrittr; openxlsx; cli
#' COMMENTS: This script can be run either block by block or using npm
#' In the package.json file, create a script that executes this script with
#' a single argument.
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
        invisible(
            createWorkbook() %T>%
            addWorksheet(., "packages") %T>%
            addWorksheet(., "entities") %T>%
            addWorksheet(., "attributes") %T>%
            addWorksheet(., "cosasrefs_availabilityStatus") %T>%
            addWorksheet(., "cosasrefs_biologicalSex") %T>%
            addWorksheet(., "cosasrefs_inclusionStatus") %T>%
            addWorksheet(., "cosasrefs_labIndications") %T>%
            writeData(., "packages", cosasrefs$packages) %T>%
            writeData(., "entities", cosasrefs$entities) %T>%
            writeData(., "attributes", cosasrefs$attributes) %T>%
            writeData(
                .,
                "cosasrefs_availabilityStatus",
                cosasrefs$cosasrefs_availabilityStatus
            ) %T>%
            writeData(
                ., "cosasrefs_biologicalSex", cosasrefs$cosasrefs_biologicalSex
            ) %T>%
            writeData(
                ., "cosasrefs_inclusionStatus", cosasrefs$cosasrefs_inclusionStatus
            ) %T>%
            writeData(
                ., "cosasrefs_labIndications", cosasrefs$cosasrefs_labIndications
            ) %T>%
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
