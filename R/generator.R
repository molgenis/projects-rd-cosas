#' @title
#' Generate Dataset
#'
#' @description
#' Generate a samples dataset that creates data on patients, diagnostics,
#' samples, and analysis
#'
#' @exportClass
generator <- R6::R6Class(,
    classname = "Generator",
    public = list(
        #' @field n the number of cases to generate
        n = NA,
        patient_id_length = NA,
        family_id_length = NA,
        patient_visits_n = NA,
        patient_visits_prob = NA,

        #' @field id_prefix a string to concat to each generated ID
        id_prefix = NA,

        #' @field data returned data object
        data = structure(list(), class = "random.data"),

        #' @title initialize
        #' @param n the number of records to generate
        initialize = function(
            n = 100,
            patient_visits = 1,
            patient_id_length = 8,
            family_id_length = 8
        ) {
            self$n <- n
            self$patient_id_length <- patient_id_length
            self$family_id_length <- family_id_length

            if (patient_visits > 5 | patient_visits < 1) {
                stop("Number of patient visits must be less than 5")
            }

            p <- c(0.3, 0.3, 0.25, 0.10, 0.05)
            self$patient_visits_n <- patient_visits
            self$patient_visits_prob <- p[1:patient_visits]
        },

        #' @title randomize data
        random_dataset = function() {
            self$data$ids <- private$rand_patient_id(n = self$n)
            self$data$patients <- private$build_patient_table()
            self$data$samples <- private$build_samples_table()
            self$data$analysis <- private$build_analysis_table()
        }
    ),
    private = list(

        # define params, patterns, and ranges for generating the data
        params = list(
            bool = c(TRUE, FALSE, NA_character_),
            sex = c("vrouw", "man"), # genetic
            dob = c(
                min = as.Date("1932-01-01"),
                max = as.Date("2014-08-31")
            ),
            visits = c(
                min = as.Date("2017-01-01"),
                max = as.Date("2021-01-01")
            ),

            # aandoening
            hpo_terms = c(
                "DYST", # "Dystonie",
                "DER", # "Dermatologie",
                "cyto3", # "SNP-Array",
                "EXOOM", # "targeted exoom",
                "5GPM" # "DNA snel diagnostiek"
            ),
            lab_indicatie = c(
                "DI", #"Diagnostisch",
                "DR", #"Dragerschap",
                "INF", #"Informatief",
                "R" #"Research"
            ),
            experiment = c(
               "NGS targeted Exoom",
               "SNP"
            ),
            mutation = c(
                "Niet afwijkend",  # no mutation found
                "Afwijkend"        # mutation found
            )
        ),

        # generate a string that resembles a UMCG ID
        rand_patient_id = function(n) {
            as.character(
                sapply(seq_len(n), function(x) {
                    paste(
                        stringi::stri_rand_strings(
                            n = 1,
                            length = 2,
                            pattern = "[0-9]"
                        ),
                        stringi::stri_rand_strings(
                            n = 1,
                            length = 2,
                            pattern = "[0-9]"
                        ),
                        stringi::stri_rand_strings(
                            n = 1,
                            length = 3,
                            pattern = "[0-9]"
                        ),
                        sep = "."
                    )
                })
            )
        },

        rand_numeric_id = function(n, length = 8) {
            stringi::stri_rand_strings(
                n = n,
                length = length,
                pattern = "[0-9]"
            )
        },

        # using the array of random IDs, create random patient data
        build_patient_table = function() {
            self$data$ids %>%
                tibble::as_tibble(.) %>%
                dplyr::rename(umcg_numr = value) %>%
                dplyr::mutate(
                    # UMCG internal ID - Family ID
                    familie_numr = private$rand_numeric_id(n = self$n),
                    # dob
                    geboortedatum = as.Date(
                        purrr::rdunif(
                            n = self$n,
                            a = as.integer(private$params$dob[1]),
                            b = as.integer(private$params$dob[2])
                        ),
                        origin = "1970-01-01"
                    ),
                    # age - age today
                    leeftijd = round(
                        as.numeric(
                            ((Sys.Date() - geboortedatum) / 365.25)
                        ),
                        digits = 2
                    ),
                    # sex
                    geslacht = sample(
                        x = private$params$sex,
                        size = self$n,
                        replace = TRUE
                    ),
                    overleden = dplyr::case_when(
                        leeftijd >= 65 ~ sample(
                            x = c("ja", "nee", "not.collected", "temp.unavailable"),
                            size = 1,
                            replace = TRUE,
                            prob = c(0.3, 0.5, 0.1, 0.1)
                        ),
                        TRUE ~ "nee"
                    )
                )
        },

        # create samples tables based on the params n (total patients) and
        # visits (i.e., the number of times a patient visited the clinic)
        build_samples_table = function() {
            d <- purrr::map(self$data$ids, function(.x) {
                i <- sample(
                    x = 1:self$patient_visits_n,
                    size = 1,
                    prob = self$patient_id_length_prob
                )
                time <- data.frame(
                    umcg_numr = .x,
                    aanvraagdatum = as.Date(
                        purrr::rdunif(
                            n = i,
                            a = as.integer(as.Date("2017-01-01")),
                            b = as.integer(as.Date("2021-01-01"))
                        ),
                        origin = "1970-01-01"
                    ),
                    analyse = paste0(
                        "NX",
                        private$rand_numeric_id(n = i, length = 3)
                    ),
                    dna_numr = paste0(
                        "DNA",
                        private$rand_numeric_id(n = i, length = 6)
                    ),
                    lab_indicatie = sample(
                        x = private$params$lab_indicatie,
                        size = 1,
                        replace = TRUE,
                        prob = c(0.95, 0.2, 0.1, 0.1)
                    ),
                    aandoening = sample(
                        x = private$params$hpo_terms,
                        size = 1,
                        replace = TRUE
                    ),
                    advisevraag_uitslagcode = sample(
                        x = private$params$mutation,
                        size = 1,
                        replace = TRUE,
                        prob = c(0.65, 0.35)
                    )
                )

                # for each visit, generate a random ID and generate visit
                # number
                time %>%
                    dplyr::group_by(umcg_numr) %>%
                    dplyr::arrange(aanvraagdatum) %>%
                    dplyr::mutate(
                        bezoek_numr = private$rand_numeric_id(n = NROW(time)),
                        bezoek = seq_len(length(aanvraagdatum))
                    ) %>%
                    dplyr::ungroup() %>%
                    dplyr::select(
                        umcg_numr,
                        aanvraagdatum,
                        bezoek_numr,
                        bezoek,
                        dplyr::everything()
                    )
            })

            d <- dplyr::bind_rows(d)

            # bind date entered into 'system'
            self$data$patients <- d %>%
                dplyr::group_by(umcg_numr) %>%
                dplyr::filter(bezoek == 1) %>%
                dplyr::select(umcg_numr, aanvraagdatum) %>%
                dplyr::left_join(g$data$patients, ., by = "umcg_numr") %>%
                dplyr::mutate(
                    aanvraagdatum = dplyr::case_when(
                        !is.null(aanvraagdatum) ~ as.Date(
                            aanvraagdatum + sample(
                                x = 0:2,
                                size = 1,
                                prob = c(0.55, 0.35, 0.1)
                            )
                        )
                    )
                ) %>%
                dplyr::rename(invoerdatum = aanvraagdatum)

            d
        },

        # generate analysis table
        build_analysis_table = function() {
            self$data$samples %>%
                dplyr::select(
                    umcg_numr, aanvraagdatum, bezoek_numr, analyse, dna_numr
                ) %>%
                dplyr::left_join(
                    self$data$patients %>%
                        dplyr::select(umcg_numr, familie_numr),
                    .,
                    by = "umcg_numr"
                ) %>%
                dplyr::mutate(
                    soort_experiment = sample(
                        x = private$params$experiment,
                        size = length(umcg_numr),
                        replace = TRUE
                    ),
                    design_numr = "AllExonV7",
                    expr_numr = "HSR347A",

                    # file name - missing onderzoeksnr
                    filenaam = paste(
                        analyse,
                        familie_numr,
                        umcg_numr,
                        dna_numr,
                        expr_numr,
                        design_numr,
                        sep = "_"
                    )
                )
        }
    )
)
