#' @title Clear Environment
#' @name clear
#' @description Force remove all objects from the current environment
#' @noRd
clear <- function() {
    ignore <- c("clear", "library2")
    rm(list = setdiff(ls(envir = .GlobalEnv), ignore), envir = .GlobalEnv)
}

#' @title Quietly Load Package
#' @name library2
#' @description suppress messages when loading a package
#' @param pkg the name of the package
#' @noRd
library2 <- function(pkg) {
    suppressPackageStartupMessages(library(pkg, character.only = TRUE))
}

# start renv: make sure this is always last!
source("renv/activate.R")
