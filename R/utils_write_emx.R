#' write emx
#'
#' @param model a parsed yml object
#'
#' @export
write_emx <- function(model, out_dir, file_gets_pkg_name = TRUE) {

    if (substring(out_dir, nchar(out_dir)) != "/") {
        out_dir <- paste0(out_dir, "/")
    }

    basepath <- out_dir
    if (isTRUE(file_gets_pkg_name)) {
        basepath <- paste0(basepath, attr(model, "package"), "_")
    }

    for (m in seq_len(length(model))) {
        if (names(model[m]) == "packages") {
            readr::write_csv(
                x = model[[m]],
                file = paste0(out_dir, "/sys_md_Package.csv"),
                na = ""
            )
        } else if (names(model[m]) == "entities") {
            readr::write_csv(
                x = model[[m]],
                file = paste0(basepath, "entities.csv"),
                na = ""
            )
        } else if (names(model[m]) == "attributes") {
            readr::write_csv(
                x = model[[m]],
                file = paste0(basepath, "attributes.csv"),
                na = ""
            )
        } else {
            readr::write_csv(
                x = model[[m]],
                file = paste0(out_dir, "/", names(model[m]), ".csv"),
                na = ""
            )
        }
    }
}