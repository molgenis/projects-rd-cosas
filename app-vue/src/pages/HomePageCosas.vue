<template>
  <Page>
    <Header
      id="cosas-header"
      title="COSAS"
      subtitle="Search the COSAS Database"
      :imageSrc="require('@/assets/header-bg-2.jpg')"
    />
    <Section id="cosas-search-instructions" aria-labelledby="cosas-search-instructions-title">
      <h2 id="cosas-search-instructions-title">Instructions</h2>
      <p>Using the forms below, you can search for files or for patients with a certain phenotype. You may search for more than one value by separating IDs or codes with a comma. For example: "Patient-1234, Patient-5678". If there are matching records, the total number of results will be displayed along with a link to view the results. Click the link to view the data in COSAS.</p>
      <p>If you encounter any issues, take a look at the <router-link :to="{name: 'help'}">troubleshooting guide</router-link>.</p>
    </Section>
    <div id="cosas-search" class="cosas-search-container">
      <FormContainer class="cosas-search-form">
        <Form id="cosas-files-search-form" title="Search for Files">
          <FormSection>
            <SearchInput
              id="subjectID"
              label="Search for MDN/UMCG Numbers"
              description="Search for patients and their relatives"
              @search="(value) => fileFilters.belongsToSubject = value"
            />
          </FormSection>
          <FormSection>
            <legend class="form__legend">
              Search for file types
              <span class="form__legend__caption">Select one or more file type</span>
            </legend>
            <div class="checkbox__group">
              <div class="checkbox" v-for="filetype in filetypes" :key="filetype.value">
                <input
                  :id="filetype.value"
                  type="checkbox"
                  :value="filetype.value"
                  class="checkbox__input"
                  v-model="selectedFileTypes"
                  @change="updateFileFormats"
                />
                <label :for="filetype.value" class="checkbox__label">
                  {{ filetype.label }}
                </label>
              </div>
            </div>
          </FormSection>
          <SearchButton id="search-subjects" @click="searchFiles"/>
        </Form>
        <SearchResultsBox
          label="Unable to retrieve records"
          :isPerformingAction="fileSearch.isSearching"
          :actionWasSuccessful="fileSearch.wasSuccessful"
          :actionHasFailed="fileSearch.hasFailed"
          :actionErrorMessage="fileSearch.errorMessage"
          :totalRecordsFound="fileSearch.totalRecordsFound"
          :searchResultsUrl="fileSearch.resultsUrl"
        />
      </FormContainer>
      <FormContainer class="cosas-search-form">
        <Form id="cosas-diagnostic-search-form" title="Search for Diagnostic Information">
          <FormSection>
            <SearchInput
              id="clinicalSubjectID"
              label="Search for MDN/UMCG Numbers"
              description="Search for patients and their relatives"
              @search="(value) => clinicalFilters.belongsToSubject = value"
            />
          </FormSection>
          <FormSection>
            <SearchInput
              id="clinicalObservedPhenotype"
              label="Clinical Phenotype (HPO)"
              description="Enter one or more HPO code, e.g., 'HP:0001270, HP:0001638'"
              @search="(value) => clinicalFilters.observedPhenotype = value"
            />
          </FormSection>
          <SearchButton id="search-clinical" @click="searchClinical"/>
        </Form>
        <SearchResultsBox
          label="Unable to retrieve records"
          :isPerformingAction="clinicalSearch.isSearching"
          :actionWasSuccessful="clinicalSearch.wasSuccessful"
          :actionHasFailed="clinicalSearch.hasFailed"
          :actionErrorMessage="clinicalSearch.errorMessage"
          :totalRecordsFound="clinicalSearch.totalRecordsFound"
          :searchResultsUrl="clinicalSearch.resultsUrl"
        />
      </FormContainer>
    </div>
  </Page>
</template>

<script>
import Page from '@/components/Page.vue'
import Header from '@/components/Header.vue'
import Section from '@/components/Section.vue'
import FormContainer from '@/components/FormContainer.vue'
import Form from '@/components/Form.vue'
import FormSection from '@/components/FormSection.vue'
import SearchButton from '@/components/ButtonSearch.vue'
import SearchInput from '@/components/InputSearch.vue'
import SearchResultsBox from '@/components/SearchResultsBox.vue'

import {
  fetchData,
  initSearchResultsObject,
  removeNullObjectKeys,
  objectToUrlFilterArray,
  setDataExplorerUrl
} from '@/utils/search.js'

export default {
  name: 'cosas-homepage',
  components: {
    Page,
    Header,
    Section,
    FormContainer,
    Form,
    FormSection,
    SearchButton,
    SearchInput,
    SearchResultsBox
  },
  data () {
    return {
      filetypes: [
        { value: 'bam', label: 'BAM' },
        { value: 'cram', label: 'CRAM' },
        { value: 'fastq', label: 'FastQ' },
        { value: 'vcf', label: 'VCF' }
      ],
      selectedFileTypes: [],
      clinicalFilters: {
        belongsToSubject: null,
        observedPhenotype: null
      },
      fileFilters: {
        belongsToSubject: null,
        fileFormat: null
      },
      fileSearch: initSearchResultsObject(),
      clinicalSearch: initSearchResultsObject()
    }
  },
  methods: {
    updateFileFormats () {
      this.fileFilters.fileFormat = this.selectedFileTypes.join()
    },
    resetFileSearch () {
      this.fileSearch = initSearchResultsObject()
    },
    resetClinicalSearch () {
      this.clinicalSearch = initSearchResultsObject()
    },
    searchFiles () {
      this.resetFileSearch()
      this.fileSearch.isSearching = true

      const filters = removeNullObjectKeys(this.fileFilters)
      const filtersAsUrlParams = objectToUrlFilterArray(filters).join(';')
      const url = `/api/v2/umdm_files?attributes=fileID&q=${filtersAsUrlParams}`

      Promise.all([fetchData(url)]).then(response => {
        const data = response[0]
        const totalRecordsFound = data.total
        this.fileSearch.totalRecordsFound = totalRecordsFound
        this.fileSearch.wasSuccessful = true
        
        if (totalRecordsFound > 0) {
          const idsForUrl = data.items.map(row => { return row.belongsToSubject.subjectID }) // use fileID when available
          const filtersAsUrlParams = objectToUrlFilterArray(
            { belongsToSubject: idsForUrl.join(',') },
            { fileFormat: this.fileFilters.fileFormat }
          )
          const url = setDataExplorerUrl('umdm_files', filtersAsUrlParams)
          this.fileSearch.resultsUrl = url
        }
        
        this.fileSearch.isSearching = false
      }).catch(error => {
        this.fileSearch.isSearching = false
        this.fileSearch.wasSuccesful = false
        this.fileSearch.hasFailed = true
        this.fileSearch.errorMessage = error.message
      })
    },
    searchClinical () {
      this.resetClinicalSearch()
      this.clinicalSearch.isSearching = true
      
      const filters = removeNullObjectKeys(this.clinicalFilters)
      const filtersAsUrlParams = objectToUrlFilterArray(filters).join(';')
      const url = `/api/v2/umdm_clinical?attributes=belongsToSubject&q=${filtersAsUrlParams}`

      Promise.all([fetchData(url)]).then(response => {
        const data = response[0]
        const totalRecordsFound = data.total
        this.clinicalSearch.totalRecordsFound = totalRecordsFound
        this.clinicalSearch.wasSuccessful = true
        
        if (totalRecordsFound > 0) {
          const idsForUrl = data.items.map(row => { return row.belongsToSubject.subjectID })
          const filtersAsUrlParams = objectToUrlFilterArray({ belongsToSubject: idsForUrl.join(',') })
          const url = setDataExplorerUrl('umdm_clinical', filtersAsUrlParams)
          this.clinicalSearch.resultsUrl = url
        }
        this.clinicalSearch.isSearching = false
      }).catch(error => {
        this.clinicalSearch.isSearching = false
        this.clinicalSearch.wasSuccesful = false
        this.clinicalSearch.hasFailed = true
        this.clinicalSearch.errorMessage = error.message
      })
    }
  }
}
</script>

<style lang="scss" scoped>

.form__legend {
  font-size: 12pt;
  color: $body-heading;
  
  .form__legend__caption {
    display: block;
    font-size: 11pt;
    color: $body-caption;
  }
}

.checkbox__group {
  .checkbox {
    display: flex;
    flex-direction: row;
    align-items: center;
    .checkbox__input {
      margin-top: -3px;
      margin-right: 6px;
    }
    .checkbox__label {
      line-height: 1.4;
    }
  }
}

.cosas-search-container {
  box-sizing: padding-box;
  padding: 2em 1em;
  margin: 0 auto;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  justify-content: center;
  align-items: flex-start;
  max-width: 1024px;
  
  .cosas-search-form {
    width: 100%;
    max-width: 462px;
    border-top-color: $green-300;
    
    .search__button {
      margin-top: 18px;
    }
  }
}

#cosas-search-instructions {
  background-color: $gray-000;
}
</style>
