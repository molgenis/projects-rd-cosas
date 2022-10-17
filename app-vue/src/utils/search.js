
// Init Search Object
// Create object that will handle all loading messages (loading, error, successful)
// when querying for results via the API
//
// @return object
function initSearchResultsObject () {
  return {
    isSearching: false,
    wasSuccessful: false,
    hasFailed: false,
    errorMessage: null,
    successMessage: null,
    resultsUrl: null
  }
}

// fetchData
// retrive data from a given endpoint
//
// @param url string to an API endoint
//
// @return json
async function fetchData (url) {
  const response = await fetch(url)
  if (response.status / 100 !== 2) {
    const message = `\nStatus: ${response.status}\nMessage: ${response.statusText}\nUrl: ${response.url}`
    throw new Error(message)
  }
  return response.json()
}

// Remove Null Object Keys
// Remove all null keys from an object. This is the first step in preparing
// filters for a Molgenis DataExplorer URL
//
// @param data an object containing one or more Null keys
//
// @examples
// const filters = {
//   gender: 'female',
//   age: null,
//   country: 'Netherlands'
//   group: null
// }
// removeNullObjectKeys(filters)
// > { gender: 'female', country: 'Netherlands' }
//
// @return object
function removeNullObjectKeys (data) {
  const filters = data
  Object.keys(filters).forEach(key => {
    if (filters[key] === null || filters[key] === '') {
      delete filters[key]
    }
  })
  return filters
}

// Object To Url Filter Array
// Object containing  to an array of strings (in Molgenis format). Any value
// that is a comma-separated string, will be formatted accordingly
//
// @param object an object containing one more valid keys
//
// @examples
// const filters = {
//   gender: 'female',
//   age: null,
//   country: 'Australia, New Zealand'
//   group: null
// }
// const f = removeNullObjectKeys(filters)
// objectToUrlFilterArray(f)
// > ['gender==female', 'country=in=(Australia,New Zealand)']
//
// @return array of strings
function objectToUrlFilterArray (object) {
  const urlFilter = []
  Object.keys(object).forEach(key => {
    let filter = null
    let value = object[key].trim().replaceAll(', ', ',')
    if (value[value.length - 1] === ',') {
      value = value.slice(0, value.length - 1)
    }
    if (key.includes('.')) {
      if (value.includes(',')) {
        const indexFilters = value.split(',').map(val => `${key}=q=${val}`)
        filter = `(${indexFilters})`
      } else {
        filter = `${key}=q=${value}`
      }
    } else {
      if (value.includes(',')) {
        filter = `${key}=in=(${value})`
      } else {
        filter = `${key}==${value}`
      }
    }
    urlFilter.push(filter)
  })
  return urlFilter
}

// setDataExplorerUrl
// Create full URL with filters
//
// @param entity EMX table location as <package>_<entity>
// @param array an array of filters (i.e., output of objectToUrlFilterArray)
//
// @examples
// const userInputs = {
//   gender: 'female',
//   age: null,
//   country: 'Australia, New Zealand'
//   group: null
// }
// const filters = removeNullObjectKeys(userInputs)
// const filterArray = objectToUrlFilterArray(filters)
// setDataExplorerUrl('database_table', filterArray)

function setDataExplorerUrl (entity, array) {
  const filters = array.join(';')
  const filtersEncoded = encodeURIComponent(filters)
  const baseUrl = `/menu/plugins/dataexplorer?entity=${entity}&mod=data&hideselect=true`
  const url = baseUrl + '&filter=' + filtersEncoded
  return url
}

// setSearchAllUrl
// Generate the Data Explorer URL for a search all query
//
// @param entity EMX table location as <package>_<entity>
// @param query a string containing a search term
//
// @examples
// const query = 'my-search-term'
//
// @return a string containing a URL to a dataexplorer table
function setSearchAllUrl (entity, query) {
  const baseUrl = `/menu/plugins/dataexplorer?entity=${entity}&mod=data&hideselect=true`
  const urlParamEncoded = 'query%5Bq%5D%5B0%5D%5Boperator%5D=SEARCH&query%5Bq%5D%5B0%5D%5Bvalue%5D'
  const queryEncoded = encodeURIComponent(query)
  const url = `${baseUrl}&${urlParamEncoded}=${queryEncoded}`
  return url
}

// https://cosas-acc.molgeniscloud.org/menu/plugins/dataexplorer?entity=variantdb_variant&hideselect=true&mod=data&query%5Bq%5D%5B0%5D%5Boperator%5D=SEARCH&query%5Bq%5D%5B0%5D%5Bvalue%5D=test

// windowReplaceUrl
// Open table in database
//
// @param url URL to open
//

function windowReplaceUrl (url) {
  window.open(url, '_blank')
}

module.exports = {
  initSearchResultsObject,
  fetchData,
  removeNullObjectKeys,
  objectToUrlFilterArray,
  setDataExplorerUrl,
  setSearchAllUrl,
  windowReplaceUrl
}
