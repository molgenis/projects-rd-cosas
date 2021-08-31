#'////////////////////////////////////////////////////////////////////////////
#' FILE: viz_sorta.R
#' AUTHOR: David Ruvolo
#' CREATED: 2021-08-31
#' MODIFIED: 2021-08-31
#' PURPOSE: explore SORTA matches
#' STATUS: in.progress
#' PACKAGES: data.table
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////


# pkgs
library2("ggplot2")

# export data from Molgenis
sorta <- data.table::fread(file = "./data/sorta_cineas_hpo_mappings.csv")


p <- ggplot(sorta, aes(x = round(score, 0))) +
    geom_histogram(bins = 50, fill = "#160F29") +
    scale_x_continuous(
        breaks = seq(0, 100, by = 5),
        expand = expansion(mult = c(.1, 0))
    ) +
    scale_y_continuous(
        breaks = c(seq(0, 80, by = 5)),
        expand = expansion(mult = c(0, 0.1))
    ) +
    labs(
        title = "COSAS Cineas to HPO Mappings",
        subtitle = "Distribution of SORTA similarity scores (n = 867)",
        caption = "Threshold: 100%; Matched: 75; Unmatched: 792",
        x = NULL,
        y = "Frequency"
    ) +
    theme_classic()

ggplot2::ggsave("sorta_similarity_scores_distibutions.png", p, device = "png")
