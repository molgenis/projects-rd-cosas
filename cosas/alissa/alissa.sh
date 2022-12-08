# ////////////////////////////////////////////////////////////////////////////
# FILE: alissa.sh
# AUTHOR: David Ruvolo
# CREATED: 2022-12-07
# MODIFIED: 2022-12-09
# STATUS: stable
# PURPOSE: alissa API endpoint
# DEPENDENCIES: jq
# COMMENTS: jq can be installed with homebrew: `brew install jq`
# ////////////////////////////////////////////////////////////////////////////

source .env

# SET URLS
HOST="${ALISSA_HOST}"
API_ROOT="${HOST}/interpret/api/2"

# AUTHENTICATE
TOKEN=$( \
  curl --user "${ALISSA_CLIENT_ID}:${ALISSA_CLIENT_SECRET}" "${HOST}/auth/oauth/token" \
  -d grant_type=password \
  -d username="${ALISSA_API_USR}" \
  -d password="${ALISSA_API_PWD}" \
)

# SET TOKEN HEADER
TOKEN_TYPE=$(jq -r '.token_type' <<< "${TOKEN}")
ACCESS_TOKEN=$(jq -r '.access_token' <<< "${TOKEN}")
TOKEN_HEADER="Authorization: ${TOKEN_TYPE} ${ACCESS_TOKEN}"
echo "${TOKEN_HEADER}"

#//////////////////////////////////////

# ~ 1 ~
# For the test, extract one subject ID, one analysis ID, and one export ID.

# ~ 1a ~
# Pull a snapshop of patients in the test environment
createdBefore="2021-02-20T00:00:00.000Z"
createdAfter="2021-02-18T00:00:00.000Z"
QUERY="createdAfter=${createdAfter}&createdBefore=${createdBefore}"
PATIENTS=$( curl -H "${TOKEN_HEADER}" -X GET "${API_ROOT}/patients?${QUERY}" )
echo "${PATIENTS}"

PATIENT_IDS=$(jq -r '.[].id' <<< "${PATIENTS}")
echo "${PATIENT_IDS}"

TEST_ID=$( sed -n '3p' <<< "${PATIENT_IDS}" )
echo "${TEST_ID}"

# ====OPTIONAL====
# ~ 1b ~
# GET TEST PATIENT INFO --- THIS ISN"T NECESSARY, BUT GOOD TO CHECK WHAT"S AVAILABLE
# TEST_PATIENT=$(curl -H "${TOKEN_HEADER}" -X GET "${API_ROOT}/patients/${TEST_ID}")
# TEST_PATIENT_ID=$(jq -r '.id' <<< "${TEST_PATIENT}")
# echo "${TEST_PATIENT}"
# echo "${TEST_PATIENT_ID}"
#=================

# ~ 1c ~
# GET ANALYSES -- YOU MAY NEED TO REPEAT THE 'TEST_ID' STEP UNTIL YOU GET A GOOD ID
TEST_PATIENT_ANALYSES=$(curl -H "${TOKEN_HEADER}" "${API_ROOT}/patients/${TEST_ID}/analyses")
echo "${TEST_PATIENT_ANALYSES}"

PATIENT_ANALYSIS_IDS=$(jq -r '.[].id' <<< "${TEST_PATIENT_ANALYSES}")
TEST_ANALYSIS_ID=$( sed -n '1p' <<< "${PATIENT_ANALYSIS_IDS}" )
echo "${PATIENT_ANALYSIS_IDS}"
echo "${TEST_ANALYSIS_ID}"

# NOTE: NONE OF THE IDS WORKED :-P
# SO I MANUALLY PICKED AN ID IN ALISSA AND PUT IT HERE
TEST_ANALYSIS_ID="...."

# ~ 1d ~
# GET VARIANTS EXPORT IDs

TEST_PATIENT_VARIANT_EXPORT=$( \
  curl --request POST "${API_ROOT}/patient_analyses/${TEST_ANALYSIS_ID}/molecular_variants/exports" \
  -H "Content-Type: application/json" \
  -H "${TOKEN_HEADER}" \
  --data '{"markedForReview":true, "markedIncludeInReport": false}' \
)

echo "${TEST_PATIENT_VARIANT_EXPORT}"

TEST_VARIANT_EXPORT_ID=$(jq -r '.exportId' <<< "${TEST_PATIENT_VARIANT_EXPORT}")
echo "${TEST_VARIANT_EXPORT_ID}"

# ~ 1e ~
# GET EXPORT ID
TEST_VARIANT_EXPORT=$( \
  curl -H "${TOKEN_HEADER}" \
  -X GET "${API_ROOT}/patient_analyses/${TEST_ANALYSIS_ID}/molecular_variants/exports/${TEST_VARIANT_EXPORT_ID}" \
)

echo "${TEST_VARIANT_EXPORT}" >> test_variant.json
