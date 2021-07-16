#'////////////////////////////////////////////////////////////////////////////
#' FILE: cosas_emx.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-03-16
#' MODIFIED: 2021-07-13
#' PURPOSE: convert EMX yaml into CSVs
#' STATUS: working
#' PACKAGES: dplyr
#' COMMENTS: This script can be run either block by block or using npm
#' In the package.json file, create a script that executes this script with
#' a single argument.
#'////////////////////////////////////////////////////////////////////////////


suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(magrittr))
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
    cli::cli_alert_info("Generating EMX for {.val cosasportal}")

    input <- "emx/src/cosas-portal.yml"
    output <- "emx/cosas-portal/cosasportal.xlsx"

    # compile emx
    tryCatch({
        cosas_portal <- yml_to_emx(path = "emx/src/cosas-portal.yml")
        cosas_portal$attributes <- cosas_portal$attributes %>%
            dplyr::rename(
                `label-nl` = label.nl,
                `description-nl` = description.nl
            )
        cli::cli_alert_success("Compiled {.file {input}}")
    }, warning = function(warn) {
        cli::cli_alert_warning("Unable to compile {.file {input}}: \n {.val {warn}}")
    }, error = function(err) {
        cli::cli_alert_danger("Unable to compile {.file {input}}: \n {.val {err}}")
    })

    # write emx
    tryCatch({
        invisible(
            openxlsx::createWorkbook() %T>%
            openxlsx::addWorksheet(., "packages") %T>%
            openxlsx::addWorksheet(., "entities") %T>%
            openxlsx::addWorksheet(., "attributes") %T>%
            openxlsx::writeData(., "packages", cosas_portal$packages) %T>%
            openxlsx::writeData(., "entities", cosas_portal$entities) %T>%
            openxlsx::writeData(., "attributes", cosas_portal$attributes) %T>%
            openxlsx::saveWorkbook(wb = ., file = output, overwrite = TRUE)
        )
        cli::cli_alert_success("Saved {.file {output}}")
    }, warning = function(warn) {
        cli::cli_alert_warning("Failed to save {.file {output}}:\n{.val {warn}}")
    }, error = function(err) {
        cli::cli_alert_danger("Failed to save {.file {output}}:\n{.val {err}}")
    })
}

#'//////////////////////////////////////

#' ~ 2 ~
#' Convert COSAS References

if (args == "cosasrefs") {
    cli::cli_alert_info("Generating EMX for {.val cosasrefs}")

    input <- "emx/src/cosas-refs.yml"
    output <- "emx/cosas-refs/cosasrefs.xlsx"

    # compile emx
    tryCatch({
        cosas_refs <- yml_to_emx(path = input)
        cosas_refs$attributes <- cosas_refs$attributes %>%
            dplyr::rename(
                `label-nl` = label.nl,
                `description-nl` = description.nl
            )
        cli::cli_alert_success("Compiled {.file {input}}")
    }, warning = function(warn) {
        cli::cli_alert_warning("Unable to compile {.file {input}}: \n {.val {warn}}")
    }, error = function(err) {
        cli::cli_alert_danger("Unable to compile {.file {input}}: \n {.val {err}}")
    })

    # write emx
    tryCatch({
        invisible(
            openxlsx::createWorkbook() %T>%
            openxlsx::addWorksheet(., "packages") %T>%
            openxlsx::addWorksheet(., "entities") %T>%
            openxlsx::addWorksheet(., "attributes") %T>%
            openxlsx::addWorksheet(., "cosasrefs_biological_sex") %T>%
            openxlsx::writeData(., "packages", cosas_refs$packages) %T>%
            openxlsx::writeData(., "entities", cosas_refs$entities) %T>%
            openxlsx::writeData(., "attributes", cosas_refs$attributes) %T>%
            openxlsx::writeData(
                wb = .,
                sheet = "cosasrefs_biological_sex",
                x = cosas_refs$cosasrefs_biological_sex
            ) %T>%
            openxlsx::saveWorkbook(wb = ., file = output, overwrite = TRUE)
        )
        cli::cli_alert_success("Saved {.file {output}}")
    }, warning = function(warn) {
        cli::cli_alert_warning("Failed to save {.file {output}}:\n{.val {warn}}")
    }, error = function(err) {
        cli::cli_alert_danger("Failed to save {.file {output}}:\n{.val {err}}")
    })
}

#'//////////////////////////////////////

#' ~ 3 ~
#' Convert COSAS package

if (args == "cosas") {
    cli::cli_alert_info("Generating EMX for {.val cosas}")

    input <- "emx/src/cosas.yml"
    output <- "emx/cosas/cosas.xlsx"

    # compile emx
    tryCatch({
        cosas <- yml_to_emx(path = input)
        cosas$attributes <- cosas$attributes %>%
            dplyr::rename(
                `label-nl` = label.nl,
                `description-nl` = description.nl
            )
        cli::cli_alert_success("Compiled {.file {input}}")
    }, warning = function(warn) {
        cli::cli_alert_warning("Unable to compile {.file {input}}: \n {.val {warn}}")
    }, error = function(err) {
        cli::cli_alert_danger("Unable to compile {.file {input}}: \n {.val {err}}")
    })

    # write emx
    tryCatch({
        invisible(
            openxlsx::createWorkbook() %T>%
            openxlsx::addWorksheet(., "packages") %T>%
            openxlsx::addWorksheet(., "entities") %T>%
            openxlsx::addWorksheet(., "attributes") %T>%
            openxlsx::writeData(., "packages", cosas$packages) %T>%
            openxlsx::writeData(., "entities", cosas$entities) %T>%
            openxlsx::writeData(., "attributes", cosas$attributes) %T>%
            openxlsx::saveWorkbook(wb = ., file = output, overwrite = TRUE)
        )
        cli::cli_alert_success("Saved {.file {output}}")
    }, warning = function(warn) {
        cli::cli_alert_warning("Failed to save {.file {output}}:\n{.val {warn}}")
    }, error = function(err) {
        cli::cli_alert_danger("Failed to save {.file {output}}:\n{.val {err}}")
    })
}
