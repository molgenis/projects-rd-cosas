#'////////////////////////////////////////////////////////////////////////////
#' FILE: utils_benchmarks.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-08-17
#' MODIFIED: 2021-08-17
#' PURPOSE: benchmarks for cosas mappings
#' STATUS: working
#' PACKAGES: microbenchmarks
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////


source("R/_load.R")
source("R/utils_mapping.R")


#' Map Objects into COSAS Terminology
cli::cli_alert_info("Mapping portal data objects into COSAS terminology")
bmrk <- microbenchmark::microbenchmark(
    mappings$patients(portal_patients),
    mappings$diagnoses(portal_diagnoses),
    mappings$samples(portal_samples),
    mappings$array_adlas(portal_array_adlas),
    mappings$array_darwin(portal_array_darwin),
    mappings$ngs_adlas(portal_ngs_adlas),
    mappings$ngs_darwin(portal_ngs_darwin),
    mappings$bench_cnv(portal_bench_cnv),
    times = 10
)