#' write emx
#'
#' @param model a parsed yml object
#'
#' @export
write_emx <- function(model) {
    for (m in seq_len(length(model))) {
        if (names(model[m]) == "packages") {
            readr::write_tsv(
                x = model[[m]],
                file = "emx/sys_md_Package.tsv"
            )
        } else if (names(model[m]) == "entities") {
            readr::write_tsv(
                x = model[[m]],
                file = "emx/cosas_entities.tsv"
            )
        } else if (names(model[m]) == "attributes") {
            d <- model[[m]]
            entities <- unique(d$entity)
            for (e in seq_len(length(entities))) {
                t <- d[d$entity == entities[e], ]
                readr::write_tsv(
                    x = t,
                    file = paste0(
                        "emx/cosas_",
                        entities[e],
                        "_attributes.tsv"
                    ),
                    na = ""
                )
            }
        } else {
            readr::write_tsv(
                x = model[[m]],
                file = paste0("emx/", names(model[m]), ".tsv")
            )
        }
    }
}