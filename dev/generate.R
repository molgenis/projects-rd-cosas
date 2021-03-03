#' ////////////////////////////////////////////////////////////////////////////
#' FILE: generate.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-03-02
#' MODIFIED: 2021-03-03
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


# convert yml to emx, and then write to file
model <- yml_to_emx(path = "data/cosas/cosas-prototype.yml")
model$packages <- model$packages %>% dplyr::rename(id = name)


# save data
readr::write_tsv(g$data$patients, "data/cosas/cosas_patients.tsv")
readr::write_tsv(g$data$samples, "data/cosas/cosas_samples.tsv")
readr::write_tsv(g$data$analysis, "data/cosas/cosas_analysis.tsv")
write_emx(model = model, out_dir = "data/cosas")


#'//////////////////////////////////////

# convert mappings

mappingmodel <- yml_to_emx(path = "data/cosas-mappings/cosas-mappings.yml")
mappingmodel$packages <- mappingmodel$packages %>% dplyr::rename(id = name)
readr::write_tsv(
    x = mappingmodel$packages,
    file = "data/cosas-mappings/sys_md_Package.tsv"
)
readr::write_tsv(
    x = mappingmodel$attributes,
    file = "data/cosas-mappings/cosasmaps_attributes.tsv",
    na = ""
)
