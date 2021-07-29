#'////////////////////////////////////////////////////////////////////////////
#' FILE: mapping_cosasportal.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-07-28
#' MODIFIED: 2021-07-29
#' PURPOSE: load and combine portal files (if desired)
#' STATUS: working
#' PACKAGES: readxl, openxlsx
#' COMMENTS: Use this script to consistently load all files across scripts
#'      adjust the write argument if needed
#'////////////////////////////////////////////////////////////////////////////

# source data
source("R/_load.R")

# write `cosasportal`
cli::cli_alert_info("Writing portal data to file...")
openxlsx::createWorkbook() %T>%
    openxlsx::addWorksheet(., "cosasportal_labs_array_adlas") %T>%
    openxlsx::addWorksheet(., "cosasportal_labs_array_darwin") %T>%
    openxlsx::addWorksheet(., "cosasportal_bench_cnv") %T>%
    openxlsx::addWorksheet(., "cosasportal_diagnoses") %T>%
    openxlsx::addWorksheet(., "cosasportal_labs_ngs_adlas") %T>%
    openxlsx::addWorksheet(., "cosasportal_labs_ngs_darwin") %T>%
    openxlsx::addWorksheet(., "cosasportal_patients") %T>%
    openxlsx::addWorksheet(., "cosasportal_samples") %T>%
    openxlsx::writeData(
        ., "cosasportal_labs_array_adlas", portal_array_adlas
    ) %T>%
    openxlsx::writeData(
        ., "cosasportal_labs_array_darwin", portal_array_darwin
    ) %T>%
    openxlsx::writeData(., "cosasportal_bench_cnv", portal_bench_cnv) %T>%
    openxlsx::writeData(., "cosasportal_diagnoses", portal_diagnoses) %T>%
    openxlsx::writeData(
        ., "cosasportal_labs_ngs_adlas", portal_ngs_adlas
    ) %T>%
    openxlsx::writeData(
        ., "cosasportal_labs_ngs_darwin", portal_ngs_darwin
    ) %T>%
    openxlsx::writeData(., "cosasportal_patients", portal_patients) %T>%
    openxlsx::writeData(., "cosasportal_samples", portal_samples) %T>%
    openxlsx::saveWorkbook(., "data/cosasportal/cosasportal.xlsx", TRUE)