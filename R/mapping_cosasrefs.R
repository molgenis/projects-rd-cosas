#' ////////////////////////////////////////////////////////////////////////////
#' FILE: mapping_cosasrefs.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-07-28
#' MODIFIED: 2021-07-28
#' PURPOSE: build datasets for reference entities
#' STATUS: in.progress
#' PACKAGES: *see below*
#' COMMENTS: NA
#' ////////////////////////////////////////////////////////////////////////////


library2("data.table")
source("R/_load.R")


#' @title Generate Data for Diagnostic Reference Entity
#' @description  Create reference entity `cosasrefs_diagnoses`
#' @section Methodology:
#'
#' Using the portal table `cosasrefs_diagnoses`, we need to genereate a list
#' of distinct diganostic codes and definitions. Diagnoses are split into
#' two columns: HOOFDDIAGNOSE and EXTRA_DIAGNOSE. The following code will do
#' the following.
#'
#' 1) bind HOOFDDIAGNOSE and EXTRA_DIAGNOSE
#' 2) remove missing values (i.e., "-")
#' 3) separate diagnostic code and description
#' 4) create new diagnostic ID using diagnostic code
#'
#' @noRd
cosasrefs_diagnoses <- data.table::rbindlist(
        list(
            portal_diagnoses[, .(diagnosis = HOOFDDIAGNOSE)],
            portal_diagnoses[, .(diagnosis = EXTRA_DIAGNOSE)]
        )
    )[
        diagnosis != "-" & !duplicated(diagnosis)
    ][
        ,
        `:=`(
            cineasCode = purrr::map_chr(diagnosis, function(x) {
                val <- unlist(strsplit(x, ":"))[1]
                trimws(tolower(val), which = "both")
            }),
            cineasDescription = purrr::map_chr(diagnosis, function(x) {
                val <- unlist(strsplit(x, ":"))[2]
                trimws(val, which = "both")
            })
        )
    ][
        ,
        id := paste0("dx_", cineasCode)
    ][
        order(as.integer(cineasCode)),
        .(id, cineasCode, cineasDescription)
    ]


#' @title COSAS Diagnostic Certainty Reference Entity
#' @describe make `cosasrefs_diagnosticCertainty`
#' @section Methodology:
#'
#' The diagnosticCertainty reference entity is created in the EMX file rather
#' than here for a few reasons: 1) there aren't many options (3), 2) manually
#' defining the categories enables us to map to FairGenomes. The values from
#' ADLAS are cleaned slightly (see utils$recode_dx_certainty in the file
#' `R/utils_mapping.R`). There is the option to recode the values, but it
#' was decided to leave the original values and repeat the "provisional"
#' row for all potential variations. This can be added later if needed.
#'
#' The following code block can be used to determine if there are any new
#' cases, but the data won't be rewritten. Values should be:
#'
#' - Niet Zeker
#' - Zeker
#' - Onzeker
#' - Zeker niet
#'
#' @noRd

# data.table::rbindlist(
#     list(
#         portal_diagnoses[, .(certainty = HOOFDDIAGNOSE_ZEKERHEID)],
#         portal_diagnoses[, .(certainty = EXTRA_DIAGNOSE_ZEKERHEID)]
#     )
# )[
#     certainty != "-" & !duplicated(certainty)
# ]


#' @title COSAS Material Types Reference Entity
#' @description create `cosasrefs_materialTypes`
#' @section Methodology:
#'
#' Material Types are located in the `portal_samples` dataset. The material
#' types (or biospecimen types) are ...
#'
#' Use the following code to identify

data.table::setDT(portal_samples)

portal_samples[
    ,
    .(material = tolower(MATERIAAL))
][!duplicated(material)][order(material)]

# tibble::tribble(
#     ~ "nl", ~"en",
#     "beenmerg", "bone marrow",
#     "bloed", "blood",
#     "dna", "dna",
#     "dna reeds aanwezig", "dna already present",
#     "fibroblastenkweek", "fibroblast culture",
#     "foetus", "fetus",
#     "gekweekt foetaal weefsel", "cultured fetal tissue",
#     "gekweekt weefsel", "cultured tissue",
#     "gekweekte amnion cellen", "cultured amniotic cells",
#     "gekweekte chorion villi", "cultured chorionic villi",
#     "huidbiopt", "skin biopsy",
#     "navelstrengbloed", "Umbilical cord blood",
#     "ongekweekt foetaal weefsel", "uncultured fetal tissue",
#     "ongekweekt weefsel", "uncultured tissue",
#     "ongekweekte amnion cellen", "uncultured amniotic cells",
#     "ongekweekte chorion villi", "uncultured chorionic villi",
#     "overig", "other",
#     "paraffine normaal", "kerosene normal",
#     "paraffine tumor", "kerosene tumor",
#     "plasmacellen", "plasma cells",
#     "speeksel", "saliva",
#     "suspensie", "suspension",
#     "toegestuurd dna foetaal", "sent dna fetal"
# ) %>%
#     readr::write_csv(., "~/Desktop/materialTypes.csv")




# Create: `cosasrefs_material_types`
cosasrefs_material_types <- portal_samples %>%
    distinct(MATERIAAL) %>%
    filter(!is.na(MATERIAAL)) %>%
    mutate(
        id = tolower(stringr::str_replace_all(MATERIAAL, " ", "-")),
        material = tools::toTitleCase(MATERIAAL)
    ) %>%
    select(id, material) %>%
    distinct(id, .keep_all = TRUE) %>%
    arrange(id)


#' //////////////////////////////////////

# Create: `cosasrefs_test_codes` (add geneticlines mappings)
gl <- readxl::read_xlsx(
    path = "_raw/geneticlines2021-03-10_15_52_37.366.xlsx",
    sheet = "geneticlines_ADLAStest"
)

# compile genes
genes <- readxl::excel_sheets("_raw/testcodes_ngs_array.xlsx") %>%
    .[. != "Actieve Testcodes"] %>%
    purrr::map(., function(name) {
        cli::cli_alert_info("Processing sheet {.val {name}}")
        readxl::read_excel(
            path = "_raw/testcodes_ngs_array.xlsx",
            sheet = name,
            col_names = "genes"
        ) %>%
            pull(genes) %>%
            unique(.) %>%
            paste0(., collapse = ",") %>%
            as_tibble(.) %>%
            mutate(id = name) %>%
            select(id, genes = value)
    }) %>%
    bind_rows()

# build dataset
cosasrefs_test_codes <- portal_samples %>%
    select(TEST_CODE) %>%
    bind_rows(
        gl %>% select(TEST_CODE),
        portal_array_adlas %>% select(TEST_CODE),
        portal_ngs_adlas %>% select(TEST_CODE),
        portal_array_darwin %>% select(TestId),
        portal_ngs_darwin %>% select(TestId),
    ) %>%
    distinct(TEST_CODE) %>%
    filter(!is.na(TEST_CODE)) %>%
    arrange(TEST_CODE) %>%
    left_join(
        portal_samples %>%
            select(TEST_CODE, TEST_OMS) %>%
            distinct(TEST_CODE, .keep_all = TRUE),
        by = "TEST_CODE"
    ) %>%
    left_join(
        gl %>%
            select(-labelPanel) %>%
            mutate(
                panel = na_if(panel, "-")
            ),
        by = "TEST_CODE"
    ) %>%
    mutate(
        id = tolower(TEST_CODE),
        TEST_OMS = purrr::map2_chr(
            TEST_OMS.x, TEST_OMS.y,
            function(x, y) {
                if (is.na(x) & !is.na(y)) {
                    y
                } else if (!is.na(x) & is.na(y)) {
                    x
                } else if (!is.na(x) & !is.na(y)) {
                    x
                } else if (is.na(x) & is.na(y)) {
                    NA_character_
                }
            }
        )
    ) %>%
    select(id, code = TEST_CODE, description = TEST_OMS, label, panel)


# bind genes to `cosasrefs_test_codes`
cosasrefs_test_codes <- cosasrefs_test_codes %>%
    left_join(
        genes %>%
            filter(id %in% cosasrefs_test_codes$code),
        by = c("code" = "id")
    )

# create: `cosasrefs_genes`
cosasrefs_genes <- genes %>%
    select(genes) %>%
    pull(genes) %>%
    paste0(., collapse = ",") %>%
    strsplit(x = ., split = ",") %>%
    `[[`(1) %>%
    as_tibble() %>%
    rename(gene = 1) %>%
    distinct()

#' //////////////////////////////////////

# Create: `cosasrefs_lab_indications`
cosasrefs_lab_indications <- portal_array_darwin %>%
    select(indication = Indicatie) %>%
    bind_rows(
        portal_ngs_darwin %>%
            select(indication = Indicatie)
    ) %>%
    distinct(indication) %>%
    filter(!is.na(indication)) %>%
    mutate(
        id = tolower(stringr::str_replace_all(indication, " ", "-"))
    ) %>%
    select(id, indication) %>%
    arrange(id)


# write cosasrefs
openxlsx::createWorkbook() %T>%
    openxlsx::addWorksheet(., "cosasrefs_diagnoses") %T>%
    openxlsx::addWorksheet(., "cosasrefs_diagnostic_certainty") %T>%
    openxlsx::addWorksheet(., "cosasrefs_condition_codes") %T>%
    openxlsx::addWorksheet(., "cosasrefs_material_types") %T>%
    openxlsx::addWorksheet(., "cosasrefs_test_codes") %T>%
    openxlsx::addWorksheet(., "cosasrefs_test_genes") %T>%
    openxlsx::addWorksheet(., "cosasrefs_lab_indications") %T>%
    openxlsx::writeData(., "cosasrefs_diagnoses", cosasrefs_diagnoses) %T>%
    openxlsx::writeData(
        .,
        "cosasrefs_diagnostic_certainty",
        cosasrefs_diagnostic_certainty
    ) %T>%
    openxlsx::writeData(., "cosasrefs_condition_codes", cosasrefs_condition_codes) %T>%
    openxlsx::writeData(., "cosasrefs_material_types", cosasrefs_material_types) %T>%
    openxlsx::writeData(., "cosasrefs_test_codes", cosasrefs_test_codes) %T>%
    openxlsx::writeData(., "cosasrefs_test_genes", cosasrefs_genes) %T>%
    openxlsx::writeData(., "cosasrefs_lab_indications", cosasrefs_lab_indications) %T>%
    openxlsx::saveWorkbook(., "data/cosasrefs/cosasrefs.xlsx", TRUE)