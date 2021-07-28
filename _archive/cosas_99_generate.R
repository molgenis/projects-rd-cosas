#' ////////////////////////////////////////////////////////////////////////////
#' FILE: generate.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-03-02
#' MODIFIED: 2021-03-16
#' PURPOSE: generate dataset
#' STATUS: working
#' PACKAGES: NA
#' COMMENTS: NA
#' ////////////////////////////////////////////////////////////////////////////


suppressPackageStartupMessages(library(dplyr))
source("R/utils_generator.R")

# remove existing files
invisible(
    sapply(
        list.files(
            path = "data/cosas",
            full.names = TRUE,
            pattern = "((cosas_[a-zA-Z])|(sys_[a-zA-Z])\\.tsv)",
        ),
        file.remove
    )
)


#' build new data
g <- generator$new(n = 25)
g$random_dataset()
g$data

# save data
readr::write_tsv(g$data$patients, "data/test/cosas_patients.tsv")
readr::write_tsv(g$data$samples, "data/test/cosas_samples.tsv")
readr::write_tsv(g$data$labinfo, "data/test/cosas_labinfo.tsv")
readr::write_tsv(g$data$files, "data/test/cosas_files.tsv")
