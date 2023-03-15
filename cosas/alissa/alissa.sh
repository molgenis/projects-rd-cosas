# ////////////////////////////////////////////////////////////////////////////
# FILE: alissa.sh
# AUTHOR: David Ruvolo
# CREATED: 2022-12-07
# MODIFIED: 2022-12-09
# STATUS: stable
# PURPOSE: alissa API endpoint
# DEPENDENCIES: jq
# COMMENTS: jq can be installed with homebrew: `brew install jq`
# Create a `.env` file in the root directory and paste the following lines.
# Fill in the credentials and run line-by-line.
# 
#     export ALISSA_HOST="...."
#     export ALISSA_API_USR="...."
#     export ALISSA_API_PWD="...."
#     export ALISSA_CLIENT_ID="...."
#     export ALISSA_CLIENT_SECRET="...."
#
# ////////////////////////////////////////////////////////////////////////////

# init vars
source .env
HOST="${ALISSA_HOST}"
API_ROOT="${HOST}/interpret/api/2"

# authenticate and create header var
TOKEN=$( \
  curl --user "${ALISSA_CLIENT_ID}:${ALISSA_CLIENT_SECRET}" "${HOST}/auth/oauth/token" \
  -d grant_type=password \
  -d username="${ALISSA_API_USR}" \
  -d password="${ALISSA_API_PWD}" \
)

TOKEN_TYPE=$(jq -r '.token_type' <<< "${TOKEN}")
ACCESS_TOKEN=$(jq -r '.access_token' <<< "${TOKEN}")
TOKEN_HEADER="Authorization: ${TOKEN_TYPE} ${ACCESS_TOKEN}"
echo "${TOKEN_HEADER}"

# //////////////////////////////////////

# SET PATIENT ID and grab data
patientID=''
patientData=$(curl -H "${TOKEN_HEADER}" -X GET "${API_ROOT}/patients/${patientID}" | jq '.' ) 

outputDir="private/alissa_export/${patientID}"
if [ ! -d $"${outputDir}" ]; then
  mkdir "${outputDir}"
fi

echo "${patientData}" >> "private/alissa_export/${patientID}/${patientID}_patient.json"

# retrieve all analyses and extract identifiers
patientAnalyses=$(curl -H "${TOKEN_HEADER}" "${API_ROOT}/patients/${patientID}/analyses" | jq '.')
echo "${patientAnalyses}" >> "private/alissa_export/${patientID}/${patientID}_analyses.json"
patientAnalysisIDs=$(jq -r '.[].id' <<< "${patientAnalyses}")

# get analysis ID repeat for each analysis in patientAnalysisIDs
echo "${patientAnalysisIDs}"
analysisID=$( sed -n '1p' <<< "${patientAnalysisIDs}" )  # CHANGE THIS FOR EACH ID
echo "${analysisID}"

# retrieve variant exports
patientVariantExports=$( \
  curl --request POST "${API_ROOT}/patient_analyses/${analysisID}/molecular_variants/exports" \
  -H "Content-Type: application/json" \
  -H "${TOKEN_HEADER}" \
  --data '{"markedForReview":true, "markedIncludeInReport": false}' \
  | jq '.' \
)

echo "${patientVariantExports}" >> "private/alissa_export/${patientID}/${patientID}_${analysisID}_variant_export_ids.json"


# get export data
variantExportID=$(jq -r '.exportId' <<< "${patientVariantExports}")
variantExportData=$( \
  curl -H "${TOKEN_HEADER}" \
  -X GET "${API_ROOT}/patient_analyses/${analysisID}/molecular_variants/exports/${variantExportID}" \
  | jq '.'
)

echo "${variantExportData}" >> "private/alissa_export/${patientID}/${patientID}_${analysisID}_variant_export_data.json"








# retrieve all variant exports
# echo "${patientAnalysisIDs}" | jq -c -r '.' | while read analysisID; do
#   echo "Retrieving variant export for analysis ${analysisID}"
  
#   patientVariantExports=$( \
#     curl --request POST "${API_ROOT}/patient_analyses/${analysisID}/molecular_variants/exports" \
#     -H "Content-Type: application/json" \
#     -H "${TOKEN_HEADER}" \
#     --data '{"markedForReview":true, "markedIncludeInReport": false}' \
#     | jq '.' \
#   )
  
#   # save export ids to file for future use
#   echo "${patientVariantExports}" >> "private/alissa_export/${patientID}/${patientID}_${analysisID}_variant_export_ids.json"
  
#   # extract export identifier
#   variantExportID=$(jq -r '.exportId' <<< "${patientVariantExport}")

#   # retrieve variant data with a quick pause just to make sure Alissa has time to generate the report
#   sleep 3
  
#   variantExportData=$( \
#     curl -H "${TOKEN_HEADER}" \
#     -X GET "${API_ROOT}/patient_analyses/${analysisID}/molecular_variants/exports/${variantExportID}" \
#     | jq '.' \
#   )

#   echo "${variantExportData}" >> "private/alissa_export/${patientID}/${patientID}_${analysisID}_variant_export_data.json"
  
# done



# ////////////////////////////////////////////////////////////////////////////

# OLD CODE

# ~ 1a ~
# Pull a snapshop of patients in the test environment
# createdBefore="2021-02-20T00:00:00.000Z"
# createdAfter="2021-02-18T00:00:00.000Z"
# QUERY="createdAfter=${createdAfter}&createdBefore=${createdBefore}"
# PATIENTS=$( curl -H "${TOKEN_HEADER}" -X GET "${API_ROOT}/patients?${QUERY}" )
# echo "${PATIENTS}"
# PATIENT_IDS=$(jq -r '.[].id' <<< "${PATIENTS}")
# echo "${PATIENT_IDS}"
# patientID=$( sed -n '3p' <<< "${PATIENT_IDS}" )
# echo "${patientID}"


# TEST_PATIENT_ID=$(jq -r '.id' <<< "${TEST_PATIENT}")
# echo "${TEST_PATIENT_ID}"
#

# TEST_ANALYSIS_ID=$( sed -n '1p' <<< "${patientAnalysisIDs}" )

# patientVariantExport=$( \
#   curl --request POST "${API_ROOT}/patient_analyses/${TEST_ANALYSIS_ID}/molecular_variants/exports" \
#   -H "Content-Type: application/json" \
#   -H "${TOKEN_HEADER}" \
#   --data '{"markedForReview":true, "markedIncludeInReport": false}' \
# )

# echo "${patientVariantExport}"

# patientVariantExportId=$(jq -r '.exportId' <<< "${patientVariantExport}")
# echo "${patientVariantExportId}"

# ~ 1e ~
# get export id
# TEST_VARIANT_EXPORT=$( \
#   curl -H "${TOKEN_HEADER}" \
#   -X GET "${API_ROOT}/patient_analyses/${TEST_ANALYSIS_ID}/molecular_variants/exports/${patientVariantExportId}" \
# )

# echo "${TEST_VARIANT_EXPORT}" >> test_variant.json
