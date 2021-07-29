#' @title Clear REnvironment
#' @name clear
#' @description Remove all objects from the current environment
#' @noRd
clear <- function() {
    objs <- ls(envir = .GlobalEnv)
    rm(list = objs[objs != "clear"], envir = .GlobalEnv)
}


source("renv/activate.R")
