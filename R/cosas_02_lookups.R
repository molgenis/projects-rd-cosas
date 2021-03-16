#'////////////////////////////////////////////////////////////////////////////
#' FILE: cosas_lookups.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-03-16
#' MODIFIED: 2021-03-16
#' PURPOSE: convert yml for lookup tables
#' STATUS: in.progress
#' PACKAGES: NA
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

#' pkgs
suppressPackageStartupMessages(library(dplyr))


#' utils
source("R/utils_yaml_convert.R")
source("R/utils_write_emx.R")

#' ~ 0 ~
#' remove existing files from `data/cosas`
invisible(
    sapply(
        list.files(
            path = "data/cosas-lookups",
            full.names = TRUE,
            pattern = "((cosasrefs_[a-zA-Z])|(sys_[a-zA-Z])\\.tsv)",
        ),
        file.remove
    )
)


#' ~ 1 ~
# convert yml to emx, and then write to file
model <- yml_to_emx(path = "data/cosas-lookups/cosas-lookups.yml")
model$packages <- model$packages %>% dplyr::rename(id = name)
write_emx(model = model, out_dir = "data/cosas-lookups")