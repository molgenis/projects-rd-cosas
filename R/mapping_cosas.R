#' ////////////////////////////////////////////////////////////////////////////
#' FILE: cosas_mapping.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-07-22
#' MODIFIED: 2021-09-02
#' PURPOSE: Mapping portal tables to main pkg
#' STATUS: working
#' PACKAGES: data.table, purrr, dplyr, tidyr
#' COMMENTS: NA
#' ////////////////////////////////////////////////////////////////////////////

# library2("data.table")
# source("R/_load.R")
# source("R/utils_mapping.R")


#' Map into COSAS Terminology
cli::cli_alert_info("Mapping portal data objects into COSAS terminology")
cosas_patients_mapped <- mappings$patients(portal_patients)
cosas_diagnoses_mapped <- mappings$diagnoses(portal_diagnoses)
cosas_samples_mapped <- mappings$samples(portal_samples)
cosas_array_adlas_mapped <- mappings$array_adlas(portal_array_adlas)
cosas_array_darwin_mapped <- mappings$array_darwin(portal_array_darwin)
cosas_ngs_adlas_mapped <- mappings$ngs_adlas(portal_ngs_adlas)
cosas_ngs_darwin_mapped <- mappings$ngs_darwin(portal_ngs_darwin)
cosas_bench_cnv_mapped <- mappings$bench_cnv(portal_bench_cnv)

# rm(list = c(
#     "portal_patients", "portal_diagnoses", "portal_samples",
#     "portal_array_adlas", "portal_array_darwin", "portal_ngs_adlas",
#     "portal_ngs_darwin", "portal_bench_cnv"
# ))

#'//////////////////////////////////////

#' @title Process Cartegenia
#' @description apply additional filters to the export before merging into COSAS
#' @section Methodology
#'
#' At this point, the export has already been processed. This process included
#' transforming and reshaping the data into COSAS data model. Since we aren't
#' adding any new information to COSAS we only want to merge confirmed phenotypes
#' to existing COSAS patients. Therefore, the object `cosas_patients_mapped`
#' should be considered the official list of patients and everything else should
#' be filtered accordingly.
#'
#' However, if at some point you would like to add fetus cases, then see the
#' subsequent mapping section.
#'
#' @noRd
tryCatch({

    #' Records are kept if all 3 conditions are met
    #' 1. `confirmedPhenotype` should not be `NA`
    #' 2. `umcgID` must exist in `cosas_patients_mapped$umcgID`
    #' 3. `umcgID` should not be duplicated
    cosas_cartegenia <- cosas_bench_cnv_mapped[
        !is.na(confirmedPhenotype) &
        umcgID %in% cosas_patients_mapped$umcgID &
        !duplicated(umcgID),
        .(umcgID, familyID, fetusStatus, twinStatus, confirmedPhenotype)
    ]

    cli::cli_alert_success("Built Cartegenia dataset")

}, error = function(err) {
    cli::cli_alert_danger("Failed to process Cartegenia data:\n{.text {err}}")

}, warning = function(warn) {
    cli::cli_alert_danger("Failed to process Cartegenia data:\n{.text {warn}}")

})

#' @title Create COSAS Patients
#' @description create `cosas_patients`
#' @section Methodology:
#'
#' The patients table (i.e. `cosas_patients`) is created by merging the
#' mapped patients object (i.e., `cosas_patients_mapped`) and the Categenia
#' object that was built in the previous step.
#'
#' @noRd
tryCatch({

    # merge and add timestamp
    cosas_patients <- merge(
        x = cosas_patients_mapped,
        y = cosas_cartegenia[, .(umcgID, fetusStatus, twinStatus)],
        by = "umcgID",
        all.x = TRUE
    )[, dateLastUpdated := utils$timestamp()]


    # create object containing only familyIds by umcgId
    patientFamilyIDs <- cosas_patients[, .(umcgID, familyID)]

    cli::cli_alert_success("Built {.val cosas_patients}")

}, error = function(err) {
    cli::cli_alert_danger("Failed to build {.val cosas_patients}:\n{.val {err}}")

}, warning = function(warn) {
    cli::cli_alert_danger("Failed to build {.val cosas_patients}:\n{.val {warn}}")

})

# isolate new cases - use if you want to add fetus cases to the patients table
# new_cosas_cases <- cosas_bench_cnv_mapped[
#     !is.na(confirmedPhenotype) &
#     !umcgID %in% cosas_patients_mapped$umcgID &
#     !duplicated(umcgID),
#     .(
#         umcgID,
#         familyID,
#         biologicalSex,
#         maternalID,
#         fetusStatus,
#         twinStatus,
#         altPatientID
#     )
# ]
#
# rbind objects and join data of existing cases
# use if you want to add fetus cases to the patients table
# cosas_patients_base <- data.table::rbindlist(
#     list(cosas_patients_mapped, new_cosas_cases),
#     fill = TRUE
# )
#
# unite fetusStatus and twinStatus columns and set dateLastUpdated
# uncomment if fetus records should be added
# cosas_patients[, `:=`(
#     fetusStatus = paste(fetusStatus.x, fetusStatus.y, sep = "="),
#     twinStatus = paste(twinStatus.x, twinStatus.y, sep = "="),
#     fetusStatus.x = NULL,
#     fetusStatus.y = NULL,
#     twinStatus.x = NULL,
#     twinStatus.y = NULL
# )][, `:=`(
#     fetusStatus = gsub("((NA=)|(=NA)|(NA))", "", fetusStatus, perl = TRUE),
#     twinStatus = gsub("((NA=)|(=NA)|(NA))", "", twinStatus, perl = TRUE),
#     dateLastUpdated = utils$timestamp()
# )]


#' @title Create Cosas Clinical Events
#' @description create `cosas_clinical`
#' @section Methodology:
#'
#' All diagnostic related data is stored in `cosas_clinical`. This includes all
#' suspected- (or provisional), excluded-, and confirmed phenotypic observations.
#' confirmed phenotypic information is found in the cartegnia export. The rest of
#' the data will soon come from another source.
#'
#' Additionally, data should be filtered for patients that exist in the patients
#' table.
#'
#' @noRd
tryCatch({

    cosas_clinical <- merge(
        x = cosas_diagnoses_mapped[umcgID %in% patientFamilyIDs$umcgID, ],
        y = cosas_cartegenia[, .(umcgID, confirmedPhenotype)],
        by = "umcgID",
        all.x = TRUE
    )[, dateLastUpdated := utils$timestamp()]

    cli::cli_alert_success("Built {.val cosas_clinical}")

}, error = function(err) {
    cli::cli_alert_danger("Failed to build {.val cosas_clinical}:\n{.val {err}}")

}, warning = function(warn) {
    cli::cli_alert_danger("Failed to build {.val cosas_clinical}:\n{.val {warn}}")
})



#' @title Create Cosas Samples
#' @description create `cosas_samples`
#' @section Methodology:
#'
#' The table `cosas_samples` is created using a some data from the experiment
#' exports. The samples metadata export is already in good shape. There isn't
#' much that we need to add. The following code block merges the attributes
#' `familyID` from `cosas_patients` and creates the column `dateLastUpdated`,
#' as well as adds `labIndication` and `testDate` where applicable (from the
#' Darwin exports).
#'
#' `testID` is no longer included in this dataset as `testCode` is widely used
#' in the data export and `testID` is not always available.
#'
#' I would like to eventually convert the columns `labResultAvailability` and
#' `authorizedStatus` into a reference entity. However, I would like to
#' align with FairGenomes before doing so.
#'
#' @section Limitations:
#'
#' There is some loss when building the experiment tables. IDs that exist in
#' the Darwin exports do no exist in the ADLAS exports. This is described in
#' the subsequent sections.
#'
#' @noRd
tryCatch({

    # join familyIDs
    cosas_samples_base <- merge(
        x = cosas_samples_mapped[umcgID %in% patientFamilyIDs$umcgID],
        y = patientFamilyIDs,
        by = "umcgID",
        all.x = TRUE
    )

    # pull testDate and labIndication from Darwin extracts
    lab_metadata <- data.table::rbindlist(
        list(
            cosas_array_darwin_mapped[, .(umcgID, testCode, testDate, labIndication)],
            cosas_ngs_darwin_mapped[, .(umcgID, testCode, testDate, labIndication)]
        )
    )

    # merge lab metadata
    cosas_samples <- merge(
        x = cosas_samples_base,
        y = lab_metadata,
        by = c("umcgID", "testCode"),
        all.x = TRUE
    )[
        , dateLastUpdated := utils$timestamp()
    ][
        order(as.integer(umcgID))
    ]

    cli::cli_alert_success("Built {.val cosas_samples}")

}, error = function(err) {
    cli::cli_alert_danger("Failed to build {.val cosas_samples}:\n{.text {err}}")

}, warning = function(warn) {
    cli::cli_alert_danger("Failed to build {.val cosas_samples}:\n{.text {warn}}")

}, finally = {
    rm(list = c("cosas_samples_base", "lab_metadata"))

})


#' @title Create Cosas Labs Array
#' @description create `cosas_labs_array`
#' @section Methodology:
#'
#' The array experiment table contains metadata from ADLAS and Darwin. Both
#' objects contain all of the information that we require. To create this table,
#' I will run a simple left join.
#'
#' @section Limitations:
#'
#' There are still cases in the Darwin export that do not have matching records in
#' the ADLAS export. For now, I am only merge Darwin records that exist in the ADLAS
#' export. For more information, see the last section
#'
#' @noRd
tryCatch({

    # create base table
    labs_array_base <- merge(
        x = cosas_array_adlas_mapped,
        y = cosas_array_darwin_mapped,
        by = c("umcgID", "testCode"),
        all.x = TRUE
    )[
        order(as.integer(umcgID)),
        dateLastUpdated := utils$timestamp()
    ]

    # merge familyIDs
    cosas_labs_array <- merge(
        x = labs_array_base,
        y = patientFamilyIDs,
        by = "umcgID",
        all.x = TRUE
    )

    cli::cli_alert_success("Built {.val cosas_labs_array}")

}, error = function(err) {
    cli::cli_alert_danger("Failed to build {.val cosas_labs_array}:\n{.text {err}}")

}, warning = function(warn) {
    cli::cli_alert_danger("Failed to build {.val cosas_labs_array}:\n{.text {warn}}")

}, finally = {
    rm(list = c("labs_array_base"))
})


#' @title Create NGS Experiment Metadata
#' @description create `cosas_labs_ngs`
#' @section Methodology:
#'
#' Like the array experiment table, the NGS table is created using both the
#' ADLAS and Darwin exports. These tables are in pretty good shape as it is,
#' so there is much that needs to be done.
#'
#' @section Limitations:
#'
#' As well as the Array experiment table, the NGS table contains IDs that
#' do not exist in the array table. For now, Darwin data will be merged where
#' applicable (i.e., some records will be lossed)
#'
#' @noRd
tryCatch({

    # create base
    labs_ngs_base <- merge(
        x = cosas_ngs_adlas_mapped,
        y = cosas_ngs_darwin_mapped,
        by = c("umcgID", "testCode"),
        all.x = TRUE
    )[
        order(as.integer(umcgID)),
        dateLastUpdated := utils$timestamp()
    ]

    # merge familyIDs
    cosas_labs_ngs <- merge(
        x = labs_ngs_base,
        y = patientFamilyIDs,
        by = "umcgID",
        all.x = TRUE
    )

    cli::cli_alert_success("Built {.val cosas_labs_ngs}")
}, error = function(err) {
    cli::cli_alert_danger("Failed to build {.val cosas_labs_ngs}:\n{err}")

}, warning = function(warn) {
    cli::cli_alert_danger("Failed to build {.val cosas_labs_ngs}:\n{warn}")

}, finally = {
    rm(list = c("labs_ngs_base"))

})


#' @Title Identify Missing Lab Information
#' @description pull records that are in Darwin, but missing in ADLAS
#'
#' @section Methodology:
#'
#' While exploring the Darwin exports, it was discovered that there are records
#' that are present in Darwin but not in ADLAS. It should be that case that if
#' there records in Darwin they should also have matching records in ADLAS.
#' In the earlier sections (samples, Array, and NGS), I merged Darwin data only
#' if there is a matching record (umcgID and testCode).
#'
#' In order to validate the loss of data, the following code identifies the
#' missing cases and writes them to file for review.
#'
#' @noRd
# library2("dplyr")
#
# # find missing Array data: What's missing from the Adlas exports?
# missingArrayCases <- list(
#     umcgID = cosas_array_darwin_mapped %>%
#         filter(!umcgID %in% cosas_array_adlas_mapped$umcgID),
#     testCodes = cosas_array_darwin_mapped %>%
#         group_by(umcgID) %>%
#         filter(!testCode %in% cosas_array_adlas_mapped$testCode)
# )
#
# # find missing NGS data: What's missing from the Adlas exports?
# missingNgsCases <- list(
#     umcgID = cosas_ngs_darwin_mapped %>%
#         filter(!umcgID %in% cosas_ngs_adlas_mapped$umcgID),
#     testCodes = cosas_ngs_darwin_mapped %>%
#         group_by(umcgID) %>%
#         filter(!testCode %in% cosas_ngs_adlas_mapped$testCode)
# )
#
# # write to file
# wb <- openxlsx::createWorkbook()
# openxlsx::addWorksheet(wb, "array_missing_ids")
# openxlsx::addWorksheet(wb, "array_missing_tests")
# openxlsx::addWorksheet(wb, "ngs_missing_ids")
# openxlsx::addWorksheet(wb, "ngs_missing_tests")
# openxlsx::writeData(wb, "array_missing_ids", missingArrayCases$umcgID)
# openxlsx::writeData(wb, "array_missing_tests", missingArrayCases$testCodes)
# openxlsx::writeData(wb, "ngs_missing_ids", missingNgsCases$umcgID)
# openxlsx::writeData(wb, "ngs_missing_tests", missingNgsCases$testCodes)
# openxlsx::saveWorkbook(wb, "data/darwin_cases_missing_from_adlas.xlsx", TRUE)
