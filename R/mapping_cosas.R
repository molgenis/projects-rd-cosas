#' ////////////////////////////////////////////////////////////////////////////
#' FILE: cosas_mapping.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-07-22
#' MODIFIED: 2021-08-18
#' PURPOSE: Mapping portal tables to main pkg
#' STATUS: working
#' PACKAGES: data.table, purrr, dplyr, tidyr
#' COMMENTS: NA
#' ////////////////////////////////////////////////////////////////////////////

library2("data.table")
source("R/_load.R")
source("R/utils_mapping.R")


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

rm(list = c(
    "portal_patients", "portal_diagnoses", "portal_samples",
    "portal_array_adlas", "portal_array_darwin", "portal_ngs_adlas",
    "portal_ngs_darwin", "portal_bench_cnv"
))

#'//////////////////////////////////////


cli::cli_alert_info("Building COSAS tables...")


#' @title Create COSAS Patients
#' @description create `cosas_patients`
#' @section Methodology:
#'
#' `cosas_patients` is created from `cosas_patients_mapped` and
#' `cosas_bench_cnv_mapped`. This object is created by binding new records
#' from bench_cnv and joining metadata for existing records (i.e., patients).
#'
#' Using the mapping CNV dataset, find records that do not exist in
#' `cosas_patients_mapped`. Grab metadata for unique cases and bind them
#' to the patients dataset.
#'
#' For records that do exist, merge metadata into patients. Since most metadata
#' is present in the data extracts and applies to records that are fetuses,
#' merge `fetusStatus` and `twinStatus`. These will always be FALSE, but it is
#' import to merge this data anyways.
#'
#' It is not possible to reliably -- or accurately -- calculate date of first
#' consult using dateCreated or other data columns. If this is required, this
#' information should be requested.
#'
#' @noRd

# isolate new cases
new_cosas_cases <- cosas_bench_cnv_mapped[
    !umcgID %in% cosas_patients_mapped$umcgID & !duplicated(umcgID),
    .(
        umcgID,
        familyID,
        biologicalSex,
        maternalID,
        fetusStatus,
        twinStatus,
        altPatientID
    )
]

# isolate existing cases
existing_cosas_cases <- cosas_bench_cnv_mapped[
    umcgID %in% cosas_patients_mapped$umcgID & !duplicated(umcgID),
    .(umcgID, fetusStatus, twinStatus)
]

# rbind objects and join data of existing cases
cosas_patients_base <- data.table::rbindlist(
    list(cosas_patients_mapped, new_cosas_cases),
    fill = TRUE
)

cosas_patients <- merge(
    x = cosas_patients_base,
    y = existing_cosas_cases,
    by = "umcgID",
    all.x = TRUE
)

# unite fetusStatus and twinStatus columns and set dateLastUpdated
cosas_patients[, `:=`(
    fetusStatus = paste(fetusStatus.x, fetusStatus.y, sep = "="),
    twinStatus = paste(twinStatus.x, twinStatus.y, sep = "="),
    fetusStatus.x = NULL,
    fetusStatus.y = NULL,
    twinStatus.x = NULL,
    twinStatus.y = NULL
)][, `:=`(
    fetusStatus = gsub("=NA", "", fetusStatus),
    twinStatus = gsub("=NA", "", twinStatus),
    dateLastUpdated = utils$timestamp()
)]


rm(list = c("new_cosas_cases", "existing_cosas_cases", "cosas_patients_base"))


# create object containing only familyIds by umcgId
patientFamilyIDs <- cosas_patients[, .(umcgID, familyID)]


#' @title Create Cosas Clinical Events
#' @description create `cosas_clinical`
#' @section Methodology:
#'
#' All diagnostic information is stored in `cosas_clinical`. The purpose is
#' to preserve the structure of the diagnostic data export. This dataset is
#' structured in long format. This means that each row is a unique diagnosis
#' per patient. It is important to preserve this structure as all diagnoses
#' are also given a certainty rating.
#'
#' In order to build the dataset, all rows that were missing values across
#' all columns (expected for umcgID) were removed. A subset of the benchCNV
#' dataset containing the phenotypic data was created, and then bound
#' to the initial clinical data.table. Lastly, familyID was merged from
#' `cosas_patients` and timestamps were generated.
#'
#' @noRd
#'

# create base `cosas_clinical` data.table
cosas_clinical_base <- cosas_diagnoses_mapped[,
    isNA := is.na(clinicalDiagnosis) &
    is.na(clinicalDiagnosisCertainty) &
    is.na(secondaryDiagnosis) &
    is.na(secondaryDiagnosisCertainty) &
    is.na(dateOfDiagnosis) &
    is.na(ondID)
][isNA %like% FALSE][, `:=`(isNA = NULL, observedPhenotype = NA_character_)]


# gather observedPhenotype and dateOfDiagnosis from benchCNV
new_clinical_data <- cosas_bench_cnv_mapped[
    , .(umcgID, observedPhenotype, dateOfDiagnosis)
][
    , isNA := is.na(observedPhenotype) & is.na(dateOfDiagnosis)
][isNA %like% FALSE][, isNA := NULL]


# bind tables
cosas_clinical_bound <- data.table::rbindlist(
    l = list(cosas_clinical_base, new_clinical_data),
    fill = TRUE
)


# join familyID
cosas_clinical <- merge(
    x = cosas_clinical_bound,
    y = cosas_patients[, .(umcgID, familyID)],
    by = "umcgID",
    all.x = TRUE
)[, dateLastUpdated := utils$timestamp()]


rm(list = c("cosas_clinical_base", "new_clinical_data", "cosas_clinical_bound"))


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
#' align with FairGenomes.
#'
#' @section Limitations:
#' There is some loss when building the experiment tables. IDs that exist in
#' the Darwin exports do no exist in the ADLAS exports. This is described in
#' the subsequent sections.
#'
#' @noRd

# join familyIDs
cosas_samples_base <- merge(
    x = cosas_samples_mapped,
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
)[order(as.integer(umcgID))]


# add dateLastUpdated
cosas_samples[, dateLastUpdated := utils$timestamp()]

rm(list = c("cosas_samples_base", "lab_metadata"))


#' @title Create Cosas Labs Array
#' @description create `cosas_labs_array`
#' @section Methodology:
#'
#' The array experiment table contains metadata from ADLAS and Darwin. Both
#' objects contain all of the information that we require. To create this table,
#' I will run a simple left join.
#'
#' @section Limitations:
#' There are still cases in the Darwin export that do not have matching records in
#' the ADLAS export. For now, I am only merge Darwin records that exist in the ADLAS
#' export. To find these cases, run the following commands.
#'
#' cosas_array_darwin_mapped %>%
#'     filter(!umcgID %in% cosas_array_adlas_mapped)
#'
#' cosas_array_darwin_mapped %>%
#'    group_by(umcgID) %>%
#'    filter(!testCode %in% cosas_array_darwin_mapped$testCode)
#'
#' @noRd

# create base table
lab_array_base <- merge(
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
    x = lab_array_base,
    y = patientFamilyIDs,
    by = "umcgID",
    all.x = TRUE
)


rm(list = c("lab_array_base"))


#' @title Create NGS Experiment Metadata
#' @description create `cosas_labs_ngs`
#' @section Methodology:
#'
#' Like the array experiment table, the NGS table is created using both the
#' ADLAS and Darwin exports. These tables are in pretty good shape as it is,
#' so there is much that needs to be done.
#'
#' @section Limitations:
#' As well as the Array experiment table, the NGS table contains IDs that
#' do not exist in the array table. For now, Darwin data will be merged where
#' applicable (i.e., some records will be lossed)
#'
#' cosas_ngs_darwin_mapped %>%
#'     filter(!umcgID %in% cosas_ngs_adlas_mapped$umcgID)
#'
#' @noRd

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

#'//////////////////////////////////////

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