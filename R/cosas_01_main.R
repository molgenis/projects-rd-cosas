#'////////////////////////////////////////////////////////////////////////////
#' FILE: cosas_01_main.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-03-16
#' MODIFIED: 2021-03-16
#' PURPOSE: convert main yml into EMX
#' STATUS: working
#' PACKAGES: dplyr
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
            path = "data/cosas",
            full.names = TRUE,
            pattern = "((cosas_[a-zA-Z])|(sys_[a-zA-Z])\\.tsv)",
        ),
        file.remove
    )
)


#' ~ 1 ~
#' convert and write
model <- yml_to_emx(path = "data/cosas/cosas-prototype.yml")
model$attributes <- model$attributes %>% dplyr::rename(`label-nl` = label.nl)
model$packages <- model$packages %>% dplyr::rename(id = name)
write_emx(model = model, out_dir = "data/cosas")
