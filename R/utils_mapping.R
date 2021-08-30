#'////////////////////////////////////////////////////////////////////////////
#' FILE: utils_mapping.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-08-16
#' MODIFIED: 2021-08-20
#' PURPOSE: methods for `mapping_cosas.R`
#' STATUS: working
#' PACKAGES: data.table, purrr, dplyr
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////


#' ~ 1 ~
#' Generic Methods

#' @name utils
#' @description various methods to assist with mapping
utils <- list()

#' @name utils$as_string_id
#' @description convert a string to an ID string (lowercase, spaces recoded to dashes)
#' @param x a string to convert to an ID
#' @describeIn utils
#' @return string
utils$as_string_id <- function(x) tolower(gsub(" ", "-", x))


#' @name utils$as_ymd
#' @description format date as yyyy-mm-dd
#' @param x a date object
#' @return a date string
#' @describeIn utils
utils$as_ymd <- function(x) format(as.Date(x), "%Y-%m-%d")


#' @name utils$calc_age
#' @description calcuate age based on date of birth and another date
#' @describeIn utils
#' @param dob date of birth
#' @param date another date used to calcuate age (e.g., today)
#' @param digits number of digits to round to (default 2)
#' @retun a number rounded to two digits
utils$calc_age <- function(dob, date, digits = 2) {
    if (is.na(dob) | is.na(date))
        return(NA_real_)

    round((date - dob) / 365.25, digits)
}

#' @name utils$is_posixct
#' @description is value a posixct date class
#' @param x value to test
#' @return logical
utils$is_posixct <- function(x) class(x)[1] == "POSIXct"


#' @name utils$format_dx_code
#' @description given a diagnoses field, extract and format the dx code
#' @return a character
#' @describeIn utils
utils$format_dx_code <- function(x) {
    if (x == "-")
        return(NA_character_)

    paste0("dx_", unlist(strsplit(x, ":"))[1])
}

#' @name utils$recode_dx_certainty
#' @description given a certainty value, format and recode values
#' @param x a string containing a certainty rating
#' @describeIn utils
#' @return a string
utils$recode_dx_certainty <- function(x) {
    # opts <- list(
    #     "niet-zeker" = "provisional",
    #     "onzeker" = "provisional",
    #     "zeker" = "confirmed",
    #     "zeker-niet" = "unconfirmed"
    # )

    val <- NA_character_
    if (x != "-")
        val <- tolower(gsub(" ", "-", x))

    # if (val %in% names(opts))
    #     val <- opts[[val]]

    val
}


#' @name utils$recode_sex
#' @description recode sex into fairgenomes
#' @param x string containing a sex code
#' @return a string
utils$recode_sex <- function(x) {
    vals <- list(
        "vrouw" = "female", "f" = "female",
        "man" = "male", "m" = "male"
    )
    if (!tolower(x) %in% names(vals))
        return(NA_character_)

    vals[[tolower(x)]]
}

#' @name utils$timestamp
#' @description Return timestamp in Molgenis datetime format
#' @return dateTime as string
#' @describeIn utils
utils$timestamp <- function() format(Sys.time(), "%Y-%m-%dT%H:%M:%OS%z")


#'////////////////////////////////////////////////////////////////////////////

#' ~ 2 ~
#' COSAS Mappings

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
#' @return data mapped to `cosas_patients_mapped`
mappings$patients <- function(data) {
    data.table::setDT(data)
    data[, .(
        umcgID = UMCG_NUMBER,
        familyID = FAMILIENUMMER,
        dateOfBirth = purrr::map_chr(GEBOORTEDATUM, utils$as_ymd),
        biologicalSex = purrr::map_chr(GESLACHT, utils$recode_sex),
        maternalID = UMCG_MOEDER,
        paternalID = UMCG_VADER,
        linkedFamilyIDs = gsub("[\\,]\\s+", ",", FAMILIELEDEN),
        dateOfDeath = purrr::map_chr(OVERLIJDENSDATUM, utils$as_ymd),
        inclusionStatus = purrr::map_chr(OVERLIJDENSDATUM, function(x) {
            if (!is.na(utils$as_ymd(x)))
                return("deceased")
            "alive"
        }),
        ageAtDeath = purrr::map2_chr(GEBOORTEDATUM, OVERLIJDENSDATUM, utils$calc_age)
    )][order(as.integer(umcgID))][]
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
    provisionOpts <- c("zeker", "niet-zeker", "onzeker")
    data.table::setDT(data)
    data.table::rbindlist(
        list(
            data[, .(
                umcgID = UMCG_NUMBER,
                diagnosis = HOOFDDIAGNOSE,
                certainty = HOOFDDIAGNOSE_ZEKERHEID
            )],
            data[, .(
                umcgID = UMCG_NUMBER,
                diagnosis = EXTRA_DIAGNOSE,
                certainty = EXTRA_DIAGNOSE_ZEKERHEID
            )]
        )
    )[
        # remove rows where the diagnosis is missing
        diagnosis != "-"
    ][
        # sort by umcgID
        order(as.integer(umcgID))
    ][, `:=`(
        # format code and certainty and drop diagnosis
        code = purrr::map_chr(diagnosis, utils$format_dx_code),
        certainty = purrr::map_chr(certainty, utils$recode_dx_certainty),
        diagnosis = NULL
    )][
        # remove duplicated codes when grouped by ID and certainty
        , .SD[!duplicated(code)], by = c("umcgID", "certainty")
    ][
        # create provisionalPhenotype and excludedPhenotype columns
        # provisional is determined by certainty rating. If the value is
        # found in provisionalOpts or is.na, then it is provisional.
        # excludedPhenotypes are created when the value is "zeker-niet".
        # Create columns with the suffix "X" as we need to keep the original
        # mappings to exclude codes that exist in both columns.
        , `:=`(
            provisionalPhenotypeX = purrr::map2_chr(
                .x = code,
                .y = certainty,
                function(code, certainty) {
                    if (certainty %in% provisionOpts | is.na(certainty))
                        return(code)
                    NA_character_
                }
            ),
            excludedPhenotypeX = purrr::map2_chr(
                .x = code,
                .y = certainty,
                function(code, certainty) {
                    if (certainty %in% c("zeker-niet"))
                        return(code)
                    NA_character_
                }
            )
        ),
        by = umcgID
    ][
        # certainty and code can be dropped now
        , `:=`(certainty = NULL, code = NULL)
    ][
        # collapse provisionalPhenotypes and excludedPhenotypes
        # select unique values only and remove codes that exist in both
        # columns as it is difficult to determine which code is correct.
        , `:=`(
            provisionalPhenotype = paste0(
                unique(
                    provisionalPhenotypeX[
                        !is.na(provisionalPhenotypeX) &
                        !provisionalPhenotypeX %in% excludedPhenotypeX
                    ]
                ),
                collapse = ","
            ),
            excludedPhenotype = paste0(
                unique(
                    excludedPhenotypeX[
                        !is.na(excludedPhenotypeX) &
                        !excludedPhenotypeX %in% provisionalPhenotypeX
                    ]
                ),
                collapse = ","
            )
        ),
        by = umcgID
    ][
        # the previous chain repeats the values for all repeated IDs
        !duplicated(umcgID)
    ][
        # drop `*X` columns and force NAs
        , `:=`(
            provisionalPhenotype = dplyr::na_if(provisionalPhenotype, ""),
            excludedPhenotype = dplyr::na_if(excludedPhenotype, ""),
            provisionalPhenotypeX = NULL,
            excludedPhenotypeX = NULL
        )
    ][]
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
    data.table::setDT(data)
    data[, .(
        umcgID = UMCG_NUMMER,
        requestID = ADVVRG_ID,
        requestDate = purrr::map_chr(ADVIESVRAAG_DATUM, utils$as_ymd),
        sampleID = MONSTER_ID,
        testCode = tolower(TEST_CODE),
        dnaID = DNA_NUMMER,
        materialType = purrr::map_chr(MATERIAAL, utils$as_string_id),
        result = EINDUITSLAGTEKST,
        resultDate = purrr::map_chr(EINDUITSLAG_DATUM, utils$as_ymd),
        requestResultID = ADVIESVRAAGUITSLAG_ID,
        disorderCode = AANDOENING_CODE,
        labResult = LABUITSLAGTEKST,
        labResultComment = purrr::map_chr(
            LABUITSLAG_COMMENTAAR, function(x) {
                gsub("([\\r]+)([\\n]?)", "; ", x, perl = TRUE)
            }
        ),
        labResultDate = purrr::map_chr(LABUITSLAG_DATUM, utils$as_ymd),
        labResultID = LABUITSLAG_ID,
        labResultAvailability = LABRESULTS,
        authorizationStatus = AUTHORISED
    )][order(as.integer(umcgID))][]
}


#' @name mappings$array_adlas
#' @description map Adlas Array data into cosas_labs_array
#' @param data export from cosasportal_array_adlas
#' @return tibble
mappings$array_adlas <- function(data) {
    data.table::setDT(data)
    unique(
        data[, .(
            umcgID = UMCG_NUMBER,
            requestID = ADVVRG_ID,
            dnaID = DNA_NUMMER,
            testID = TEST_ID,
            testCode = tolower(TEST_CODE)
        )],
        by = c("umcgID", "requestID", "dnaID", "testID", "testCode")
    )[order(as.integer(umcgID))]
}

#' @name mappings$array_darwin
#' @description map array data from darwin to cosas_labs_array
#' @param data export from cosasportal_array_darwin
#' @return tibble
mappings$array_darwin <- function(data) {
    data.table::setDT(data)
    unique(
        data[, .(
            umcgID = UmcgNr,
            testCode = tolower(TestId), # codes are written into ID
            testDate = purrr::map_chr(TestDatum, utils$as_ymd),
            labIndication = purrr::map_chr(Indicatie, utils$as_string_id)
        )],
        by = c("umcgID", "testCode") # pull distinct cases by ID and CODE
    )[order(as.integer(umcgID))]
}

#' @name mappings$ngs_adlas
#' @description map ngs aldas data into cosas_labs_ngs
#' @param data export from cosasportal_ngs_adlas
#' @return tibble
mappings$ngs_adlas <- function(data) {
    data.table::setDT(data)
    unique(
        data[
            , .(
                umcgID = UMCG_NUMBER,
                requestID = ADVVRG_ID,
                dnaID = DNA_NUMMER,
                testID = TEST_ID,
                testCode = tolower(TEST_CODE)
            )
        ]
    )[order(as.integer(umcgID))]
}

#' @name mappings$ngs_darwin
#' @description map ngs darwin data into cosas_lab_ngs
#' @param data export from `cosasportal_ngs_darwin`
#' @return tibble
mappings$ngs_darwin <- function(data) {
    data.table::setDT(data)
    unique(
        data[
            , .(
                umcgID = UmcgNr,
                testCode = tolower(TestId), # code is written into ID
                testDate = TestDatum,
                labIndication = Indicatie,
                sequencer = Sequencer,
                prepKit = PrepKit,
                sequencingType = SequencingType,
                seqType = SeqType,
                capturingKit = CapturingKit,
                batchName = BatchNaam,
                genomeBuild = GenomeBuild
            )
        ][
            , `:=`(
                testDate = purrr::map_chr(testDate, utils$as_ymd),
                labIndication = purrr::map_chr(labIndication, utils$as_string_id)
            )
        ],
        by = c("umcgID", "testCode")
    )[order(as.integer(umcgID))]
}

#' @title Map Bench CNV Export
#' @name mappings$bench_cnv
#' @description Map HPO and fetal status into patients
#' @param data output from `cosasportal_bench_cnv`
#' @return a tibble
mappings$bench_cnv <- function(data) {
    # set fetus ID patterns
    patterns <- list(
        fetus = "^([0-9]{2,}F([0-9]{,2})?)$", # pure fetus cases
        twins = "^([0-9]{2,}F[0-9]{1}\\.[0-9]{1})$", # twins
        linked = "^([0-9]{2,}(F)?([0-9]{1,})?-[0-9]{2,})$" # linked IDs
    )

    # format data
    # 1) format umcgID: standarize separators, remove spaces, extra chars, etc.
    # 2) determine ID type: is it fetus, twin, linked, or default?
    # 3) set umcgID based on idType
    # 4) create fetus status column
    # 5) create twin status column
    # 6) extract maternal ID
    # 7) extract linked ID
    # 8) format dateOfDiagnosis
    data.table::setDT(data)
    data[, .(
        id = primid,
        familyID = secid,
        biologicalSex = gender,
        observedPhenotype = Phenotype
    )][, `:=`(
        id = purrr::map_chr(id, function(x) {
            x1 <- gsub("([_=])", "-", x)
            x2 <- gsub("((\\s+)|(\\(snp\\))|([-]OND))", "", x1)
            gsub("([-])$", "", x2)
        }),
        idType = purrr::map_chr(id, function(x) {
            if (grepl(patterns$fetus, x)) {
                "fetus"
            } else if (grepl(patterns$twin, x)) {
                "twin"
            } else if (grepl(patterns$linked, x)) {
                "linked"
            } else {
                "default"
            }
        })
    )][, `:=`(
        umcgID = purrr::map2_chr(id, idType, function(id, type) {
            if (type == "linked") {
                unlist(strsplit(id, "-"))[1]
            } else {
                id
            }
        }),
        biologicalSex = purrr::map_chr(biologicalSex, utils$recode_sex),
        observedPhenotype = purrr::map_chr(
            observedPhenotype, function(values) {
                if (is.na(values))
                    return(NA_character_)

                c1 <- unlist(strsplit(values, "\\s+"))
                c2 <- gsub("HP:", "", c1)
                paste0(unique(c2), collapse = ",")
            }
        ),
        fetusStatus = purrr::map_lgl(
            idType, function(type) type %in% names(patterns)
        ),
        twinStatus = purrr::map_lgl(idType, function(type) type == "twin"),
        maternalID = purrr::map2_chr(id, idType, function(id, type) {
            if (type %in% c("fetus", "twin")) {
                split <- unlist(strsplit(id, "F"))[1]
                gsub("F", "", split)
            } else if (type == "linked") {
                split <- unlist(strsplit(id, "-"))[1]
                gsub("F", "", split)
            } else {
                NA_character_
            }
        }),
        altPatientID = purrr::map2_chr(id, idType, function(id, type) {
            if (type != "linked")
                return(NA_character_)
            unlist(strsplit(id, "-"))[2]
        })
    )][, `:=`(id = NULL, idType = NULL)][]
}
