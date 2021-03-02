#'////////////////////////////////////////////////////////////////////////////
#' FILE: dev.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-02-26
#' MODIFIED: 2021-03-01
#' PURPOSE: workspace management
#' STATUS: in.progress
#' PACKAGES: NA
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

# init renv
renv::init(bare = TRUE)
renv::snapshot()

#'//////////////////////////////////////

#' src
usethis::create_project(".")
usethis::use_description(check_name = FALSE)

# pkgs
usethis::use_package("dplyr")
usethis::use_package("R6")
usethis::use_package("stringi")
usethis::use_package("purrr")
usethis::use_package("openxlsx")
usethis::use_package("readr")
usethis::use_package("yaml")
usethis::use_pipe()