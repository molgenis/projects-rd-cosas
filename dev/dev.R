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