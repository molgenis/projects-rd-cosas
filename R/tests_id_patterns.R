

suppressPackageStartupMessages(library(dplyr))

d <- readxl::read_xlsx(
    path = "data/cosasportal/cosasportal_bench_cnv.xlsx",
    col_types = "text"
)

d$ftype <- NA

split_by <- function(value, split) {
    x <- unlist(strsplit(value, paste0("(?<=.)(?=", split, ")"), perl = TRUE))[2]
    if (grepl("(-|_|=)", x)) {
        x <- unlist(strsplit(x, "(?<=[-_=])", perl = TRUE))[1]
        x <- gsub("(-|_|=)", "", x)
    }
    return(x)
}


for (i in seq_len(NROW(d))) {
    if (grepl("F", d$primid[i])) {
        d$ftype[i] <- split_by(d$primid[i], "F")
    }
    if (grepl("A", d$primid[i])) {
        d$ftype[i] <- split_by(d$primid[i], "A")
    }
    if (grepl("Tx", d$primid[i])) {
        d$ftype[i] <- split_by(d$primid[i], "Tx")
    }
}

splittypes <- d %>% group_by(ftype) %>% count() %>% arrange(-n)
splittypes %>% as.data.frame() %>% arrange(ftype)

splittypes %>%
    arrange(ftype) %>%
    rename("pattern" = ftype, "count" = n) %>%
    knitr::kable()

splittypes %>% filter(!is.na(ftype)) %>% pull(n) %>% sum()