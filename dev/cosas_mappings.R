#'////////////////////////////////////////////////////////////////////////////
#' FILE: cosas_mappings.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-03-03
#' MODIFIED: 2021-03-03
#' PURPOSE: create mappings from COSAS to FairGenomes
#' STATUS: in.progress
#' PACKAGES: NA
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////


suppressPackageStartupMessages(library(dplyr))


inclusionstatus <- list(
    fg = readr::read_tsv(
        file = "data/fairgenomes/personal_inclusionstatus.tsv",
        col_types = readr::cols()
    ) %>%
        select(fg_id = value),
    cosas = readr::read_tsv(
        file = "data/cosas/cosas_patients.tsv",
        col_types = readr::cols()
    ) %>%
        select(cosas_id = overleden) %>%
        distinct(cosas_id)
)

inclusionstatus$mapping <- inclusionstatus$fg %>%
    mutate(
        cosas_overleden = case_when(
            fg_id == "Alive" ~ "nee",
            fg_id == "Dead" ~ "ja",
            fg_id == "Lost in follow-up" ~ "withdrawn",
            fg_id == "Opted-out" ~ "declined",
            fg_id == "NoInformation (NI, nullflavor)" ~ "no.info",
            fg_id == "Invalid (INV, nullflavor)" ~ "invalid",
            fg_id == "Derived (DER, nullflavor)" ~ "derived",
            fg_id == "Other (OTH, nullflavor)" ~ "other",
            fg_id == "Negative infinity (NINF, nullflavor)" ~ "neg.infinity",
            fg_id == "Positive infinity (PINF, nullflavor)" ~ "pos.infinity",
            fg_id == "Un-encoded (UNC, nullflavor)" ~ "decoded",
            fg_id == "Masked (MSK, nullflavor)" ~ "encoded",
            fg_id == "Not applicable (NA, nullflavor)" ~ "NA",
            fg_id == "Unknown (UNK, nullflavor)" ~ "uknown",
            fg_id == "Asked but unknown (ASKU, nullflavor)" ~ "asked.declined",
            fg_id == "Temporarily unavailable (NAV, nullflavor)" ~ "temp.unavailable",
            fg_id == "Not asked (NASK, nullflavor)" ~ "not.collected",
            fg_id == "Not available (NAVU, nullflavor)" ~ "unavailable",
            fg_id == "Sufficient quantity (QS, nullflavor)" ~ "sufficient",
            fg_id == "Trace (TRC, nullflavor)" ~ "trace",
        )
    ) %>%
    select(cosas_overleden, fg_id)

readr::write_tsv(
    x = inclusionstatus$mapping,
    file = "data/cosas-mappings/cosasmaps_inclusionStatus.tsv"
)
