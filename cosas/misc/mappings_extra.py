#'////////////////////////////////////////////////////////////////////////////
#' FILE: mappings_extra.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-02-17
#' MODIFIED: 2022-03-02
#' PURPOSE: extra mappings that were once part of the main mapping script
#' STATUS: stable
#' PACKAGES: NA
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

# 
# cosasportal_samples -> umdm_samples
#
# The following code was used initially, but after review it was decide to
# remove it.
#
# NOTE: WILL NOT DO
# collapse request by sampleID into a comma seperated string
# status_msg('Formatting request identifiers...')
# samples['belongsToRequest'] = dt.Frame([
#     ','.join(
#         list(
#             set(
#                 samples[
#                     f.sampleID == d[0], 'belongsToRequest'
#                 ].to_list()[0]
#             )
#         )
#     ) for d in samples[:, (f.sampleID, f.belongsToRequest)].to_tuples()
# ])
#
# format `dateOfRequest` as yyyy-mm-dd
# samples['dateOfRequest'] = dt.Frame([
#     cosastools.formatAsDate(d, asString = True) for d in samples['dateOfRequest'].to_list()[0]
# ])

# 
# The following code was never implemented, but it was test to create a list
# of all unique test codes per sample and then formatting the values into
# a comma separated string. I thought this would be useful for the column
# `alternativeIdentifiers`, but the purpose of that column is to capture
# other IDs that associated with the samples. For example, if the sample
# is used in another study/project you may want to reference that ID here.
# If you need this, use the code below
#
# samples['alternativeIdentifiers'] = dt.Frame([  
#     ','.join(
#         list(
#             set(
#                 samples[
#                   (
#                     (f.sampleID == d[0]) &
#                     (f.belongsToSubject == d[1]) &
#                     (f.belongsToRequest == d[2]),
#                   )
#                     'alternativeIdentifiers'
#                 ].to_list()[0]
#             )
#         )
#     ) for d in samples[
#         :,(
#               f.sampleID,
#               f.belongsToSubject,
#               f.belongsToRequest,
#               f.alternativeIdentifiers
#           )
#     ].to_tuples()
# ])