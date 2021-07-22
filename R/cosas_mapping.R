#'////////////////////////////////////////////////////////////////////////////
#' FILE: cosas_mapping.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-07-22
#' MODIFIED: 2021-07-22
#' PURPOSE: Mapping portal tables to main pkg
#' STATUS: in.progress
#' PACKAGES: dplyr
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////


# pkgs
suppressPackageStartupMessages(library(dplyr))

#'//////////////////////////////////////

#' ~ 0 ~
#' Define functions


#' @name utils
#' @description various methods to assist with mapping
utils <- structure(list(), class = "cosas-utils")

#' @name utils$timestamp
#' @description Return timestamp in Molgenis datetime format
#' @return dateTime as string
utils$timestamp <- function() {
    return(format(Sys.time(), "%Y-%m-%dT%H:%M:%OS%z"))
}

#' @name utils$format__dx__code
#' @description given a diagnoses field, extract and format the dx code
#' @return a character
utils$format__dx__code <- function(x) {
    case_when(
        x != "-" ~ paste0(
            "dx_", stringr::str_split(x, ":", n = 2, simplify = TRUE)[[1]]
        ),
        TRUE ~ NA_character_
    )
}

#' @name utils$format__dx__certainty
#' @description given a certainty string, format for COSAS
#' @return a string
utils$format__dx__certainty <- function(x) {
    case_when(
        x != "-" ~ tolower(stringr::str_replace(x, " ", "-")),
        TRUE ~ NA_character_
    )
}

#' @name mappings
#' @descriptiion class for COSAS mappings
mappings <- structure(list(), class = "cosas-mappings")


#' @name mappings$patients
#' @description map patient portal data to COSAS terminology
#' @section Notes:
#' You will need to add the following columns from other datasets
#' - consanguinity (Tbd)
#' - is_fetus <= from categenia export
#' - is_twin <= from categenia export
#' - date_first_consult <= from diagnoses
#' @param data data from `cosasportal_patients`
#' @return tibble with data mapped to `cosas_patients`
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
            # format `dob`
            dob = format(dob, "%Y-%m-%d"),
            # clean `biological_sex`
            biological_sex = tolower(biological_sex),
            # clean `linked_family_ids`
            linked_family_ids = gsub(
                pattern = ", ",
                replacement = ",",
                x = linked_family_ids
            ),
            # set deceased status
            is_deceased = case_when(
                !is.na(date_deceased) &
                class(date_deceased)[1] == "POSIXct" ~ "ja",
                TRUE ~ "nee"
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
#' @return tibble containing data mapped to `cosas_diagnoses`
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
            "umcg_numr" = UmcgNr,
            "test_code" = TestId,
            "test_date" = TestDatum,
            "lab_indication" = Indicatie,
            "sequencer" = Sequencer,
            "prep_kit" = PrepKit,
            "sequencing_type" = `Sequencing Type`,
            "seqtype" = SeqType,
            "capturing_kit" = CapturingKit,
            "batch" = BatchNaam,
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

#'//////////////////////////////////////

#' ~ 1 ~
# load raw portal objects

portal_patients <- readxl::read_xlsx(
    path = "data/cosasportal/cosasportal_patients.xlsx",
    sheet = 1,
    col_types = c("text", "date", "text", "date", rep("text", 4)),
)

portal_diagnoses <- readxl::read_xlsx(
    path = "data/cosasportal/cosasportal_diagnoses.xlsx",
    sheet = 1,
    col_types = c(rep("text", 5), "date", "text")
)

portal_samples <- readxl::read_xlsx(
    path = "data/cosasportal/cosasportal_samples.xlsx",
    sheet = 1,
    col_types = "text"
)

portal_array_adlas <- readxl::read_xlsx(
    path = "data/cosasportal/cosasportal_array_adlas.xlsx",
    sheet = 1,
    col_types = c(rep("text", 29))
)

portal_array_darwin <- readxl::read_xlsx(
    path = "data/cosasportal/cosasportal_array_darwin.xlsx",
    sheet = 1,
    col_types = c(rep("text", 2), "date", rep("text", 4))
)

portal_ngs_adlas <- readxl::read_xlsx(
    path = "data/cosasportal/cosasportal_ngs_adlas.xlsx",
    sheet = 1,
    col_types = c(rep("text", 14))
)

portal_ngs_darwin <- readxl::read_xlsx(
    path = "data/cosasportal/cosasportal_ngs_darwin.xlsx",
    sheet = 1,
    col_types = c(rep("text", 2), "date", rep("text", 10))
)

portal_bench_cnv <- readxl::read_xlsx(
    path = "data/cosasportal/cosasportal_bench_cnv.xlsx",
    sheet = 1,
    col_types = c(rep("text", 6), "date")
)

#'//////////////////////////////////////

#' ~ 2 ~
#' Map Objects into COSAS Terminology

cosas_patients <- mappings$patients(portal_patients)
cosas_diagnoses <- mappings$diagnoses(portal_diagnoses)
cosas_samples <- mappings$samples(portal_samples)
cosas_array_adlas <- mappings$array_adlas(portal_array_adlas)
cosas_array_darwin <- mappings$array_darwin(portal_array_darwin)
cosas_ngs_adlas <- mappings$ngs_adlas(portal_ngs_adlas)
cosas_ngs_darwin <- mappings$ngs_darwin(portal_ngs_darwin)

# initial cosas_labs_array
cosas_labs_array <- cosas_array_adlas %>%
    left_join(
        cosas_array_darwin,
        by = c("umcg_numr", "test_code")
    ) %>%
    left_join(
        cosas_patients %>%
            distinct(umcg_numr, family_numr),
        by = "umcg_numr"
    )

# initial cosas_labs_ngs
cosas_labs_ngs <- cosas_ngs_adlas %>%
    left_join(
        cosas_ngs_darwin %>%
            distinct(umcg_numr, test_code, .keep_all = TRUE)
        ,
        by = c("umcg_numr", "test_code")
    )

#'//////////////////////////////////////

#' ~ 3 ~
#' Merge Data

# merge: earliest `date_first_consult` per patient into patients
cosas_patients <- cosas_patients %>%
    left_join(
        cosas_diagnoses %>%
            select(umcg_numr, date_first_consult) %>%
            filter(!is.na(date_first_consult)) %>%
            group_by(umcg_numr) %>%
            mutate(
                date_first_consult = lubridate::ymd(date_first_consult)
            ) %>%
            summarize(
                date_first_consult = min(date_first_consult, na.rm = TRUE)
            ),
        by = "umcg_numr"
    )


# merge: `family_numr` from patients into samples
# merge: `test_id`, `lab_indication`, `test_date` into samples
cosas_samples <- cosas_samples %>%
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
                    umcg_numr, request_id, dna_numr, test_id, test_code,
                    test_date, lab_indication
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
        )


#'//////////////////////////////////////


#' ~ 4 ~
#' Prep Data
#' arrange, add timestamps, etc


# finalize: `cosas_patients`

# finalize: `cosas_diagnoses`

# finalize: `cosas_samples`
cosas_samples %>%
    arrange(family_numr, umcg_numr, sample_id) %>%
    select(
        umcg_numr, family_numr, request_id, sample_id, dna_numr,
        material_type, lab_indication, test_id, test_code, test_date,
        test_result, test_result_status, disorder_code
    )

#...