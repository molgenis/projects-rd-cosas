#'////////////////////////////////////////////////////////////////////////////
#' FILE: .Rprofile
#' AUTHOR: David Ruvolo
#' CREATED: 2021-08-16
#' MODIFIED: 2021-08-16
#' PURPOSE: set global functions and load renv
#' STATUS: working
#' PACKAGES: NA
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////


#' @title Clear
#' @name clear
#' @description clear the active terminal
#' @noRD
clear <- function() {
    cmds <- list("unix" = "clear", "windows" = "cls")
    system(cmds[[.Platform$OS.type]])
}


#' @title Remove2
#' @name rm2
#' @description Force remove all objects from the current environment
#' @noRd
rm2 <- function() {
    ignore <- c("clear", "library2", "rm2")
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
