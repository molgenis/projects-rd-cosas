#'////////////////////////////////////////////////////////////////////////////
#' FILE: test-validate-raw-files.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-08-16
#' MODIFIED: 2021-08-16
#' PURPOSE: validate raw data files
#' STATUS: in.progress
#' PACKAGES: readxl
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

#' @name validate_vars
#' @description compare two arrays of variable names
#' @param expected an array of known variable names
#' @param x an array of names from a new object
validate_vars <- function(expected, x) {
    counter <- 0
    sapply(x, function(d) {
        if (d %in% expected) {
            counter <<- counter + 1
        } else {
            cli::cli_alert_warning("{.value {d}} is an unexpected variable")
        }
    })
    return(counter)
}

#' ~ 1 ~
#' Read and validate the structure of `cosasportal_patients`
testthat::test_that("cosasportal_patients is valid", {
    vars <- c(
        "UMCG_NUMBER",
        "OVERLIJDENSDATUM",
        "FAMILIENUMMER",
        "GEBOORTEDATUM",
        "GESLACHT",
        "FAMILIELEDEN",
        "UMCG_MOEDER",
        "UMCG_VADER"
    )

    file <- readxl::read_xlsx(
        path = "../../_raw/cosasportal_patients.xlsx",
        sheet = 1,
        col_types = c("text", "date", "text", "date", rep("text", 4)),
    )

    count <- validate_vars(vars, colnames(file))

    testthat::expect_equal(
        object = count,
        expected = length(vars),
        label = "cosasportal_patients does not contain expected variables"
    )

    rm(list = c("vars", "file", "count"))

})

#' ~ 2 ~
#' Read and validate the structure of `cosasportal_diagnoses`
testthat::test_that("cosasportal_diagnoses is valid", {
    vars <- c(
       "UMCG_NUMBER",
       "HOOFDDIAGNOSE",
       "HOOFDDIAGNOSE_ZEKERHEID",
       "EXTRA_DIAGNOSE",
       "EXTRA_DIAGNOSE_ZEKERHEID",
       "DATUM_EERSTE_CONSULT",
       "OND_ID"
    )

    file <- readxl::read_xlsx(
        path = "../../_raw/cosasportal_diagnoses.xlsx",
        sheet = 1,
        col_types = c(rep("text", 5), "date", "text")
    )

    count <- validate_vars(vars, colnames(file))

    testthat::expect_equal(
        object = count,
        expected = length(vars),
        label = "cosasportal_diagnoses does not contain expected variables"
    )

    rm(list = c("vars", "file", "count"))

})

#' ~ 3 ~
#' Validate the structure of `cosasportal_samples`
testthat::test_that("cosasporatal_samples is valid", {

    vars <- c(
        "UMCG_NUMMER",
        "ADVVRG_ID",
        "ADVIESVRAAG_DATUM",
        "MONSTER_ID",
        "TEST_CODE",
        "TEST_OMS",
        "DNA_NUMMER",
        "MATERIAAL",
        "EINDUITSLAGTEKST",
        "EINDUITSLAG_DATUM",
        "ADVIESVRAAGUITSLAG_ID",
        "ADVIESVRAAGUITSLAG_CODE",
        "AANDOENING_CODE",
        "LABUITSLAGTEKST",
        "LABUITSLAG_COMMENTAAR",
        "LABUITSLAG_DATUM",
        "LABUITSLAG_ID",
        "LABUITSLAG_CODE",
        "LABRESULTS",
        "AUTHORISED"
    )

    file <- readxl::read_xlsx(
        path = "../../_raw/cosasportal_samples.xlsx",
        sheet = 1,
        col_types = "text"
    )

    count <- validate_vars(vars, colnames(file))

    testthat::expect_equal(
        object = count,
        expected = length(vars),
        label = "cosasportal_samples contains unexpected variables"
    )

    rm(list = c("vars", "file", "count"))

})

#' ~ 4 ~
#' Validate the structure of the `cosasportal_array_adlas`
testthat::test_that("cosasportal_array_adlas is valid", {

    vars <- c(
        "UMCG_NUMBER",
        "ADVVRG_ID",
        "DNA_NUMMER",
        "TEST_ID",
        "TEST_CODE",
        "TEST_OMS",
        "SGA_CHROMOSOME_REGION",
        "SGA_CLASSIFICATION",
        "SGA_CYTOBAND",
        "SGA_DECIPHER_SYNDROMES",
        "SGA_DGV_SIMILARITY",
        "SGA_EVENT",
        "SGA_EVIDENCE_SCORE",
        "SGA_HMRELATED_GENES",
        "SGA_HMRELATED_GENES_COUNT",
        "SGA_LENGTH",
        "SGA_MOSAIC",
        "SGA_MOSAIC_PERCENTAGE",
        "SGA_NO_OF_PROBES",
        "SGA_NOTES",
        "SGA_OMIM_MORBID_MAP",
        "SGA_OMIM_MORBIDMAP_COUNT",
        "SGA_PROBE_MEDIAN",
        "SGA_REFSEQ_CODING_GENES",
        "SGA_REFSEQ_CODING_GENES_COUNT",
        "SGA_REGIONS_UMCG_CNV_NL_COUNT",
        "SGA_SIMILAR_PREVIOUS_CASES",
        "SGA_OVERERVING"
    )

    file <- readxl::read_xlsx(
        path = "../../_raw/cosasportal_array_adlas.xlsx",
        sheet = 1,
        col_types = "text"
    )

    count <- validate_vars(vars, colnames(file))

    testthat::expect_equal(
        object = count,
        expected = length(vars),
        label = "cosasportal_array_adlas does not contain expected variables"
    )

    rm(list = c("vars", "file", "count"))

})



#' ~ 5 ~
#' Validate the structure of `cosasportal_`
testthat::test_that("cosasportal_array_darwin is valid", {

    vars <- c(
        "UmcgNr",
        "TestId",
        "TestDatum",
        "Indicatie",
        "BatchNaam",
        "CallRate",
        "StandaardDeviatie"
    )

    file <- readxl::read_xlsx(
        path = "../../_raw/cosasportal_array_darwin.xlsx",
        sheet = 1,
        col_types = c("text", "text", "date", rep("text", 4))
    )

    count <- validate_vars(vars, colnames(file))

    testthat::expect_equal(
        object = count,
        expected = length(vars),
        label = "cosasportal_array_darwin does not contain expected variables"
    )

    rm(list = c("vars", "file", "count"))

})

#' ~ 5 ~
#' Validate the structure of `cosasportal_ngs_adlas`
testthat::test_that("cosasportal_ngs_adlas is valid", {

    vars <- c(
        "UMCG_NUMBER",
        "ADVVRG_ID",
        "DNA_NUMMER",
        "TEST_ID",
        "TEST_CODE",
        "TEST_OMS",
        "GEN",
        "MUTATIE",
        "KLASSE",
        "NM_NUMMER",
        "LRGS_NUMMER",
        "AMPLICON",
        "ALLELFREQUENTIE",
        "OVERERVING"
    )

    file <- readxl::read_xlsx(
        path = "../../_raw/cosasportal_ngs_adlas.xlsx",
        sheet = 1,
        col_types = "text"
    )

    count <- validate_vars(vars, colnames(file))

    testthat::expect_equal(
        object = count,
        expected = length(vars),
        label = "cosasportal_ngs_adlas does not contain expected variables"
    )

    rm(list = c("vars", "file", "count"))

})

#' ~ 5 ~
#' Validate the structure of `cosasportal_ngs_darwin`
testthat::test_that("cosasportal_ngs_darwin is valid", {

    vars <- c(
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
        "GenomeBuild",
        "CallRate",
        "StandaardDeviatie"
    )

    file <- readxl::read_xlsx(
        path = "../../_raw/cosasportal_ngs_darwin.xlsx",
        sheet = 1,
        col_types = c(rep("text", 2), "date", rep("text", 10))
    )

    count <- validate_vars(vars, colnames(file))

    testthat::expect_equal(
        object = count,
        expected = length(vars),
        label = "cosasportal_ngs_darwin does not contain expected variables"
    )

    rm(list = c("vars", "file", "count"))

})

#' ~ 5 ~
#' Validate the structure of `cosasportal_bench_cnv`
testthat::test_that("cosasportal_bench_cnv is valid", {
    vars <- c(
        "primid",
        "secid",
        "externalid",
        "gender",
        "comment",
        "Phenotype",
        "created"
    )

    file <- readxl::read_xlsx(
        path = "../../_raw/cosasportal_bench_cnv.xlsx",
        sheet = 1,
        col_types = c(rep("text", 6), "date")
    )

    count <- validate_vars(vars, colnames(file))

    testthat::expect_equal(
        object = count,
        expected = length(vars),
        label = "cosasportal_bench_cnv does not contain expected variables"
    )

    rm(list = c("vars", "file", "count"))
})
