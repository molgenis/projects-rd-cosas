#'////////////////////////////////////////////////////////////////////////////
#' FILE: utils_mapping.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-08-16
#' MODIFIED: 2021-08-17
#' PURPOSE: methods for `mapping_cosas.R`
#' STATUS: in.progress
#' PACKAGES: data.table, dplyr, purrr, stringr
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

    paste0("dx_", stringr::str_split(x, ":", n = 2, simplify = TRUE)[[1]])
}

#' @name utils$recode_dx_certainty
#' @description given a certainty value, format and recode values
#' @param x a string containing a certainty rating
#' @describeIn utils
#' @return a string
utils$recode_dx_certainty <- function(x) {
    opts <- list(
        "niet-zeker" = "provisional",
        "onzeker" = "provisional",
        "zeker" = "confirmed",
        "zeker-niet" = "unconfirmed"
    )

    val <- NA_character_
    if (x != "-")
        val <- tolower(gsub(" ", "-", x))

    if (val %in% names(opts))
        val <- opts[[val]]

    return(val)
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
    data.table::setnames(data,
        old = c(
            "UMCG_NUMBER",
            "FAMILIENUMMER",
            "GEBOORTEDATUM",
            "GESLACHT",
            "UMCG_MOEDER",
            "UMCG_VADER",
            "FAMILIELEDEN",
            "OVERLIJDENSDATUM"
        ),
        new = c(
            "umcgID",
            "familyID",
            "dateOfBirth",
            "biologicalSex",
            "maternalID",
            "paternalID",
            "linkedFamilyIDs",
            "dateOfDeath"
        )
    )

    # format data
    # 1) recode biological sex
    # 2) remove space(s) in linked family IDs
    # 3) create bool to indicate if a patient is deceased
    # 4) calcuate age at death
    # 5) format date of birth
    # 6) formate date of death
    data[, `:=`(
        biologicalSex = purrr::map_chr(biologicalSex, utils$recode_sex),
        linkedFamilyIDs = gsub("[\\,]\\s+", ",", linkedFamilyIDs),
        inclusionStatus = purrr::map_chr(dateOfDeath, function(x) {
            if (!is.na(x)) {
                "deceased"
            } else {
                "alive"
            }
        }),
        ageAtDeath = purrr::map2_chr(dateOfBirth, dateOfDeath, utils$calc_age),
        dateOfBirth = purrr::map_chr(dateOfBirth, utils$as_ymd),
        dateOfDeath = purrr::map_chr(dateOfDeath, utils$as_ymd)
    )]

    # sort by ID
    data[, umcgID := as.integer(umcgID)]
    data.table::setorder(data, umcgID)
    data[, umcgID := as.character(umcgID)]


    return(data[])
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
    data.table::setDT(data)
    data.table::setnames(
        data,
        old = c(
            "UMCG_NUMBER",
            "HOOFDDIAGNOSE",
            "HOOFDDIAGNOSE_ZEKERHEID",
            "EXTRA_DIAGNOSE",
            "EXTRA_DIAGNOSE_ZEKERHEID",
            "DATUM_EERSTE_CONSULT",
            "OND_ID"
        ),
        new = c(
            "umcgID",
            "clinicalDiagnosis",
            "clinicalDiagnosisCertainty",
            "secondaryDiagnosis",
            "secondaryDiagnosisCertainty",
            "dateOfDiagnosis",
            "ondID"
        )
    )

    # format data
    # 1) process primary diagnosis code and missing values
    # 2) format certainty of primary diagnosis
    # 3) processing extra diagnosis code and missing values
    # 4) form certainty of extra diagnosis
    # 5) format date
    data[, `:=`(
        clinicalDiagnosis = purrr::map_chr(clinicalDiagnosis, utils$format_dx_code),
        clinicalDiagnosisCertainty = purrr::map_chr(
            clinicalDiagnosisCertainty, utils$recode_dx_certainty
        ),
        secondaryDiagnosis = purrr::map_chr(secondaryDiagnosis, utils$format_dx_code),
        secondaryDiagnosisCertainty = purrr::map_chr(
            secondaryDiagnosisCertainty, utils$recode_dx_certainty
        ),
        dateOfDiagnosis = purrr::map_chr(dateOfDiagnosis, utils$as_ymd)
    )]

    data[, umcgID := as.integer(umcgID)]
    data.table::setorder(data, umcgID)
    data[, umcgID := as.character(umcgID)]

    return(data[])
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

    # drop variables -- this information will be linked via the xrefs
    data[, `:=`(
        TEST_OMS = NULL,
        ADVIESVRAAGUITSLAG_CODE = NULL,
        LABUITSLAG_CODE = NULL
    )]

    # rename variables
    data.table::setnames(
        data,
        old = c(
            "UMCG_NUMMER",
            "ADVVRG_ID",
            "ADVIESVRAAG_DATUM",
            "MONSTER_ID",
            "TEST_CODE",
            # "TEST_OMS", # dropped from table
            "DNA_NUMMER",
            "MATERIAAL",
            "EINDUITSLAGTEKST",
            "EINDUITSLAG_DATUM",
            "ADVIESVRAAGUITSLAG_ID",
            # "ADVIESVRAAGUITSLAG_CODE", # droped from table
            "AANDOENING_CODE",
            "LABUITSLAGTEKST",
            "LABUITSLAG_COMMENTAAR",
            "LABUITSLAG_DATUM",
            "LABUITSLAG_ID",
            # "LABUITSLAG_CODE", # droped from table
            "LABRESULTS",
            "AUTHORISED"
        ),
        new = c(
            "umcgID", # "UMCG_NUMMER"
            "requestID", # "ADVVRG_ID"
            "requestDate", # "ADVIESVRAAG_DATUM"
            "sampleID", # "MONSTER_ID"
            "testCode", # "TEST_CODE"
            # "test_description", # "TEST_OMS" # for refEntity
            "dnaID", # "DNA_NUMMER"
            "materialType", # "MATERIAAL"
            "result", # "EINDUITSLAGTEKST"
            "resultDate", # "EINDUITSLAG_DATUM"
            "requestResultID", # "ADVIESVRAAGUITSLAG_ID"
            # "", # "ADVIESVRAAGUITSLAG_CODE" # for refEntity
            "disorderCode", # "AANDOENING_CODE"
            "labResult", # "LABUITSLAGTEKST"
            "labResultComment", # "LABUITSLAG_COMMENTAAR"
            "labResultDate", # "LABUITSLAG_DATUM"
            "labResultID", # "LABUITSLAG_ID"
            # "", # "LABUITSLAG_CODE", # for RefEntity
            "labResultAvailability", # "LABRESULTS",
            "authorizedStatus" # "AUTHORISED"
        )
    )

    # format data
    # 1) recode/format materialType
    # 2) lowercase test_code (to match with refEntity)
    # 3) lower disorderCode
    data[, `:=`(
        requestDate = purrr::map_chr(requestDate, utils$as_ymd),
        resultDate = purrr::map_chr(resultDate, utils$as_ymd),
        labResultDate = purrr::map_chr(labResultDate, utils$as_ymd),
        materialType = purrr::map_chr(materialType, utils$as_string_id),
        testCode = tolower(testCode),
        disorderCode = tolower(disorderCode)
    )]

    # sort by ID
    data[, umcgID := as.integer(umcgID)]
    data.table::setorder(data, umcgID)
    data[, umcgID := as.character(umcgID)]

    return(data[])
}


#' @name mappings$array_adlas
#' @description map Adlas Array data into cosas_labs_array
#' @param data export from cosasportal_array_adlas
#' @return tibble
mappings$array_adlas <- function(data) {
    data.table::setDT(data)

    # reduce dataset to select columns (explicitly state which columns to remove)
    data[, `:=`(
        # UMCG_NUMBER, ADVVRG_ID, DNA_NUMMER, TEST_ID, TEST_CODE, # standard variables
        TEST_OMS = NULL,
        # SGA_CHROMOSOME_REGION = NULL,
        SGA_CLASSIFICATION = NULL,
        SGA_CYTOBAND = NULL,
        # SGA_DECIPHER_SYNDROMES = NULL,
        SGA_DGV_SIMILARITY = NULL,
        SGA_EVENT = NULL,
        SGA_EVIDENCE_SCORE = NULL,
        SGA_HMRELATED_GENES = NULL,
        SGA_HMRELATED_GENES_COUNT = NULL,
        SGA_LENGTH = NULL,
        SGA_MOSAIC = NULL,
        SGA_MOSAIC_PERCENTAGE = NULL,
        SGA_NO_OF_PROBES = NULL,
        SGA_NOTES = NULL,
        SGA_OMIM_MORBID_MAP = NULL,
        SGA_OMIM_MORBIDMAP_COUNT = NULL,
        SGA_PROBE_MEDIAN = NULL,
        SGA_REFSEQ_CODING_GENES = NULL,
        SGA_REFSEQ_CODING_GENES_COUNT = NULL,
        SGA_REGIONS_UMCG_CNV_NL_COUNT = NULL,
        SGA_SIMILAR_PREVIOUS_CASES = NULL,
        SGA_OVERERVING = NULL
    )]

    data.table::setnames(
        data,
        old = c(
            "UMCG_NUMBER", "ADVVRG_ID", "DNA_NUMMER", "TEST_ID", "TEST_CODE",
            "SGA_CHROMOSOME_REGION", "SGA_DECIPHER_SYNDROMES"
        ),
        new = c(
            "umcgID", "requestID", "dnaID", "testID", "testCode",
            "chromosomeRegion", "decipherSyndromes"
        )
    )

    # format data
    # 1) lowercase testCode
    data[, testCode := tolower(testCode)]

    data[, umcgID := as.integer(umcgID)]
    data.table::setorder(data, umcgID)
    data[, umcgID := as.character(umcgID)]

    return(data[])
}

#' @name mappings$array_darwin
#' @description map array data from darwin to cosas_labs_array
#' @param data export from cosasportal_array_darwin
#' @return tibble
mappings$array_darwin <- function(data) {
    data.table::setDT(data)

    # explicitly define columns to remove
    data[, `:=`(
        # UmcgNr, TestId, TestDatum, Indicatie # standard variables
        BatchNaam = NULL,
        CallRate = NULL,
        StandaardDeviatie = NULL
    )]
    data.table::setnames(
        data,
        old = c("UmcgNr", "TestId", "TestDatum", "Indicatie"),
        new = c("umcgID", "testCode", "testDate", "labIndication")
    )

    # format data
    # 1) lower testCode
    # 2) format testDate
    # 3) formate labIndication
    data[, `:=`(
        testCode = tolower(testCode),
        testDate = purrr::map_chr(testDate, utils$as_ymd),
        labIndication = purrr::map_chr(labIndication, utils$as_string_id)
    )]

    data[, umcgID := as.integer(umcgID)]
    data.table::setorder(data, umcgID)
    data[, umcgID := as.character(umcgID)]

    return(unique(data, by = c("umcgID", "testCode")))
}

#' @name mappings$ngs_adlas
#' @description map ngs aldas data into cosas_labs_ngs
#' @param data export from cosasportal_ngs_adlas
#' @return tibble
mappings$ngs_adlas <- function(data) {
    data.table::setDT(data)

    data[, `:=`(
        # UMCG_NUMBER, ADVVRG_ID, DNA_NUMMER, TEST_ID, TEST_CODE,
        TEST_OMS = NULL,
        # GEN = NULL,
        # MUTATIE = NULL,
        KLASSE = NULL,
        NM_NUMMER = NULL,
        LRGS_NUMMER = NULL,
        AMPLICON = NULL,
        # ALLELFREQUENTIE = NULL,
        OVERERVING = NULL
    )]
    data.table::setnames(
        data,
        old = c(
            "UMCG_NUMBER", "ADVVRG_ID", "DNA_NUMMER",
            "TEST_ID", "TEST_CODE", "GEN", "MUTATIE", "ALLELFREQUENTIE"
        ),
        new = c(
            "umcgID", "requestID", "dnaID", "testID",
            "testCode", "gene", "mutation", "alleleFrequency"
        )
    )

    # format data
    # 1) lower testcode
    data[, `:=`(
        testCode = tolower(testCode),
        alleleFrequency = purrr::map_chr(alleleFrequency, function(x) {
            if (x %in% c("-", "_"))
                return(NA_character_)
            tolower(x)
        })
    )]

    data[, umcgID := as.integer(umcgID)]
    data.table::setorder(data, umcgID)
    data[, umcgID := as.character(umcgID)]
    return(data[])
}

#' @name mappings$ngs_darwin
#' @description map ngs darwin data into cosas_lab_ngs
#' @param data export from `cosasportal_ngs_darwin`
#' @return tibble
mappings$ngs_darwin <- function(data) {
    data.table::setDT(data)

    data[, `:=`(
        # UmcgNr, TestId, TestDatum, # standard attributes
        # Indicatie, Sequencer, PrepKit, Sequencing Type, # standard attributes
        # SeqType, CapturingKit, BatchNaam, GenomeBuild, # standard attributes
        CallRate = NULL,
        StandaardDeviatie = NULL
    )]
    data.table::setnames(
        data,
        old = c(
            "UmcgNr",
            "TestId",
            "TestDatum",
            "Indicatie",
            "Sequencer",
            "PrepKit",
            "Sequencing Type",
            "SeqType",
            "CapturingKit",
            "BatchNaam",
            "GenomeBuild"
        ),
        new = c(
            "umcgID", # "UmcgNr"
            "testCode", # "TestId"
            "testDate", # "TestDatum"
            "labIndication", # "Indicatie"
            "sequencer", # "Sequencer"
            "prepKit", # "PrepKit"
            "sequencingType", # "Sequencing Type"
            "seqType", # "SeqType"
            "capturingKit", # "CapturingKit"
            "batchName", # "BatchNaam"
            "genomeBuild" # "GenomeBuild"
        )
    )

    # format data
    # 1) lower testCode
    # 2) format testDate
    # 3) format labIndication
    data[, `:=`(
        testCode = tolower(testCode),
        testDate = purrr::map_chr(testDate, utils$as_ymd),
        labIndication = purrr::map_chr(labIndication, utils$as_string_id)
    )]

    data[, umcgID := as.integer(umcgID)]
    data.table::setorder(data, umcgID)
    data[, umcgID := as.character(umcgID)]
    return(unique(data, by = c("umcgID", "testCode")))
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

    data.table::setDT(data)
    data[, `:=`(
        # primid, secid, # standard vars
        externalid = NULL,
        # gender = NULL, # keep
        comment = NULL
        # Phenotype, created # keep
    )]
    data.table::setnames(
        data,
        old = c("primid", "secid", "gender", "Phenotype", "created"),
        new = c(
            "id", "familyID", "biologicalSex", "observedPhenotype", "dateofDiagnosis"
        )
    )

    # format data
    # 1) format umcgID: standarize separators, remove spaces, extra chars, etc.
    # 2) determine ID type: is it fetus, twin, linked, or default?
    # 3) set umcgID based on idType
    # 4) create fetus status column
    # 5) create twin status column
    # 6) extract maternal ID
    # 7) extract linked ID
    # 8) format dateofDiagnosis
    data[, `:=`(
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
            if (type != "linked")
                return(id)
            unlist(strsplit(id, "_"))[1]
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
        fetusStatus = purrr::map_chr(
            idType, function(type) type %in% names(patterns)
        ),
        twinStatus = purrr::map_chr(idType, function(type) type == "twin"),
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
        linkedPatientID = purrr::map2_chr(id, idType, function(id, type) {
            if (type != "linked")
                return(NA_character_)
            unlist(strsplit(id, "-"))[2]
        }),
        dateofDiagnosis = purrr::map_chr(dateofDiagnosis, utils$as_ymd)
    )]

    data[, `:=`(id = NULL, idType = NULL)]
    # data[, umcgID := as.integer(umcgID)]
    # data.table::setorder(data, umcgID)
    # data[, umcgID := as.character(umcgID)]

    return(data[])
}
