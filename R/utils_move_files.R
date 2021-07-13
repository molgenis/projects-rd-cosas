#'////////////////////////////////////////////////////////////////////////////
#' FILE: utils_move_files.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-07-13
#' MODIFIED: 2021-07-13
#' PURPOSE: prep files for import
#' STATUS: in.progress
#' PACKAGES: dplyr
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

#' pkgs
suppressPackageStartupMessages(library(dplyr))

#' @name .xlsx__to__csv__filepath
#' @description convert filepath from xlsx to csv
#' @param path input filepath
#' @param outdir output directory
#' @return string containing a filepath
.xlsx__to__csv__filepath <- function(path, outdir) {
    out <- outdir

    if (substring(text = out, first = nchar(out)) != "/")
        out <- paste0(out, "/")


    path %>%
        basename(path = .) %>%
        gsub(pattern = ".xlsx", replacement = ".csv", x = .) %>%
        paste0(out, .)
}

#' read as xlsx and save as csv
files <- list.files("data", full.names = TRUE)
for (file in files) {
    cli::cli_alert_info("Processing file {.val {basename(file)}}")
    path <- .xlsx__to__csv__filepath(path = file, outdir = "data")
    readxl::read_xlsx(file) %>%
        readr::write_csv(d, path)
}