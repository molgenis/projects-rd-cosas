#'////////////////////////////////////////////////////////////////////////////
#' FILE: mapping_cosasrefs.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-07-28
#' MODIFIED: 2021-07-28
#' PURPOSE: build datasets for reference entities
#' STATUS: in.progress
#' PACKAGES: *see below*
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

# pkgs
suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(magrittr))

# load data
source("R/mapping_cosasportal.R")

#'////////////////////////////////////////////////////////////////////////////

#' ~ 2 ~
#' Create `cosasrefs_*` datasets

# Create: `cosasrefs_diagnoses`
cosasrefs_diagnoses <- portal_diagnoses %>%
    select(diagnosis = HOOFDDIAGNOSE) %>%
    bind_rows(
        portal_diagnoses %>%
            select(diagnosis = EXTRA_DIAGNOSE)
    ) %>%
    distinct(diagnosis) %>%
    filter(!is.na(diagnosis), diagnosis != "-") %>%
    mutate(
        cineas_code = purrr::map_chr(
            diagnosis,
            function(x) {
                strsplit(x, ":") %>%
                    unlist(.) %>%
                    .[1] %>%
                    tolower(.)
            }
        ),
        cineas_description = purrr::map_chr(
            diagnosis,
            function(x) {
                strsplit(x, ":") %>%
                    unlist(.) %>%
                    .[2] %>%
                    trimws(.) %>%
                    tools::toTitleCase(.)
            }
        ),
        id = paste0("dx_", cineas_code)
    ) %>%
    select(id, cineas_code, cineas_description) %>%
    arrange(id)

# Create: `cosasrefs_diagnostic_certainty`
cosasrefs_diagnostic_certainty <- portal_diagnoses %>%
    select(certainty = HOOFDDIAGNOSE_ZEKERHEID) %>%
    bind_rows(
        portal_diagnoses %>%
            select(certainty = EXTRA_DIAGNOSE_ZEKERHEID)
    ) %>%
    distinct(certainty) %>%
    filter(!is.na(certainty), certainty != "-") %>%
    mutate(
        id = tolower(stringr::str_replace_all(certainty, " ", "-")),
        certainty = tools::toTitleCase(certainty)
    ) %>%
    select(id, certainty) %>%
    arrange(id)

# Create: `cosasrefs_condition_codes`
cosasrefs_condition_codes <- portal_samples %>%
    distinct(AANDOENING_CODE) %>%
    filter(!is.na(AANDOENING_CODE)) %>%
    mutate(
        id = tolower(AANDOENING_CODE),
        name = AANDOENING_CODE
    ) %>%
    select(id, name) %>%
    arrange(id)

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


#'//////////////////////////////////////

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

#'//////////////////////////////////////

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