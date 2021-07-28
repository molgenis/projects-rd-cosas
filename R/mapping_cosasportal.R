#'////////////////////////////////////////////////////////////////////////////
#' FILE: mapping_cosasportal.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-07-28
#' MODIFIED: 2021-07-28
#' PURPOSE: combine portal files
#' STATUS: in.progress
#' PACKAGES: readxl, openxlsx
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

portal_patients <- readxl::read_xlsx(
    path = "_raw/cosasportal_patients.xlsx",
    sheet = 1,
    col_types = c("text", "date", "text", "date", rep("text", 4)),
)

portal_diagnoses <- readxl::read_xlsx(
    path = "_raw/cosasportal_diagnoses.xlsx",
    sheet = 1,
    col_types = c(rep("text", 5), "date", "text")
)

portal_samples <- readxl::read_xlsx(
    path = "_raw/cosasportal_samples.xlsx",
    sheet = 1,
    col_types = "text"
)

portal_array_adlas <- readxl::read_xlsx(
    path = "_raw/cosasportal_array_adlas.xlsx",
    sheet = 1,
    col_types = c(rep("text", 29))
)

portal_array_darwin <- readxl::read_xlsx(
    path = "_raw/cosasportal_array_darwin.xlsx",
    sheet = 1,
    col_types = c(rep("text", 2), "date", rep("text", 4))
)

portal_ngs_adlas <- readxl::read_xlsx(
    path = "_raw/cosasportal_ngs_adlas.xlsx",
    sheet = 1,
    col_types = c(rep("text", 14))
)

portal_ngs_darwin <- readxl::read_xlsx(
    path = "_raw/cosasportal_ngs_darwin.xlsx",
    sheet = 1,
    col_types = c(rep("text", 2), "date", rep("text", 10))
)

portal_bench_cnv <- readxl::read_xlsx(
    path = "_raw/cosasportal_bench_cnv.xlsx",
    sheet = 1,
    col_types = c(rep("text", 6), "date")
)

# write `cosasportal`
write <- FALSE
if (write) {
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
}
rm(write)