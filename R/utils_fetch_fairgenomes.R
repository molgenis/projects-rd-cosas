#'////////////////////////////////////////////////////////////////////////////
#' FILE: utils_fetch_fairgenomes.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-07-14
#' MODIFIED: 2021-07-14
#' PURPOSE: Script for fetching various FG modules
#' STATUS: in.progress
#' PACKAGES: NA
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

# nolint start
base <- "https://raw.githubusercontent.com/fairgenomes/fairgenomes-semantic-model/main/lookups/"
# nolint end

# read Phenotypes
d <- read.delim(
    file = paste0(base, "Phenotypes.txt"),
    sep = "\t",
    colClasses = rep("character", 5)
)

readr::write_csv(
    x = d,
    file = "data/fairgenomes/cosasrefs_phenotype.csv"
)
