#'////////////////////////////////////////////////////////////////////////////
#' FILE: _load.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-07-29
#' MODIFIED: 2021-08-16
#' PURPOSE: load and combine portal files (if desired)
#' STATUS: working
#' PACKAGES: readxl, openxlsx
#' COMMENTS: Use this script to consistently load all files across scripts
#'      adjust the write argument if needed
#'////////////////////////////////////////////////////////////////////////////

cli::cli_alert_info("Loading portal files...")

portal_patients <- readxl::read_xlsx(
    path = "_raw/cosasportal_patients.xlsx",
    sheet = 1,
    col_types = c("text", "date", "text", "date", rep("text", 4))
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
    col_types = "text"
)

portal_array_darwin <- readxl::read_xlsx(
    path = "_raw/cosasportal_array_darwin.xlsx",
    sheet = 1,
    col_types = c("text", "text", "date", rep("text", 4))
)

portal_ngs_adlas <- readxl::read_xlsx(
    path = "_raw/cosasportal_ngs_adlas.xlsx",
    sheet = 1,
    col_types = "text"
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


# check
if (
    !is.null(portal_patients) &
    !is.null(portal_diagnoses) &
    !is.null(portal_samples) &
    !is.null(portal_array_adlas) &
    !is.null(portal_array_darwin) &
    !is.null(portal_ngs_adlas) &
    !is.null(portal_ngs_darwin)
) {
    cli::cli_alert_success("Successfully loaded files! :-) ")
} else {
    cli::cli_alert_danger("Failed to load files :-(")
}