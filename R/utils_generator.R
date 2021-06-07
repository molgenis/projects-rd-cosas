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

        #' @field n_samples number of samples to generate per patient 1-5
        n_samples = NA,

        #' @field patient_visits_pro
        n_samples_prob = NA,

        #' @field data returned data object
        data = structure(list(), class = "random.data"),

        #' @title initialize
        #' @param n the number of records to generate
        initialize = function(
            n = 100,
            n_samples = 1,
            patient_visits = 1
        ) {
            private$params$n <- n

            if (patient_visits > 5 | patient_visits < 1) {
                stop("Number of patient samples must be less than 5")
            }

            p <- c(0.3, 0.3, 0.25, 0.10, 0.05)
            private$params$n_samples <- patient_visits
            private$params$n_samples_prob <- p[1:patient_visits]
        },

        #' @title randomize data
        random_dataset = function() {
            self$data$ids <- private$rand_patient_id(n = private$params$n)
            self$data$patients <- private$build_patient_table()
            self$data$samples <- private$build_samples_table()
            self$data$labinfo <- private$build_labinfo_table()
            self$data$files <- private$build_files_table()
        }
    ),
    private = list(

        # define params, patterns, and ranges for generating the data
        params = list(
            n = NA,
            n_samples = NA,
            n_samples_prob = NA,
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
            lab_incidation = c(
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
            ),
            filetypes = list(
                ngs = tibble::tribble(
                    ~format, ~ext,
                    "vcf", "GAVIN.rlv.vcf.gz",
                    "gvcf", "batch-1.variant.calls.g.vcf.gz",
                    "gvcf.tbi",  "batch-1.variant.calls.g.vcf.gz.tbi",
                    "bam", "merged.dedup.bam",
                    "bam.bai", "merged.dedup.bam.bai",
                    "cram", "merged.dedup.bam.cram",
                    "cram.bai", "merged.dedup.bam.cram.crai"
                )#,
                # snp = tibble::tribble(
                #     ~format, ~ext,
                #     ""
                # )
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
                    family_numr = private$rand_numeric_id(n = private$params$n),
                    # dob
                    dob = as.Date(
                        purrr::rdunif(
                            n = private$params$n,
                            a = as.integer(private$params$dob[1]),
                            b = as.integer(private$params$dob[2])
                        ),
                        origin = "1970-01-01"
                    ),
                    # # age - age today
                    age = round(
                        as.numeric(
                            ((Sys.Date() - dob) / 365.25)
                        ),
                        digits = 2
                    ),
                    # sex
                    biological_sex = sample(
                        x = private$params$sex,
                        size = private$params$n,
                        replace = TRUE
                    ),
                    is_deceased = dplyr::case_when(
                        age >= 65 ~ sample(
                            x = c("ja", "nee", "not.collected", "temp.unavailable"),
                            size = 1,
                            replace = TRUE,
                            prob = c(0.3, 0.5, 0.1, 0.1)
                        ),
                        TRUE ~ "nee"
                    ),
                    consanguinity = "nee",
                    date_registered = as.Date(
                        purrr::rdunif(
                            n = length(private$params$n),
                            a = as.integer(as.Date("2017-01-01")),
                            b = as.integer(as.Date("2021-01-01"))
                        ),
                        origin = "1970-01-01"
                    )
                ) %>%
                select(-age)
        },

        # create samples tables based on the params n (total patients) and
        # visits (i.e., the number of times a patient visited the clinic)
        build_samples_table = function() {
            d <- purrr::map(self$data$ids, function(.x) {
                i <- sample(
                    x = 1:private$params$n_samples,
                    size = 1,
                    prob = private$params$n_samples_prob
                )
                time <- data.frame(
                    umcg_numr = .x,
                    family_numr = self$data$patients$family_numr[
                        self$data$patients$umcg_numr == .x
                    ],
                    dna_numr = paste0(
                        "DNA-",
                        private$rand_numeric_id(n = i, length = 6)
                    ),
                    test_code = paste0(
                        "NX",
                        private$rand_numeric_id(n = i, length = 3)
                    ),
                    lab_indication = sample(
                        x = private$params$lab_incidation,
                        size = 1,
                        replace = TRUE,
                        prob = c(0.95, 0.2, 0.1, 0.1)
                    ),
                    sample_material = "bloed",
                    phenotype = sample(
                        x = c("OA", "NVT"),
                        size = 1,
                        replace = TRUE
                    ),
                    biological_sex = self$data$patients$biological_sex[
                        self$data$patients$umcg_numr == .x
                    ],
                    relationship = "patient",
                    requester = "S. Canner",
                    affected_status = sample(
                        x = c("ja", "nee"),
                        size = 1,
                        replace = TRUE,
                        prob = c(0.65, 0.35)
                    )
                )
            })

            d <- dplyr::bind_rows(d)
            d
        },

        build_labinfo_table = function() {
            self$data$samples %>%
                dplyr::select(
                    umcg_numr, family_numr, dna_numr, test_code
                ) %>%
                dplyr::left_join(
                    self$data$patients %>%
                        dplyr::select(umcg_numr, test_date = date_registered),
                    .,
                    by = "umcg_numr"
                ) %>%
                mutate(
                    test = sample(
                        x = c("Analyse Exoom; open exoom", "Analyse Exoom; panel OA"),
                        size = length(umcg_numr),
                        replace = TRUE
                    ),
                    capture_kit = "QXTR_580-Exoom_v3,Agilent/QXTExoom_v3",
                    prep_kit = "Agilent SureSelect",
                    expr_numr = "QXTR580",
                    design_numr = "S07604514"
                )
        },

        # generate files table
        build_files_table = function() {
            self$data$samples %>%
                dplyr::select(
                    umcg_numr, family_numr, dna_numr
                ) %>%
                dplyr::left_join(
                    self$data$patients %>%
                        dplyr::select(umcg_numr, date_registered),
                    .,
                    by = "umcg_numr"
                ) %>%
                dplyr::mutate(
                    filetype = sample(
                        x = private$params$filetypes$ngs$format,
                        size = length(umcg_numr),
                        replace = TRUE
                    ),
                    extension = sample(
                        x = private$params$filetypes$ngs$ext,
                        size = length(umcg_numr),
                        replace = TRUE
                    ),
                    filename = paste0(
                        paste(
                            family_numr,
                            umcg_numr,
                            dna_numr,
                            sep = "_"
                        ),
                        ".", extension
                    )
                ) %>%
                dplyr::select(-extension)
        }
    )
)
