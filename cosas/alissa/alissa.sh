
source .env

# set URLs + endpoints
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