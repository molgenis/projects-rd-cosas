#! /usr/local/bin/sh
source .env

HOST="${ALISSA_HOST}"
API_ROOT="${HOST}/interpret/api/2"

TOKEN=$( \
  curl --user "${ALISSA_CLIENT_ID}:${ALISSA_CLIENT_SECRET}" "${HOST}/auth/oauth/token" \
  -d grant_type=password \
  -d username="${ALISSA_API_USR}" \
  -d password="${ALISSA_API_PWD}" \
)

TOKEN_TYPE=$(jq -r '.token_type' <<< "${TOKEN}")
ACCESS_TOKEN=$(jq -r '.access_token' <<< "${TOKEN}")

curl -H "Authorization: ${TOKEN_TYPE} ${ACCESS_TOKEN}" -X GET "${API_ROOT}/patients/<id>"


# API_PATIENTS="${API_ROOT}/patients"
# echo "${API_PATIENTS}"
# echo "${ALISSA_API_USR}"
# echo "${TOKEN_TYPE}"
# echo "${ACCESS_TOKEN}"

# -H "Content-Type: application/json" \
# -H "accept: */*" \
# QUERY='createdAfter=2012-21-11T00:00:00.000+00:00&createdBefore=2012-22-11T00:00:00.000+00:00'
# API_ANALYSES = "${API_PATIENTS}/${PATIENT_ID}/analyses"
# API_VARIANT_EXPORTS = "${API_PATIENTS}/patient_analyses/${ANALYSIS_ID}/molecular_variants/exports"
# API_VARIANT_REPORT = "${API_PATIENTS}/patient_analyses/${ANALYSIS_ID}/molecular_variants/exports/{EXPORT_ID}"

# echo "${API_PATIENTS}"
# echo "${URL}"

# URL="${API_PATIENTS}?${QUERY}"
# --data '{ \
#   "createdBefore": "2012-22-11T00:00:00.000+00:00",
#   "createdAfter": "2012-21-11T00:00:00.000+00:00"
# }'
  
# >> 'private/test.json' 
  
# -d createdBefore="2012-22-11T00:00:00.000+00:00" \
# >> 'private/patients.json'

# PATIENTS=$( )
# echo "${PATIENTS}"
