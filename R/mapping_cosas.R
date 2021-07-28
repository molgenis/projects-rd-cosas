#' ////////////////////////////////////////////////////////////////////////////
#' FILE: cosas_mapping.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-07-22
#' MODIFIED: 2021-07-26
#' PURPOSE: Mapping portal tables to main pkg
#' STATUS: in.progress
#' PACKAGES: dplyr, tidyr, stringr, purrr
#' COMMENTS: NA
#' ////////////////////////////////////////////////////////////////////////////

# pkgs
suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(magrittr))

# data
source("R/mapping_cosasportal.R")

#' //////////////////////////////////////

#' ~ 0 ~
#' Define methods and mappings
cli::cli_alert_info("Initializing Methods...")

#' @name utils
#' @description various methods to assist with mapping
utils <- list(
    #' @name utils$timestamp
    #' @description Return timestamp in Molgenis datetime format
    #' @return dateTime as string
    timestamp = function() format(Sys.time(), "%Y-%m-%dT%H:%M:%OS%z"),
    #' @name utils$format__dx__code
    #' @description given a diagnoses field, extract and format the dx code
    #' @return a character
    format__dx__code = function(x) {
        case_when(
            x != "-" ~ paste0(
                "dx_", stringr::str_split(x, ":", n = 2, simplify = TRUE)[[1]]
            ),
            TRUE ~ NA_character_
        )
    },
    #' @name utils$format__dx__certainty
    #' @description given a certainty string, format for COSAS
    #' @return a string
    format__dx__certainty = function(x) {
        case_when(
            x != "-" ~ tolower(stringr::str_replace(x, " ", "-")),
            TRUE ~ NA_character_
        )
    }
)


#' @name mappings
#' @descriptiion class for COSAS mappings
mappings <- list(class = "cosas-mappings")


#' @name mappings$patients
#' @description map patient portal data to COSAS terminology
#' @section Notes:
#' You will need to add the following columns from other datasets
#' - consanguinity (Tbd)
#' - is_fetus <= from categenia export
#' - is_twin <= from categenia export
#' - date_first_consult <= from diagnoses
#' @param data data from `cosasportal_patients`
#' @return tibble with data mapped to `cosas_patients_mapped`
mappings$patients <- function(data) {
    data %>%
        select(
            umcg_numr = UMCG_nummer,
            family_numr = Familienummer,
            dob = Geboortedatum,
            biological_sex = Geslacht,
            maternal_id = UMCG_moeder,
            paternal_id = UMCG_vader,
            linked_family_ids = Familieleden,
            date_deceased = Overlijdensdatum
        ) %>%
        mutate(
            biological_sex = case_when(
                tolower(biological_sex) == "vrouw" ~ "female",
                tolower(biological_sex) == "man" ~ "male"
            ),
            linked_family_ids = gsub(", ", ",", linked_family_ids),
            is_deceased = case_when(
                !is.na(date_deceased) &
                    class(date_deceased)[1] == "POSIXct" ~ TRUE,
                TRUE ~ FALSE
            ),
            age_at_death = purrr::map2_chr(
                date_deceased, dob,
                function(date_deceased, dob) {
                    if (!is.na(date_deceased)) {
                        round((date_deceased - dob) / 365.25, 2)
                    } else {
                        NA_real_
                    }
                }
            ),
            dob = format(dob, "%Y-%m-%d"),
            date_deceased = purrr::map_chr(
                date_deceased,
                function(x) format(as.Date(x), "%Y-%m-%d")
            )
        )
}

#' @name mappings$diagnoses
#' @description map diagnoses portal data to COSAS terminology
#' @section Notes:
#' The date of consult will need to be mapped into the patients dataset.
#' After the initial mappings, calculate the earliest date per patient.
#' - Earliest Date First Consult => patients
#' @param data data from the portal table (`cosasportal_diagnoses`)
#' @return tibble containing data mapped to `cosas_diagnoses_mapped`
mappings$diagnoses <- function(data) {
    data %>%
        select(
            umcg_numr = UMCG_NUMBER,
            primary_dx = HOOFDDIAGNOSE,
            primary_dx_certainty = HOOFDDIAGNOSE_ZEKERHEID,
            extra_dx = EXTRA_DIAGNOSE,
            extra_dx_certainty = EXTRA_DIAGNOSE_ZEKERHEID,
            date_first_consult = DATUM_EERSTE_CONSULT,
            ond_id = OND_ID
        ) %>%
        mutate(
            primary_dx = purrr::map_chr(primary_dx, utils$format__dx__code),
            primary_dx_certainty = purrr::map_chr(
                primary_dx_certainty, utils$format__dx__certainty
            ),
            extra_dx = purrr::map_chr(extra_dx, utils$format__dx__code),
            extra_dx_certainty = purrr::map_chr(
                extra_dx_certainty, utils$format__dx__certainty
            ),
            date_first_consult = purrr::map_chr(
                date_first_consult,
                function(x) format(as.Date(x), "%Y-%m-%d")
            )
        )
}

#' @name mappings$samples
#' @description map samples portal table to COSAS terminology
#' @param data data from the portal table `cosasportal_samples`
#' @section Notes:
#' You will need to map the following variables from other datasets
#' - family number <= from patients
#' - lab indication <= from Darwin (array and ngs)
#' - test date <= from Darwin (array and ngs)
#' @return tibble
mappings$samples <- function(data) {
    data %>%
        select(
            umcg_numr = UMCG_NUMMER,
            request_id = ADVVRG_ID,
            sample_id = MONSTER_ID,
            dna_numr = DNA_NUMMER,
            material_type = MATERIAAL,
            test_code = TEST_CODE,
            test_result = UITSLAG_TEKST,
            test_result_status = UITSLAGCODE,
            disorder_code = AANDOENING_CODE
        ) %>%
        mutate(
            material_type = purrr::map_chr(
                material_type, function(x) tolower(gsub(" ", "-", x))
            ),
            test_code = purrr::map_chr(test_code, tolower),
            disorder_code = purrr::map_chr(disorder_code, tolower)
        )
}


#' @name mappings$array_adlas
#' @description map Adlas Array data into cosas_labs_array
#' @param data export from cosasportal_array_adlas
#' @return tibble
mappings$array_adlas <- function(data) {
    data %>%
        select(
            umcg_numr = UMCG_NUMBER,
            request_id = ADVVRG_ID,
            dna_numr = DNA_NUMMER,
            test_id = TEST_ID,
            test_code = TEST_CODE
        ) %>%
        mutate(test_code = purrr::map_chr(test_code, tolower)) %>%
        dplyr::distinct_all(.) # remove if more cols are added
}

#' @name mappings$array_darwin
#' @description map array data from darwin to cosas_labs_array
#' @param data export from cosasportal_array_darwin
#' @return tibble
mappings$array_darwin <- function(data) {
    data %>%
        select(
            umcg_numr = UmcgNr,
            test_code = TestId,
            test_date = TestDatum,
            lab_indication = Indicatie
        ) %>%
        mutate(
            test_code = purrr::map_chr(test_code, tolower),
            test_date = purrr::map_chr(
                test_date, function(x) format(as.Date(x), "%Y-%m-%d")
            ),
            lab_indication = purrr::map_chr(
                lab_indication, function(x) tolower(gsub(" ", "-", x))
            )
        ) %>%
        distinct_all(.) # remove if more cols are added
}

#' @name mappings$ngs_adlas
#' @description map ngs aldas data into cosas_labs_ngs
#' @param data export from cosasportal_ngs_adlas
#' @return tibble
mappings$ngs_adlas <- function(data) {
    data %>%
        select(
            umcg_numr = UMCG_NUMBER,
            request_id = ADVVRG_ID,
            dna_numr = DNA_NUMMER,
            test_id = TEST_ID,
            test_code = TEST_CODE
        ) %>%
        mutate(test_code = purrr::map_chr(test_code, tolower)) %>%
        distinct_all(.) # remove if more cols are added
}

#' @name mappings$ngs_darwin
#' @description map ngs darwin data into cosas_lab_ngs
#' @param data export from `cosasportal_ngs_darwin`
#' @return tibble
mappings$ngs_darwin <- function(data) {
    data %>%
        select(
            umcg_numr = UmcgNr,
            test_code = TestId,
            test_date = TestDatum,
            lab_indication = Indicatie,
            sequencer = Sequencer,
            prep_kit = PrepKit,
            sequencing_type = `Sequencing Type`,
            seqtype = SeqType,
            capturing_kit = CapturingKit,
            batch = BatchNaam,
            genome_build = GenomeBuild
        ) %>%
        mutate(
            test_code = purrr::map_chr(test_code, tolower),
            test_date = purrr::map_chr(
                test_date, function(x) format(as.Date(x), "%Y-%m-%d")
            ),
            lab_indication = purrr::map_chr(
                lab_indication, function(x) tolower(gsub(" ", "-", x))
            )
        ) %>%
        distinct_all(.) # remove if more cols are added
}

#' @title Map Bench CNV Export
#' @name mappings$bench_cnv
#' @description Map HPO and fetal status into patients
#' @param data output from `cosasportal_bench_cnv`
#' @return a tibble
mappings$bench_cnv <- function(data) {
    d <- data %>%
        select(
            umcg_numr = primid,
            family_numr = secid,
            biological_sex = gender,
            hpo = Phenotype,
            date_created = created
        ) %>%
        mutate(
            umcg_numr = purrr::map_chr(
                umcg_numr,
                function(x) {
                    y <- gsub("([_=])", "-", x)
                    gsub("((\\s+)|(\\(snp\\)))", "", y)
                }
            ),
            maternal_id = NA,
            is_fetus = NA,
            is_twin = NA,
            biological_sex = case_when(
                biological_sex == "F" ~ "female",
                biological_sex == "M" ~ "male",
                biological_sex == "U" ~ "unknown"
            ),
            # hpo = case_when(
            #     !is.na(hpo) ~ stringr::str_replace_all(hpo, "\\s+", ","),
            #     TRUE ~ NA_character_
            # ),
            hpo = purrr::map_chr(
                hpo, function(x) {
                    if (!is.na(x)) {
                        strsplit(x, "\\s+") %>%
                            unlist(.) %>%
                            unique(.) %>%
                            stringr::str_replace_all(., "HP:", "") %>%
                            paste0(., collapse = ",")
                    } else {
                        NA_character_
                    }
                }
            ),
            date_created = as.Date(date_created),
            linked_patient_id = NA
        )

    # pattern for twin detection
    p1 <- "^([0-9]{2,}F[0-9]{1}\\.[0-9]{1})$"
    # pattern for linked ID
    p2 <- "^([0-9]{2,}(F)?([0-9]{1,})?-[0-9]{2,})$"
    # process fetus metadata
    for (i in seq_len(NROW(d))) {
        if (grepl("F", d$umcg_numr[i])) {
            d$is_fetus[i] <- TRUE
            # extract maternal ID for pure fetus cases
            if (grepl("^([0-9]{2,}F)$", d$umcg_numr[i])) {
                d$maternal_id[i] <- gsub("F", "", d$umcg_numr[i])
            }
            # detect if patient is a twin
            if (grepl(p1, d$umcg_numr[i])) {
                str <- unlist(strsplit(d$umcg_numr[i], "F"))
                d$is_twin[i] <- TRUE
                d$maternal_id[i] <- gsub("F", "", str[1])
            } else {
                d$is_twin[i] <- FALSE
            }
            # process IDs that indicate fetus was born
            if (grepl(p2, d$umcg_numr[i])) {
                str <- unlist(strsplit(d$umcg_numr[i], "-"))
                d$umcg_numr[i] <- str[1]
                d$maternal_id[i] <- gsub("F", "", str[1])
                d$linked_patient_id[i] <- str[2]
            }
        } else {
            d$is_fetus[i] <- FALSE
            d$is_twin[i] <- FALSE
        }
    }
    return(d)
}

#'////////////////////////////////////////////////////////////////////////////


#' ~ 2 ~
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

#'////////////////////////////////////////////////////////////////////////////

#' ~ 3 ~
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