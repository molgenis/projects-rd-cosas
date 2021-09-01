#' ////////////////////////////////////////////////////////////////////////////
#' FILE: mapping_cosasrefs.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-07-28
#' MODIFIED: 2021-09-01
#' PURPOSE: build datasets for reference entities
#' STATUS: working; ongoing
#' PACKAGES: *see below*
#' COMMENTS: NA
#' ////////////////////////////////////////////////////////////////////////////


library2("data.table")
# source("R/_load.R")


# convert objects to data.table
data.table::setDT(portal_diagnoses)
data.table::setDT(portal_samples)
data.table::setDT(portal_array_adlas)
data.table::setDT(portal_array_darwin)
data.table::setDT(portal_ngs_adlas)
data.table::setDT(portal_ngs_darwin)


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
cli::cli_alert_info("Building {.val cosasrefs_diagnoses}")


# merge SORTA results
sorta <- data.table::fread("./data/sorta_cineas_hpo_mappings.csv")[
    , .(description = Name, ontologyTermIRI, score)
][score >= 70 & ontologyTermIRI %like% "obo/HP_"][
    , `:=`(
        hpo = gsub("http://purl.obolibrary.org/obo/HP_", "", ontologyTermIRI),
        ontologyTermIRI = NULL,
        score = NULL
    )
][]

# build diagnostic codes and descriptions
diagnoses <- data.table::rbindlist(
        list(
            portal_diagnoses[, .(description = HOOFDDIAGNOSE)],
            portal_diagnoses[, .(description = EXTRA_DIAGNOSE)]
        )
    )[
        description != "-" & !duplicated(description)
    ][
        ,
        `:=`(
            code = purrr::map_chr(description, function(x) {
                val <- unlist(strsplit(x, ":"))[1]
                trimws(tolower(val), which = "both")
            }),
            description = purrr::map_chr(description, function(x) {
                val <- unlist(strsplit(x, ":"))[2]
                trimws(val, which = "both")
            }),
            codesystem = "cineas"
        )
    ][
        ,
        id := paste0("dx_", code)
    ][
        order(as.integer(code)),
        .(id, description, codesystem, code)
    ]

# merge HPO codes with diagnoses
cosasrefs_diagnoses <- merge(
    x = diagnoses,
    y = sorta,
    by = "description",
    all.x = TRUE
)[, .(id, description, codesystem, code, hpo)]

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
#' Use the following code to identify materialTypes.
#'
#' @noRD

# portal_samples[
#     ,
#     .(material = tolower(MATERIAAL))
# ][!duplicated(material)][order(material)]

# # write code to file
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
#
# data.table::setDT(portal_samples)
#
# cosasrefs_materialTypes <- portal_samples[
#     , .(material = MATERIAAL)
#     ][
#         !duplicated(material)
#     ][
#         order(material),
#         id := purrr::map_chr(material, function(x) {
#             tolower(gsub(" ", "-", x))
#         })
#     ]

#' @title COSAS Test Codes Reference Entity
#' @description create cosasrefs_testCodes
#' @section Methodology:
#'
#' Most of the test metadata comes from the samples dataset. However,
#' there may be some extra cases in the ADLAS and Darwin extracts.
#'
#' @noRd
cli::cli_alert_info("Building {.val cosasrefs_testCodes}")

testCodes <- merge(
    x = data.table::rbindlist(
        list(
            portal_samples[, .(code = TEST_CODE, description = TEST_OMS)],
            portal_array_adlas[, .(code = TEST_CODE, description = TEST_OMS)],
            portal_ngs_adlas[, .(code = TEST_CODE, description = TEST_OMS)]
        )
        )[!duplicated(code)][
            order(code), `:=`(
                label = NA,
                panel = NA,
                labelPanel = NA
            )
        ][, .(code, description)
    ],
    y = data.table::setDT(
        readxl::read_xlsx(
            path = "_raw/geneticlines2021-03-10_15_52_37.366.xlsx",
            sheet = "geneticlines_ADLAStest"
        )
    ),
    by.x = "code",
    by.y = "TEST_CODE",
    all = TRUE
)


# compile list of genes per testCode
cli::cli_alert_info("Compiling gene lists...")
sheets <- readxl::excel_sheets("_raw/testcodes_ngs_array.xlsx")
sheets <- sheets[sheets %in% testCodes$code]
genes <- data.table::as.data.table(
    purrr::map_df(sheets, function(name) {
        # cli::cli_alert_info("Processing sheet {.val {name}}")
        d <- readxl::read_excel(
            path = "_raw/testcodes_ngs_array.xlsx",
            sheet = name,
            col_names = "genes"
        )
        data.frame(
            code = name,
            genes = paste0(sort(unique(d$genes)), collapse = ",")
        )
    })
)

# create refEntity
cosasrefs_testCodes <- merge(
    x = testCodes,
    y = genes,
    by = "code",
    all.x = TRUE
)[, id := tolower(code)][
    , .(id, code, description, label, panel, genes)
][order(id)]



# Optional: split sequencing method, preparation, etc.
# seqMethodPatterns <- list(
#     wes = paste0(
#         "(",
#         "(analyse exoom)", "|",
#         "(analyse 5gpm)", "|",
#         "(analyse klinisch exoom)", "|",
#         "(specifieke vraagstelling exoom)",
#         ")"
#     ),
#     wgs = paste0(
#         "(",
#         "(whole genome sequencing)",
#         ")"
#     ),
#     ngts = paste0(
#         "(",
#         "(analyse ngs)", "|",
#         "(analyse targeted svp)", "|",
#         ")"
#     ),
#     array = paste0(
#         "(",
#         "(CNV + )",
#         ")"
#     )
# )
#
# d[
#     , `:=`(
#         sequencingMethod = purrr::map_chr(description, function(x) {
#             val <- tolower(x)
#             if (grepl(seqMethodPatterns$wes, val, perl = TRUE)) {
#                 "Whole Exome Sequencing"
#             } else if (grepl(seqMethodPatterns$wgs, val, perl = TRUE)) {
#                 "Whole Genome Sequencing"
#             } else if (grepl(seqMethodPatterns$ngts, val, perl = TRUE)) {
#                 "Next Generation Targeted Sequencing"
#             } else {
#                 NA_character_
#             }
#         }),
#         preparation = purrr::map_chr(description, function(x) {
#             val <- tolower(x)
#             if (grepl("(uncultered|cultured)", x)) {
#                 grep()
#             }
#         })
#     )
# ]


#' @name cosasrefs_labIndications
#' @description create reference table for labIndications
#'
#' @section Methodology:
#'
#' The labIndication reference entity is used to categorize the reason a sample
#' was collected and map it into FairGenomes terminology. For the intial release
#' of COSAS, this information will be explicitly defined in the YML. Use the following
#' code to find the information.

# data.table::rbindlist(
#     list(
#         portal_array_darwin[, .(Indicatie)],
#         portal_ngs_darwin[, .(Indicatie)]
#     )
# )[!duplicated(Indicatie)][,
#     `:=`(
#         Indicatie = gsub(" ", "-", tolower(Indicatie))
#     )
# ][order(Indicatie)]
