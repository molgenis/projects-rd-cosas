<template>
  <Page>
    <Header
      id="cosas-header"
      title="COSAS"
      subtitle="Search the COSAS Database"
      :imageSrc="require('@/assets/header-bg-2.jpg')"
    />
    <main>
      <Section id="cosas-search-form">
        <Form
          id="cosas-files-search-form"
          class="cosas-search-form"
          title="Search for Files"
          description="Find types of files by one or more patients."
        >
          <FormSection>
            <SearchInput
              id="subjectID"
              label="Search for MDN/UMCG Numbers"
              description="Enter one ore more MDN/UMCGnr for a patient or a relative of the patient"
              @search="(value) => fileFilters.belongsToSubject = value"
            />
          </FormSection>
          <FormSection>
            <legend class="form__legend">
              Search for file types
              <span class="form__legend__caption">Select one or more file types</span>
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
          <SearchResultsBox
            label="Unable to retrieve records"
            :isPerformingAction="fileSearch.isSearching"
            :actionWasSuccessful="fileSearch.wasSuccessful"
            :actionHasFailed="fileSearch.hasFailed"
            :actionErrorMessage="fileSearch.errorMessage"
            :actionSuccessMessage="fileSearch.successMessage"
          />
        </Form>
        <Form
          id="cosas-diagnostic-search-form"
          class="cosas-search-form"
          title="Search for Diagnostic Information"
        >
          <FormSection>
            <SearchInput
              id="clinicalSubjectID"
              label="UMCGnummer"
              description="Search for a particular UMCGnr"
              @search="(value) => clinicalFilters.belongsToSubject = value"
            />
          </FormSection>
          <FormSection>
            <SearchInput
              id="clinicalObservedPhenotype"
              label="Klinisch Fenotype (HPO)"
              description="Enter one or more HPO codes, e.g., 'HP:0001270,HP:0001638'"
              @search="(value) => clinicalFilters.observedPhenotype = value"
            />
          </FormSection>
          <SearchButton id="search-clinical" @click="searchClinical"/>
        </Form>
      </Section>
    </main>
  </Page>
</template>

<script>
import Page from '@/components/Page.vue'
import Header from '@/components/Header.vue'
import Section from '@/components/Section.vue'
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
  setDataExplorerUrl,
  windowReplaceUrl
} from '@/utils/search.js'

export default {
  name: 'cosas-homepage',
  components: {
    Page,
    Header,
    Section,
    Form,
    FormSection,
    SearchButton,
    SearchInput,
    SearchResultsBox
  },
  data () {
    return {
      filetypes: [
        { value: 'gVCF', label: 'gVCF' },
        { value: 'fastq', label: 'FastQ' },
        { value: 'bam', label: 'Bam' }
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
      fileSearch: initSearchResultsObject()
    }
  },
  methods: {
    updateFileFormats () {
      this.fileFilters.fileFormat = this.selectedFileTypes.join()
    },
    resetFileSearch () {
      this.fileSearch = initSearchResultsObject()
    },
    searchFiles () {
      this.resetFileSearch()
      this.fileSearch.isSearching = true

      const filters = removeNullObjectKeys(this.fileFilters)
      const filtersAsUrlParams = objectToUrlFilterArray(filters).join(';')
      const url = `/api/v2/umdm_files?attributes=fileID&q=${filtersAsUrlParams}`

      setTimeout(() => {
        Promise.all([
          fetchData(url)
        ]).then(response => {
          const data = response[0]
          this.fileSearch.totalRecordsFound = data.total
          this.fileSearch.successMessage = `Found ${data.total} result${data.total === 1 ? 's' : ''}`
          
          const idsForUrl = data.items.map(row => row.belongsToSubject)
          const filtersAsUrlParams = objectToUrlFilterArray({ belongsToSubject: idsForUrl.join(',') })
          const url = setDataExplorerUrl('umdm_files', filtersAsUrlParams)
          this.fileSearch.url = url
          
          this.fileSearch.isSearching = false
          this.fileSearch.wasSuccesful = true
        }).catch(error => {
          this.fileSearch.isSearching = false
          this.fileSearch.wasSuccesful = false
          this.fileSearch.hasFailed = true
          this.fileSearch.errorMessage = error.message
        })
      }, 4000)
    },
    searchClinical () {
      const filters = removeNullObjectKeys(this.clinicalFilters)
      const filtersAsUrlParams = objectToUrlFilterArray(filters)
      const url = setDataExplorerUrl('umdm_clinical', filtersAsUrlParams)
      windowReplaceUrl(url)
    }
  }
}
</script>

<style lang="scss" scoped>
.cosas-search-form {
  border-top-color: $green-300;
}

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
</style>
