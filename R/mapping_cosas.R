#' ////////////////////////////////////////////////////////////////////////////
#' FILE: cosas_mapping.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-07-22
#' MODIFIED: 2021-07-29
#' PURPOSE: Mapping portal tables to main pkg
#' STATUS: working
#' PACKAGES: dplyr, tidyr, stringr, purrr
#' COMMENTS: NA
#' ////////////////////////////////////////////////////////////////////////////

# pkgs
library2("dplyr")
library2("magrittr")

source("R/_load.R")
source("R/utils_mapping.R")


#' Map Objects into COSAS Terminology

cli::cli_alert_info("Mapping portal data objects into COSAS terminology")
cosas_patients_mapped <- mappings$patients(portal_patients)
cosas_diagnoses_mapped <- mappings$diagnoses(portal_diagnoses)
cosas_samples_mapped <- mappings$samples(portal_samples)
cosas_array_adlas_mapped <- mappings$array_adlas(portal_array_adlas)
cosas_array_darwin_mapped <- mappings$array_darwin(portal_array_darwin)
cosas_ngs_adlas_mapped <- mappings$ngs_adlas(portal_ngs_adlas)
cosas_ngs_darwin_mapped <- mappings$ngs_darwin(portal_ngs_darwin)
cosas_bench_cnv_mapped <- mappings$bench_cnv(portal_bench_cnv)

#'//////////////////////////////////////


#' Clean datasets

# prepare bench_cnv dataset
# pull cases that exist in the main patients tables, and then split by
# fetus status. This is important as fetus records will be binded to
# `cosas_patients` as new rows. Both fetus and non-fetus cases will be added
# to `cosas_clinical`.
cli::cli_alert_info("Filtering {.val benchCNV} and calcuating earliest date")
cosas_fetuses <- cosas_bench_cnv_mapped %>%
    filter(family_numr %in% cosas_patients_mapped$family_numr, is_fetus) %>%
    # this will get rid of the IDs with multiple HPO entries
    # this information will be added later in the clinical table
    distinct(
        umcg_numr, family_numr, biological_sex, maternal_id,
        is_fetus, is_twin, linked_patient_id
    ) %>%
    # calculate and join earliest date seen
    left_join(
        cosas_bench_cnv_mapped %>%
            select(umcg_numr, date_created) %>%
            filter(!is.na(date_created)) %>%
            group_by(umcg_numr) %>%
            mutate(
                date_first_consult = lubridate::ymd(date_created)
            ) %>%
            summarize(
                date_first_consult = min(date_first_consult, na.rm = TRUE)
            ),
        by = "umcg_numr"
    ) %>%
    distinct(umcg_numr, .keep_all = TRUE) # remove duplicate entries

# bind fetus cases to main patients
cli::cli_alert_info("Combining patients and fetus data...")
cosas_patients_fetuses <- cosas_patients_mapped %>%
    bind_rows(cosas_fetuses) %>%
    arrange(umcg_numr)

# code to check for multiple entries per fetus
# cosas_bench_cnv_mapped %>%
#     filter(
#         family_numr %in% cosas_patients_mapped$family_numr,
#         is_fetus
#     ) %>%
#     group_by(umcg_numr) %>%
#     summarize(
#         count = length(umcg_numr)
#     ) %>%
#     arrange(-count)

#' //////////////////////////////////////

#' ~ 4 ~
#' Merge Data

cosas_samples_mapped %>%
    select(umcg_numr, request_id, sample_id, dna_numr, material_type, test_code) %>%
    left_join(
        cosas_array_adlas_mapped,
        by = c("umcg_numr", "request_id", "dna_numr", "test_code")
    )


cosas_array_adlas_mapped %>%
    # merge samples metadata
    left_join(
        cosas_samples_mapped %>%
            select(
                umcg_numr, request_id, sample_id,
                dna_numr, material_type, test_code
            ),
        by = c("umcg_numr", "request_id", "dna_numr", "test_code")
    ) %>%
    # merge array data from darwin
    left_join(
        cosas_array_darwin_mapped,
        by = c("umcg_numr", "test_code")
    ) %>%
    # merge patient metadata
    left_join(
        cosas_patients_fetuses %>%
            select(umcg_numr, family_numr),
        by = "umcg_numr"
    ) %>%
    mutate(date_last_updated = utils$timestamp()) %>%
    select(umcg_numr, family_numr, everything()) %>%
    arrange(umcg_numr)


# create: `cosas_labs_array`
cli::cli_alert_info("Building Labs Array...")
cosas_labs_array <- cosas_array_adlas_mapped %>%
    left_join(
        cosas_array_darwin_mapped,
        by = c("umcg_numr", "test_code")
    ) %>%
    left_join(
        cosas_patients_fetuses %>%
            select(umcg_numr, family_numr) %>%
            distinct(umcg_numr, family_numr, .keep_all = TRUE),
        by = "umcg_numr"
    ) %>%
     mutate(
        date_last_updated = utils$timestamp()
    ) %>%
    select(umcg_numr, family_numr, everything()) %>%
    arrange(umcg_numr)

# create: `cosas_labs_ngs`
cosas_labs_ngs <- cosas_ngs_adlas_mapped %>%
    left_join(
        cosas_ngs_darwin_mapped %>%
            distinct(umcg_numr, test_code, .keep_all = TRUE),
        by = c("umcg_numr", "test_code")
    ) %>%
    left_join(
        cosas_patients_fetuses %>%
            select(umcg_numr, family_numr) %>%
            distinct(umcg_numr, family_numr, .keep_all = TRUE),
        by = "umcg_numr"
    ) %>%
    mutate(
        date_last_updated = utils$timestamp()
    ) %>%
    select(umcg_numr, family_numr, everything()) %>%
    arrange(umcg_numr)


# merge: earliest `date_first_consult` per patient into patients
cli::cli_alert_info("Building cosas_patients...")
cosas_patients <- cosas_patients_fetuses %>%
    left_join(
        cosas_diagnoses_mapped %>%
            select(umcg_numr, date_first_consult) %>%
            filter(
                !is.na(date_first_consult),
                umcg_numr %in% cosas_patients_fetuses$umcg_numr
            ) %>%
            group_by(umcg_numr) %>%
            mutate(
                date_first_consult = lubridate::ymd(date_first_consult)
            ) %>%
            summarize(
                date_first_consult = min(date_first_consult, na.rm = TRUE)
            ),
        by = "umcg_numr"
    ) %>%
    tidyr::unite(
        data = .,
        col = "date_first_consult",
        c("date_first_consult.x", "date_first_consult.y"),
        na.rm = TRUE
    ) %>%
    mutate(
        date_first_consult = na_if(date_first_consult, ""),
        date_last_updated = utils$timestamp()
    )


# merge: `family_numr` from patients into samples
# merge: `test_id`, `lab_indication`, `test_date` from labs_* into samples
cli::cli_alert_info("Building cosas_samples...")
cosas_samples <- cosas_samples_mapped %>%
    left_join(
        cosas_patients %>%
            distinct(umcg_numr, family_numr),
        by = "umcg_numr"
    ) %>%
    left_join(
        cosas_labs_array %>%
            select(-family_numr),
        by = c("umcg_numr", "request_id", "dna_numr", "test_code")
    ) %>%
    left_join(
        cosas_labs_ngs %>%
            select(
                umcg_numr, request_id, dna_numr,
                test_id, test_code, test_date,
                lab_indication
            ),
        by = c("umcg_numr", "request_id", "dna_numr", "test_code")
    ) %>%
    tidyr::unite(
        "lab_indication",
        c("lab_indication.x", "lab_indication.y"),
        na.rm = TRUE
    ) %>%
    tidyr::unite("test_id", c("test_id.x", "test_id.y"), na.rm = TRUE) %>%
    tidyr::unite("test_date", c("test_date.x", "test_date.y"), na.rm = TRUE) %>%
    mutate(
        lab_indication = na_if(lab_indication, ""),
        test_id = na_if(test_id, ""),
        test_date = na_if(test_date, ""),
        date_last_updated = utils$timestamp()
    ) %>%
    arrange(umcg_numr, sample_id)

# create: `cosas_clinical`
cli::cli_alert_info("Building cosas_clinical...")
cosas_clinical <- cosas_diagnoses_mapped %>%
    rename(date = date_first_consult) %>%
    mutate(
        keep = case_when(
            is.na(primary_dx) &
            is.na(primary_dx_certainty) &
            is.na(extra_dx) &
            is.na(extra_dx_certainty) &
            is.na(date) &
            is.na(ond_id) ~ FALSE,
            TRUE ~ TRUE
        )
    ) %>%
    filter(keep) %>%
    select(-keep) %>%
    mutate(
        event_type = case_when(
            is.na(primary_dx) & is.na(extra_dx) & !is.na(ond_id) ~ "OND",
            !is.na(primary_dx) ~ "DX",
            TRUE ~ NA_character_
        )
    ) %>%
    arrange(umcg_numr) %>%
    bind_rows(
        cosas_bench_cnv_mapped %>%
            select(umcg_numr, hpo, date = date_created) %>%
            filter(umcg_numr %in% cosas_patients$umcg_numr) %>%
            mutate(
                date = as.character(date),
                event_type = "HPO"
            )
    ) %>%
    left_join(
        cosas_patients_fetuses %>%
            select(umcg_numr, family_numr) %>%
            filter(umcg_numr %in% cosas_diagnoses_mapped$umcg_numr),
        by = "umcg_numr"
    ) %>%
    select(
        umcg_numr,
        family_numr,
        date,
        event_type,
        primary_dx,
        primary_dx_certainty,
        extra_dx,
        extra_dx_certainty,
        hpo,
        ond_id
    ) %>%
    arrange(umcg_numr) %>%
    mutate(
        date_last_updated = utils$timestamp()
    )

# write files
cli::cli_alert_info("Saving data to file...")
openxlsx::createWorkbook() %T>%
    openxlsx::addWorksheet(., "cosas_patients") %T>%
    openxlsx::addWorksheet(., "cosas_clinical") %T>%
    openxlsx::addWorksheet(., "cosas_samples") %T>%
    openxlsx::addWorksheet(., "cosas_labs_array") %T>%
    openxlsx::addWorksheet(., "cosas_labs_ngs") %T>%
    openxlsx::writeData(., "cosas_patients", cosas_patients) %T>%
    openxlsx::writeData(., "cosas_clinical", cosas_clinical) %T>%
    openxlsx::writeData(., "cosas_samples", cosas_samples) %T>%
    openxlsx::writeData(., "cosas_labs_array", cosas_labs_array) %T>%
    openxlsx::writeData(., "cosas_labs_ngs", cosas_labs_ngs) %T>%
    openxlsx::saveWorkbook(., "data/cosas/cosas.xlsx", TRUE)


cli::cli_alert_success("Complete! :-)")