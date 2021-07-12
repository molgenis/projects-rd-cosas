#'////////////////////////////////////////////////////////////////////////////
#' FILE: gene_list.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-07-09
#' MODIFIED: 2021-07-12
#' PURPOSE: load gene file and generate gene list reference dataset
#' STATUS: working
#' PACKAGES: NA
#' COMMENTS: This script is intended for initial COSAS setup only
#'////////////////////////////////////////////////////////////////////////////


# pkgs
suppressPackageStartupMessages(library(dplyr))
source("R/utils_molgenis.R")


# set env vars
# Sys.setenv("molgenis_username" = "")
# Sys.setenv("molgenis_password" = "")


# connect to molgenis
m <- molgenis$new(host = "https://cosas-acc.gcc.rug.nl")
m$login(
    username = Sys.getenv("molgenis_username"),
    password = Sys.getenv("molgenis_password")
)

# pull initial data from reference entity
coderefs <- m$get(table = "cosasrefs_test_codes", attrs = "id,code,description")


#'//////////////////////////////////////

#' ~ 1 ~
#' COLLATE DATE
#' Using the gene list file, collate all test codes and genes into a single
#' data object. that lists testcodes, descriptions, and a list of genes.
#' Since the genes per test code are stored on separate sheets, we need to
#' loop through and extract data sheet-by-sheet.


# pull first sheet
testcodes <- readxl::read_xlsx(
        path = "data/gene_list.xlsx",
        sheet = "Actieve Testcodes"
    )


# get a list of sheetnames
sheetnames <- readxl::excel_sheets(path = "data/gene_list.xlsx") %>%
    .[. != "Actieve Testcodes"]


# extract gene lists from sheets
main <- as_tibble(sapply(c("id", "genes"), function(x) character()))
for (name in sheetnames) {
    cli::cli_alert_info("Processing sheet {.val {name}}")
    raw <- readxl::read_xlsx(
        path = "data/gene_list.xlsx",
        sheet = name,
        col_names = "genes"
    ) %>%
    pull(genes) %>%
        paste0(., collapse = ", ") %>%
        as_tibble() %>%
        rename("genes" = value) %>%
        mutate(id = name) %>%
        select(id, genes)
    main <- main %>% bind_rows(., raw)
}


# merge panel metadata with genes
df <- main %>%
    left_join(
        testcodes %>% select(-Panel),
        by = c("id" = "Testcode")
    ) %>%
    mutate(id = tolower(id))


new_coderefs <- coderefs %>% left_join(df, by = "id")

m$prep(new_coderefs) %>%
    m$push(table = "cosasrefs_test_codes", x = .)

# optional write codes to files
# wb <- openxlsx::createWorkbook()
# openxlsx::addWorksheet(wb, sheetName = "testcodes-genes")
# openxlsx::writeData(wb, "testcodes-genes", df)
# openxlsx::saveWorkbook(wb, "data/genes_by_testcode.xlsx", overwrite = TRUE)
