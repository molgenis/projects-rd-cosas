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

args <- commandArgs(trailingOnly = TRUE)

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
    timestamp = function() {
        return(format(Sys.time(), "%Y-%m-%dT%H:%M:%OS%z"))
    },
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
            "umcg_numr" = UMCG_nummer,
            "family_numr" = Familienummer,
            "dob" = Geboortedatum,
            "biological_sex" = Geslacht,
            "maternal_id" = UMCG_moeder,
            "paternal_id" = UMCG_vader,
            "linked_family_ids" = Familieleden,
            "date_deceased" = Overlijdensdatum
        ) %>%
        mutate(
            biological_sex = case_when(
                tolower(biological_sex) == "vrouw" ~ "female",
                tolower(biological_sex) == "man" ~ "male"
            ),
            linked_family_ids = gsub(", ", ",", linked_family_ids),
            is_deceased = case_when(
                !is.na(date_deceased) &
                    class(date_deceased)[1] == "POSIXct" ~ "Y",
                TRUE ~ "N"
            ),
            age_at_death = as.numeric(purrr::map2_chr(
                date_deceased, dob,
                function(date_deceased, dob) {
                    if (!is.na(date_deceased)) {
                        (date_deceased - dob) / 365.25
                    } else {
                        NA
                    }
                }
            )),
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
            "umcg_numr" = UMCG_NUMBER,
            "primary_dx" = HOOFDDIAGNOSE,
            "primary_dx_certainty" = HOOFDDIAGNOSE_ZEKERHEID,
            "extra_dx" = EXTRA_DIAGNOSE,
            "extra_dx_certainty" = EXTRA_DIAGNOSE_ZEKERHEID,
            "date_first_consult" = DATUM_EERSTE_CONSULT,
            "ond_id" = OND_ID
        ) %>%
        mutate(
            primary_dx = purrr::map_chr(
                primary_dx,
                utils$format__dx__code
            ),
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
            "umcg_numr" = UMCG_NUMMER,
            "request_id" = ADVVRG_ID,
            "sample_id" = MONSTER_ID,
            "dna_numr" = DNA_NUMMER,
            "material_type" = MATERIAAL,
            "test_code" = TEST_CODE,
            "test_result" = UITSLAG_TEKST,
            "test_result_status" = UITSLAGCODE,
            "disorder_code" = AANDOENING_CODE
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
            "umcg_numr" = UMCG_NUMBER,
            "request_id" = ADVVRG_ID,
            "dna_numr" = DNA_NUMMER,
            "test_id" = TEST_ID,
            "test_code" = TEST_CODE
        ) %>%
        mutate(
            test_code = purrr::map_chr(test_code, tolower)
        ) %>%
        # this will need to be remove if more cols are added
        dplyr::distinct_all(.)
}

#' @name mappings$array_darwin
#' @description map array data from darwin to cosas_labs_array
#' @param data export from cosasportal_array_darwin
#' @return tibble
mappings$array_darwin <- function(data) {
    data %>%
        select(
            "umcg_numr" = UmcgNr,
            "test_code" = TestId,
            "test_date" = TestDatum,
            "lab_indication" = Indicatie
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
        # this should be removed if more columns are added
        distinct_all()
}

#' @name mappings$ngs_adlas
#' @description map ngs aldas data into cosas_labs_ngs
#' @param data export from cosasportal_ngs_adlas
#' @return tibble
mappings$ngs_adlas <- function(data) {
    data %>%
        select(
            "umcg_numr" = UMCG_NUMBER,
            "request_id" = ADVVRG_ID,
            "dna_numr" = DNA_NUMMER,
            "test_id" = TEST_ID,
            "test_code" = TEST_CODE
        ) %>%
        mutate(
            test_code = purrr::map_chr(test_code, tolower)
        ) %>%
        # this should be removed if more columns are added
        distinct_all()
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
        # this should be removed if more columns are added
        distinct_all()
}

#' @title Map Bench CNV Export
#' @name mappings$bench_cnv
#' @description Map HPO and fetal status into patients
#' @param data output from `cosasportal_bench_cnv`
#' @return a tibble
mappings$bench_cnv <- function(data) {
    d <- data %>%
        select(
            "umcg_numr" = primid,
            "family_numr" = secid,
            "biological_sex" = gender,
            "hpo" = Phenotype,
            "date_created" = created
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
            hpo = case_when(
                !is.na(hpo) ~ stringr::str_replace_all(hpo, "\\s+", ","),
                TRUE ~ NA_character_
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

#' ~ 1 ~
# load raw portal objects
cli::cli_alert_info("Reading portal datasets")

portal_patients <- readxl::read_xlsx(
    path = "_raw/cosasportal_patients.xlsx",
    sheet = 1,
    col_types = c("text", "date", "text", "date", rep("text", 4)),
)

portal_diagnoses <- readxl::read_xlsx(
    path = "_raw/cosasportal_diagnoses.xlsx",
    sheet = 1,
    col_types = c(rep("text", 5), "date", "text")
)

portal_samples <- readxl::read_xlsx(
    path = "_raw/cosasportal_samples.xlsx",
    sheet = 1,
    col_types = "text"
)

portal_array_adlas <- readxl::read_xlsx(
    path = "_raw/cosasportal_array_adlas.xlsx",
    sheet = 1,
    col_types = c(rep("text", 29))
)

portal_array_darwin <- readxl::read_xlsx(
    path = "_raw/cosasportal_array_darwin.xlsx",
    sheet = 1,
    col_types = c(rep("text", 2), "date", rep("text", 4))
)

portal_ngs_adlas <- readxl::read_xlsx(
    path = "_raw/cosasportal_ngs_adlas.xlsx",
    sheet = 1,
    col_types = c(rep("text", 14))
)

portal_ngs_darwin <- readxl::read_xlsx(
    path = "_raw/cosasportal_ngs_darwin.xlsx",
    sheet = 1,
    col_types = c(rep("text", 2), "date", rep("text", 10))
)

portal_bench_cnv <- readxl::read_xlsx(
    path = "_raw/cosasportal_bench_cnv.xlsx",
    sheet = 1,
    col_types = c(rep("text", 6), "date")
)

# write cosasportal
cli::cli_alert_info("Writing portal data to file...")
openxlsx::createWorkbook() %T>%
    openxlsx::addWorksheet(., "cosasportal_labs_array_adlas") %T>%
    openxlsx::addWorksheet(., "cosasportal_labs_array_darwin") %T>%
    openxlsx::addWorksheet(., "cosasportal_bench_cnv") %T>%
    openxlsx::addWorksheet(., "cosasportal_diagnoses") %T>%
    openxlsx::addWorksheet(., "cosasportal_labs_ngs_adlas") %T>%
    openxlsx::addWorksheet(., "cosasportal_labs_ngs_darwin") %T>%
    openxlsx::addWorksheet(., "cosasportal_patients") %T>%
    openxlsx::addWorksheet(., "cosasportal_samples") %T>%
    openxlsx::writeData(
        ., "cosasportal_labs_array_adlas", portal_array_adlas
    ) %T>%
    openxlsx::writeData(
        ., "cosasportal_labs_array_darwin", portal_array_darwin
    ) %T>%
    openxlsx::writeData(., "cosasportal_bench_cnv", portal_bench_cnv) %T>%
    openxlsx::writeData(., "cosasportal_diagnoses", portal_diagnoses) %T>%
    openxlsx::writeData(., "cosasportal_labs_ngs_adlas", portal_ngs_adlas) %T>%
    openxlsx::writeData(., "cosasportal_labs_ngs_darwin", portal_ngs_darwin) %T>%
    openxlsx::writeData(., "cosasportal_patients", portal_patients) %T>%
    openxlsx::writeData(., "cosasportal_samples", portal_samples) %T>%
    openxlsx::saveWorkbook(., "data/cosasportal/cosasportal.xlsx", TRUE)

#'////////////////////////////////////////////////////////////////////////////


#' ~ 2 ~
#' Map Objects into COSAS Terminology

cli::cli_alert_info("Mapping portal data objects")
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
#' Create `cosasrefs_*` datasets


cosasrefs <- structure(list(), class = "cosasrefs")

# Create: `cosasrefs_diagnoses`
cosasrefs$diagnoses <- portal_diagnoses %>%
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
cosasrefs$diagnostic_certainty <- portal_diagnoses %>%
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
cosasrefs$condition_codes <- portal_samples %>%
    distinct(AANDOENING_CODE) %>%
    filter(!is.na(AANDOENING_CODE)) %>%
    mutate(
        id = tolower(AANDOENING_CODE),
        name = AANDOENING_CODE
    ) %>%
    select(id, name) %>%
    arrange(id)

# Create: `cosasrefs_material_types`
cosasrefs$material_types <- portal_samples %>%
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
cosasrefs$test_codes <- portal_samples %>%
    select(TEST_CODE) %>%
    bind_rows(
        gl %>%
            select(TEST_CODE)
    ) %>%
    distinct(TEST_CODE) %>%
    arrange(TEST_CODE) %>%
    left_join(
        portal_samples %>%
            select(TEST_CODE, TEST_OMS) %>%
            distinct(TEST_CODE, .keep_all = TRUE),
        by = "TEST_CODE"
    ) %>%
    left_join(
        gl %>%
            select(-labelPanel),
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
                } else {
                    paste0("999_", x, ";", y)
                }
            }
        )
    ) %>%
    select(id, code = TEST_CODE, description = TEST_OMS, label, panel)


# bind genes to `cosasrefs_test_codes`
cosasrefs$test_codes <- cosasrefs$test_codes %>%
    left_join(
        genes %>%
            filter(id %in% cosasrefs$test_codes$code),
        by = c("code" = "id")
    )

# create: `cosasrefs_genes`
cosasrefs$genes <- genes %>%
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
cosasrefs$lab_indications <- portal_array_darwin %>%
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
    openxlsx::writeData(., "cosasrefs_diagnoses", cosasrefs$diagnoses) %T>%
    openxlsx::writeData(
        .,
        "cosasrefs_diagnostic_certainty",
        cosasrefs$diagnostic_certainty
    ) %T>%
    openxlsx::writeData(., "cosasrefs_condition_codes", cosasrefs$condition_codes) %T>%
    openxlsx::writeData(., "cosasrefs_material_types", cosasrefs$material_types) %T>%
    openxlsx::writeData(., "cosasrefs_test_codes", cosasrefs$test_codes) %T>%
    openxlsx::writeData(., "cosasrefs_test_genes", cosasrefs$genes) %T>%
    openxlsx::writeData(., "cosasrefs_lab_indications", cosasrefs$lab_indications) %T>%
    openxlsx::saveWorkbook(., "data/cosasrefs/cosasrefs.xlsx", TRUE)

#'////////////////////////////////////////////////////////////////////////////

#' ~ 4 ~
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
    )

# bind fetus cases to main patients
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

#' ~ 5 ~
#' Merge Data

# create: `cosas_labs_array`
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
