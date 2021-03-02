#'////////////////////////////////////////////////////////////////////////////
#' FILE: generate.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-03-02
#' MODIFIED: 2021-03-02
#' PURPOSE: generate dataset
#' STATUS: working
#' PACKAGES: NA
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

# for development of prototype
devtools::load_all()

#' build new data
g <- generator$new(n = 20, patient_visits = 1)
g$random_dataset()
g$data

# save data
readr::write_tsv(g$data$patients, "emx/cosas_patients.tsv")
readr::write_tsv(g$data$samples, "emx/cosas_samples.tsv")
readr::write_tsv(g$data$analysis, "emx/cosas_analysis.tsv")

# convert yml to emx
model <- yml_to_emx(path = "emx/cosas-prototype.yml")
readr::write_tsv(model$packages %>% rename(id = name), "emx/sys_md_Package.tsv")
readr::write_tsv(model$entities, "emx/cosas_entites.tsv")
readr::write_tsv(model$attributes, "emx/cosas_attributes.tsv")
