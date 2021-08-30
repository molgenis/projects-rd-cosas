#'////////////////////////////////////////////////////////////////////////////
#' FILE: build_data.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-08-30
#' MODIFIED: 2021-08-30
#' PURPOSE: process data and save into a single file
#' STATUS: in.progress
#' PACKAGES: NA
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

# get arguments from command line
args <- commandArgs(trailingOnly = TRUE)
stopifnot(args %in% c("cosasrefs", "cosasportal", "cosas"))

# pkgs
library2("data.table")
library2("openxlsx")
library2("cli")
source("R/utils_mapping.R")


cli_alert_info("Loading portal data (warnings can be ignored)")
source("R/_load.R")

#'//////////////////////////////////////

#' ~ 1 ~
#' Compile data for cosasportal

if (args == "cosasportal") {
    cli_alert_info("Compiling data for {.val {args}}")

    tryCatch({
        wb <- createWorkbook()
        addWorksheet(wb, "cosasportal_labs_array_adlas")
        addWorksheet(wb, "cosasportal_labs_array_darwin")
        addWorksheet(wb, "cosasportal_bench_cnv")
        addWorksheet(wb, "cosasportal_diagnoses")
        addWorksheet(wb, "cosasportal_labs_ngs_adlas")
        addWorksheet(wb, "cosasportal_labs_ngs_darwin")
        addWorksheet(wb, "cosasportal_patients")
        addWorksheet(wb, "cosasportal_samples")
        writeData(wb, "cosasportal_labs_array_adlas", portal_array_adlas)
        writeData(wb, "cosasportal_labs_array_darwin", portal_array_darwin)
        writeData(wb, "cosasportal_bench_cnv", portal_bench_cnv)
        writeData(wb, "cosasportal_diagnoses", portal_diagnoses)
        writeData(wb, "cosasportal_labs_ngs_adlas", portal_ngs_adlas)
        writeData(wb, "cosasportal_labs_ngs_darwin", portal_ngs_darwin)
        writeData(wb, "cosasportal_patients", portal_patients)
        writeData(wb, "cosasportal_samples", portal_samples)
        saveWorkbook(wb, "data/cosasportal/cosasportal.xlsx", TRUE)

    }, warning = function(warn) {
        cli_alert_warning("Unable to build data for {.val {args}}:\n{{warn}}")
    }, error = function(err) {
        cli_alert_danger("Unable to build data for {.val {args}}:\n{{err}}")
    })
}


#' ~ 2 ~
#' Compile data for cosasref
if (args == "cosasrefs") {
    cli_alert_info("Compiling data for {.val {args}}")

    tryCatch({
        source("R/mapping_cosasrefs.R")
        wb <- createWorkbook()
        addWorksheet(wb, "cosasrefs_diagnoses")
        addWorksheet(wb, "cosasrefs_testCodes")
        writeData(wb, "cosasrefs_diagnoses", cosasrefs_diagnoses)
        writeData(wb, "cosasrefs_testCodes", cosasrefs_testCodes)
        saveWorkbook(wb, "data/cosasrefs/cosasrefs.xlsx", overwrite = TRUE)

    }, warning = function(warn) {
        cli_alert_warning("Unable to build data for {.val {args}}:\n{.text {warn}}")
    }, error = function(err) {
        cli_alert_danger("Unable to build data for {.val {args}}:\n{.text {err}}")
    })
}


#' ~ 3 ~
#' Compile data for cosas
if (args == "cosas") {
    cli_alert_info("Compiling data for {.val {args}}")

    tryCatch({
        source("R/mapping_cosas.R")
        wb <- createWorkbook()
        addWorksheet(wb, "cosas_patients")
        addWorksheet(wb, "cosas_clinical")
        addWorksheet(wb, "cosas_samples")
        addWorksheet(wb, "cosas_labs_array")
        addWorksheet(wb, "cosas_labs_ngs")
        writeData(wb, "cosas_patients", cosas_patients)
        writeData(wb, "cosas_clinical", cosas_clinical)
        writeData(wb, "cosas_samples", cosas_samples)
        writeData(wb, "cosas_labs_array", cosas_labs_array)
        writeData(wb, "cosas_labs_ngs", cosas_labs_ngs)
        saveWorkbook(wb, "data/cosas/cosas.xlsx", TRUE)

    }, warning = function(warn) {
        cli_alert_warning("Unable to build data for {.val {args}}:\n{.text {warn}}")
    }, error = function(err) {
        cli_alert_danger("Unable to build data for {.val {args}}:\n{.text {err}}")
    })
}

# clean up
rm2()