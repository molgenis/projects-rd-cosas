#' yaml_to_emx
#'
#' extract all emx data
#'
#' @param path string containing the path to a yml file
#' @param ... arguments to pass down to `yaml::read_yaml`
#'
#' @export
yml_to_emx <- function(path, attr_entity_has_pkg = FALSE, ...) {
    yaml <- yaml::read_yaml(path, ...)

    # init main emx object
    data <- structure(
        list(
            packages = pull_pkg(yaml),
            entities = data.frame(),
            attributes = data.frame()
        ),
        class = "emx.list",
        package = yaml[["name"]]
    )

    # pull data and attributes by entity
    for (d in seq_len(length(yaml[["entities"]]))) {

        # isoloate entity and pull metadata
        entity <- yaml[["entities"]][[d]]
        .meta <- list(
            entity = entity[["name"]],
            pkg_entity = paste0(attr(data, "package"), "_", entity[["name"]])
        )

        # extract entity attributes
        data[["attributes"]] <- dplyr::bind_rows(
            data[["attributes"]],
            pull_attributes(
                entity = entity,
                pkg_name = data$package$name,
                attr_entity_has_pkg = attr_entity_has_pkg
            )
        )

        # likely a file path
        if (length(entity[["data"]]) == 1) {
            data[[.meta$pkg_entity]] <- entity[["data"]][[1]]
        }

        # likely a dataset
        if (length(entity[["data"]]) > 1) {
            data[[.meta$pkg_entity]] <- pull_data(entity = entity)
        }

        # lastly, bind entitiy objects to main object
        # pull variables that are valid EMX attributes
        data[["entities"]] <- dplyr::bind_rows(
            data$entities,
            entity[!names(entity) %in% c("attributes", "data")]
        )
    }

    # if defined, apply null/na flavors
    if (length(yaml$defaults) > 0) {
        data$attributes <- apply_defaults(
            data = data$attributes,
            options = yaml$defaults
        )
    }

    # append pkg name to entities
    data[["entities"]][["package"]] <- attr(data, "package")

    return(data)
}

#' pull_pkg
#'
#' Extact package information based on known pkg attributes
#'
#' @param yaml a yaml object
#'
#' @noRd
pull_pkg <- function(yaml) {
    d <- yaml[names(yaml) %in% emx[["packages"]][["names"]]]
    data.frame(d)
}

#' convert.pull_attributes
#'
#' Pull entity attributes
#'
#' @param entity an entity from a yaml object
#' @param pkg_name name of the package
#' @param attr_entity_has_pkg if TRUE, attr entities values will be printed
#'         as `pkg_entity`
#'
#' @noRd
pull_attributes <- function(entity, pkg_name, attr_entity_has_pkg) {
    out <- data.frame()
    if (length(entity[["attributes"]])) {
        for (n in seq_len(length(entity[["attributes"]]))) {
            df <- data.frame(entity[["attributes"]][n])
            if (attr_entity_has_pkg) {
                df$entity <- paste0(pkg_name, "_", entity[["name"]])
            } else {
                df$entity <- paste0(entity[["name"]])
            }
            out <- dplyr::bind_rows(out, df)
        }
    }
    return(out)
}

#' convert.pull_data
#'
#' Ideally, data should be located in a separate file. However,
#' if data is present in the yaml file, extract data and save to file.
#'
#' @param entity an entity from a yaml object
#'
#' @noRd
pull_data <- function(entity) {
    out <- data.frame()
    for (n in seq_len(length(entity[["data"]]))) {
        df <- data.frame(entity[["data"]][n])
        out <- dplyr::bind_rows(out, df)
    }
    return(out)
}

#' convert.apply_defaults
#'
#' extract yaml options and apply them where applicable
#'
#' @param data the attributes object
#' @param options yaml$options output
#'
#' @noRd
apply_defaults <- function(data, options) {
    for (n in seq_len(NCOL(data))) {
        if (names(data[n]) %in% names(options)) {
            pos <- match(names(data[n]), names(options))
            data[n] <- tidyr::replace_na(data[n], options[pos])
        }
    }
    return(data)
}

#' EMX data structures
#'
#' Create a list of attributes for validating user input
#'
#' @noRd
emx <- list()


#' emx packages
emx$packages <- data.frame(
    names = c(
        "name",
        "label",
        "description",
        "parent",
        "tags"
    )
)

#' EMX valid attribute variables
#'
#' Available column names for attribute data structures. Variables `label`
#' and `description` can have many columns dependening on languages used
#'
#' @noRd
emx$attributes <- data.frame(
    names = c(
        "entity",         # required attributes
        "name",           # required attributes
        "dataType",
        "refEntity",
        "nillable",
        "idAttribute",
        "auto",
        "description",
        "description-",  # can have multiple columns for languages
        "rangeMin",
        "rangeMax",
        "lookupAttribute",
        "label",
        "label-",  # can have multiple columns for language
        "aggregateable",
        "labelAttribute",
        "readOnly",
        "tags",
        "validationExpression",
        "visible",
        "defaultValue",
        "partOfAttribute",
        "expression"
    )
)


#' Emx entities
#' @noRd
emx$entites <- data.frame(
    names = c(
        "entity",  # required
        "extends",
        "package",
        "abstract",
        "description",
        "backend",
        "tags"
    )
)


#' emx_datatypes
#' @noRd
emx$datatypes <- data.frame(
    names  = c(
        "bool",
        "categorical",
        "categorical_mref",
        "compound",
        "date",
        "datetime",
        "decimal",
        "email",
        "enum",
        "file",
        "hyperlink",
        "int",
        "long",
        "mref",
        "one_to_many",
        "string",
        "text",
        "xref"
    )
)

#' emx_tags
#' @noRd
emx$tags <- data.frame(
    names = c(
        "identifier",
        "label",
        "objectIRI",
        "relationLabel",
        "relationIRI",
        "codeSystem"
    )
)