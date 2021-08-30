#'////////////////////////////////////////////////////////////////////////////
#' FILE: mapping_cosasportal.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-07-28
#' MODIFIED: 2021-08-30
#' PURPOSE: load and combine portal files (if desired)
#' STATUS: working
#' PACKAGES: openxlsx
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

# source data
source("R/_load.R")

# write `cosasportal`
cli::cli_alert_info("Writing portal data to file...")
wb <- openxlsx::createWorkbook()
openxlsx::addWorksheet(wb, "cosasportal_labs_array_adlas")
openxlsx::addWorksheet(wb, "cosasportal_labs_array_darwin")
openxlsx::addWorksheet(wb, "cosasportal_bench_cnv")
openxlsx::addWorksheet(wb, "cosasportal_diagnoses")
openxlsx::addWorksheet(wb, "cosasportal_labs_ngs_adlas")
openxlsx::addWorksheet(wb, "cosasportal_labs_ngs_darwin")
openxlsx::addWorksheet(wb, "cosasportal_patients")
openxlsx::addWorksheet(wb, "cosasportal_samples")
openxlsx::writeData(wb, "cosasportal_labs_array_adlas", portal_array_adlas)
openxlsx::writeData(wb, "cosasportal_labs_array_darwin", portal_array_darwin)
openxlsx::writeData(wb, "cosasportal_bench_cnv", portal_bench_cnv)
openxlsx::writeData(wb, "cosasportal_diagnoses", portal_diagnoses)
openxlsx::writeData(wb, "cosasportal_labs_ngs_adlas", portal_ngs_adlas)
openxlsx::writeData(wb, "cosasportal_labs_ngs_darwin", portal_ngs_darwin)
openxlsx::writeData(wb, "cosasportal_patients", portal_patients)
openxlsx::writeData(wb, "cosasportal_samples", portal_samples)
openxlsx::saveWorkbook(wb, "data/cosasportal/cosasportal.xlsx", TRUE)

# clean up
rm2()