#' ////////////////////////////////////////////////////////////////////////////
#' FILE: generate.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-03-02
#' MODIFIED: 2021-03-02
#' PURPOSE: generate dataset
#' STATUS: working
#' PACKAGES: NA
#' COMMENTS: NA
#' ////////////////////////////////////////////////////////////////////////////

# for development of prototype
devtools::load_all()

#' build new data
g <- generator$new(n = 100, patient_visits = 1)
g$random_dataset()
g$data

# save data
readr::write_tsv(g$data$patients, "emx/cosas_patients.tsv")
readr::write_tsv(g$data$samples, "emx/cosas_samples.tsv")
readr::write_tsv(g$data$analysis, "emx/cosas_analysis.tsv")

# convert yml to emx, and then write to file
model <- yml_to_emx(path = "emx/cosas-prototype.yml")
model$packages <- model$packages %>% dplyr::rename(id = name)

# remove existing files
invisible(
    sapply(
        list.files(
            path = "emx",
            full.names = TRUE,
            pattern = "((cosas_[a-zA-Z])|(sys_[a-zA-Z])\\.tsv)",
        ),
        file.remove
    )
)

write_emx(model)
