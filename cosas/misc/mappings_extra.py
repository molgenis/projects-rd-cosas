#'////////////////////////////////////////////////////////////////////////////
#' FILE: mappings_extra.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-02-17
#' MODIFIED: 2022-07-14
#' PURPOSE: extra mappings that were once part of the main mapping script
#' STATUS: stable
#' PACKAGES: NA
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////


# ~ 1a ~
# Identify new linked family members
#
# In the new data, find subjects that do not exist in the following columns:
# `belongsWithFamilyMembers`. These IDs are import to keep, but it throws
# an error because the referenced IDs do not exist in the column `subjectID`.
# Instead of removing the IDs, it is better to register these cases as new
# COSAS subjects.
#
# The following code identifies missing IDs, creates a new COSAS record, and
# appends them to the main subject dataset.
#
# status_msg('Identifying unregistered family member identifiers...')

# maternalIDs = subjects['belongsToMother'].to_list()[0]
# paternalIDs = subjects['belongsToFather'].to_list()[0]
# familyData = subjects[:, (f.belongsWithFamilyMembers, f.belongsToFamily,f.subjectID)].to_tuples()

# belongsWithFamilyMembers = dt.Frame()
# for entity in familyData:
#   if not (entity[0] is None):
#     ids = [d.strip() for d in entity[0].split(',') if not (d is None) or (d != '')]
#     for el in ids:
#     # value must: not be blank, not equal to subjectID, and does not exist
#       if (
#         (el != '') and
#         (el != entity[2]) and
#         (el not in cosasSubjectIdList) and
#         (el not in maternalIDs) and
#         (el not in paternalIDs)
#       ):
#         belongsWithFamilyMembers.rbind(
#           dt.Frame([{
#             'subjectID': el,
#             'belongsToFamily': entity[1],
#             'belongsWithFamilyMembers': entity[0],
#             'comments': 'manually registered in COSAS'
#           }])
#         )

# del entity, ids, el

# select unique subjects only
# belongsWithFamilyMembers = belongsWithFamilyMembers[
#   :, first(f[:]), dt.by('subjectID')
# ][:, :, dt.sort(as_type(f.subjectID, int))]

# status_msg(
#   "Identified {} family members that aren't in the export..."
#   .format(belongsWithFamilyMembers.nrows)
# )


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