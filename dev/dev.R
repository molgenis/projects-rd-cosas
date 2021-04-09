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

#' pkgs
install.packages("devtools")
install.packages("usethis")
install.packages("R6")
install.packages("tidyr")
install.packages("dplyr")
install.packages("yaml")
install.packages("purrr")
install.packages("readr")

#' src
usethis::create_project(".")