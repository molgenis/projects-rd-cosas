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


devtools::load_all()

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
g <- generator$new(n = 100, patient_visits = 1)
g$random_dataset()
g$data

# save data
readr::write_tsv(g$data$patients, "data/cosas/cosas_patients.tsv")
readr::write_tsv(g$data$samples, "data/cosas/cosas_samples.tsv")
readr::write_tsv(g$data$analysis, "data/cosas/cosas_analysis.tsv")
