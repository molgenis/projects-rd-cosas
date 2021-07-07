#'////////////////////////////////////////////////////////////////////////////
#' FILE: cosas_emx.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-03-16
#' MODIFIED: 2021-07-07
#' PURPOSE: convert EMX yaml into CSVs
#' STATUS: working
#' PACKAGES: dplyr
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

#' pkgs
suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(magrittr))

#' utils
source("R/utils_yaml_convert.R")

# @name remove.files
# @description Remove all files in a given directory
# @param dir path to folder
remove.files <- function(dir) {
    invisible(sapply(list.files(dir, full.names = TRUE), file.remove))
}

#'//////////////////////////////////////

#' ~ 1 ~
#' Convert COSAS Portal

remove.files(dir = "emx/cosas-portal")

cosas_portal <- yml_to_emx(
    path = "emx/src/cosas-portal.yml",
    attr_entity_has_pkg = TRUE
)

# fix names
cosas_portal$attributes <- cosas_portal$attributes %>%
    dplyr::rename(
        `label-nl` = label.nl,
        `description-nl` = description.nl
    )

# cosas_portal$packages <- cosas_portal$packages %>%
#     dplyr::rename(id = name)
# # write file
# write_emx(
#     model = cosas_portal,
#     out_dir = "emx/cosas-portal"
# )

openxlsx::createWorkbook() %T>%
    openxlsx::addWorksheet(., "packages") %T>%
    openxlsx::addWorksheet(., "entities") %T>%
    openxlsx::addWorksheet(., "attributes") %T>%
    openxlsx::writeData(., "packages", cosas_portal$packages) %T>%
    openxlsx::writeData(., "entities", cosas_portal$entities) %T>%
    openxlsx::writeData(., "attributes", cosas_portal$attributes) %T>%
    openxlsx::saveWorkbook(
        wb = .,
        file = "emx/cosas-portal/cosasportal.xlsx",
        overwrite = TRUE
    )


#'//////////////////////////////////////

#' ~ 2 ~
#' Convert COSAS References

remove.files(dir = "emx/cosas-refs")

cosas_refs <- yml_to_emx(
    path = "emx/src/cosas-refs.yml",
    attr_entity_has_pkg = TRUE
)

cosas_refs$attributes <- cosas_refs$attributes %>%
    dplyr::rename(
        `label-nl` = label.nl,
        `description-nl` = description.nl
    )

openxlsx::createWorkbook() %T>%
    openxlsx::addWorksheet(., "packages") %T>%
    openxlsx::addWorksheet(., "entities") %T>%
    openxlsx::addWorksheet(., "attributes") %T>%
    openxlsx::addWorksheet(., "cosasrefs_diagnostic_certainty") %T>%
    openxlsx::addWorksheet(., "cosasrefs_lab_indications") %T>%
    openxlsx::addWorksheet(., "cosasrefs_phenotypic_sex") %T>%
    openxlsx::writeData(., "packages", cosas_refs$packages) %T>%
    openxlsx::writeData(., "entities", cosas_refs$entities) %T>%
    openxlsx::writeData(., "attributes", cosas_refs$attributes) %T>%
    openxlsx::writeData(
        wb = .,
        sheet = "cosasrefs_diagnostic_certainty",
        x = cosas_refs$cosasrefs_diagnostic_certainty
    ) %T>%
    openxlsx::writeData(
        wb = .,
        sheet = "cosasrefs_lab_indications",
        x = cosas_refs$cosasrefs_lab_indications
    ) %T>%
    openxlsx::writeData(
        wb = .,
        sheet = "cosasrefs_phenotypic_sex",
        x = cosas_refs$cosasrefs_phenotypic_sex
    ) %T>%
    openxlsx::saveWorkbook(
        wb = .,
        file = "emx/cosas-refs/cosasrefs.xlsx",
        overwrite = TRUE
    )


#'//////////////////////////////////////

#' ~ 3 ~
#' Convert COSAS package


remove.files(dir = "emx/cosas/")

cosas <- yml_to_emx(
    path = "emx/src/cosas.yml",
    attr_entity_has_pkg = TRUE
)


# fix names
cosas$attributes <- cosas$attributes %>%
    dplyr::rename(
        `label-nl` = label.nl,
        `description-nl` = description.nl
    )

openxlsx::createWorkbook() %T>%
    openxlsx::addWorksheet(., "packages") %T>%
    openxlsx::addWorksheet(., "entities") %T>%
    openxlsx::addWorksheet(., "attributes") %T>%
    openxlsx::writeData(., "packages", cosas$packages) %T>%
    openxlsx::writeData(., "entities", cosas$entities) %T>%
    openxlsx::writeData(., "attributes", cosas$attributes) %T>%
    openxlsx::saveWorkbook(
        wb = .,
        file = "emx/cosas/cosas.xlsx",
        overwrite = TRUE
    )

#'//////////////////////////////////////
