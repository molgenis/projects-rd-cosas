<template>
  <Page>
    <Header
      id="variantdb-header"
      title="Variant DB"
      subtitle="Search for classified variants"
      :imageSrc="require('@/assets/header-bg-2.jpg')"
    />
    <Section id="variantdb-search-instructions" aria-labelledby="variantdb-search-instructions-title">
      <h2 id="variantdb-search-instructions-title">Instructions</h2>
      <p>Using the forms below, you can search for files or for patients with a certain phenotype. In all search fields, you may search for more than one value by separating each value with a comma. For example, if you would like to search for more than one patient by ID, format the values in the following way: "Patient-1234, Patient-5678". Click the search button to search the variant database.</p>
      <p>If there are any matching records, you will see a message below the search button that displays the total number of results along with a link to view the results. Click the link to view the data in the database.</p>
      <p>If you encounter any issues, take a look at the <router-link :to="{name: 'help'}">troubleshooting guide</router-link>.</p>
    </Section>
    <Section id="variantdb-search-forms" aria-labelledby="variantdb-search-patients-title">
      <div class="search-form-container">
        <FormContainer>
          <Form id="variantdb-search-patients-form" title="Search by Patient Information">
            <FormSection>
              <SearchInput
                id="UMCGnr"
                label="Search by MDN/UMCG number"
                description="Find classified variants using MDN/UMCG numbers"
                @search="(value) => patientFilters.umcg = value"
              />
            </FormSection>
            <FormSection>
              <SearchInput
                id="DNAnumr"
                label="Search by DNA number"
                description="Find classified variants using DNA numbers"
                @search="(value) => patientFilters.belongsToSample = value"
              />
            </FormSection>
            <FormSection>
              <SearchInput
                id=""
                label="Search by test code"
                description="Find classified variants using ADLAS test codes"
                @search="(value) => patientFilters[`belongsToSamplePreparation.belongsToLabProcedure`] = value"
              />
            </FormSection>
            <SearchButton id="variantdb-search-patients" @click="searchPatients" />
          </Form>
          <SearchResultsBox
            label="Unable to retrieve records"
            :isPerformingAction="patientSearchResults.isSearching"
            :actionWasSuccessful="patientSearchResults.wasSuccessful"
            :actionHasFailed="patientSearchResults.hasFailed"
            :actionErrorMessage="patientSearchResults.errorMessage"
            :totalRecordsFound="patientSearchResults.totalRecordsFound"
            :searchResultsUrl="patientSearchResults.resultsUrl"
          />
        </FormContainer>
        <FormContainer>
          <Form id="variantdb-search-variants-form" title="Search by Variant Information">
            <FormSection>
              <SearchInput
                id="gene-name"
                label="Search for Genes"
                description="Find classified variants by ADLAS gene names"
                @search="(value) => variantFilters.ADLASgeneNames = value"
              />
            </FormSection>
            <FormSection>
              <SearchInput
                id="gene-location"
                label="Search by Location"
                description="Find classified variants by chr:position"
                @search="(value) => parseVariantLocation(value)"
              />
            </FormSection>
            <FormSection>
              <FormLegend
                title="Search by Classification Status"
                description="Find classified variants by clinical classification status"
              />
              <CheckboxGroup>
                <div class="checkbox" v-for="type in classificationTypes" :key="type.value">
                  <input
                    :id="type.value"
                    type="checkbox"
                    :value="type.value"
                    class="checkbox__input"
                    v-model="selectedClassificationTypes"
                    @change="updateClassificationTypes"
                  />
                  <label :for="type.value" class="checkbox__label">
                    {{ type.label }}
                  </label>
                </div>
              </CheckboxGroup>
            </FormSection>
            <FormSection>
              <FormLegend title="Additional Search Options" />
              <CheckboxInput
                id="showVusPlus"
                label="Would you also like to limit results by VUS+?"
                :value="false"
                @change="updateVusPlus"
              />
            </FormSection>
            <SearchButton id="variantdb-search-variants" @click="searchVariants" />
          </Form>
          <SearchResultsBox
            label="Unable to retrieve records"
            :isPerformingAction="variantSearchResults.isSearching"
            :actionWasSuccessful="variantSearchResults.wasSuccessful"
            :actionHasFailed="variantSearchResults.hasFailed"
            :actionErrorMessage="variantSearchResults.errorMessage"
            :totalRecordsFound="variantSearchResults.totalRecordsFound"
            :searchResultsUrl="variantSearchResults.resultsUrl"
          />
        </FormContainer>
      </div>
    </Section>
  </Page>
</template>

<script>
import Page from '@/components/Page.vue'
import Header from '@/components/Header.vue'
import Section from '@/components/Section.vue'
import FormContainer from '@/components/FormContainer.vue'
import Form from '@/components/Form.vue'
import FormLegend from '@/components/FormLegend.vue'
import FormSection from '@/components/FormSection.vue'
import SearchResultsBox from '@/components/SearchResultsBox.vue'
import SearchButton from '@/components/ButtonSearch.vue'
import SearchInput from '@/components/InputSearch.vue'
import CheckboxInput from '@/components/CheckboxInput.vue'
import CheckboxGroup from '@/components/CheckboxGroup.vue'

import {
  fetchData,
  initSearchResultsObject,
  removeNullObjectKeys,
  objectToUrlFilterArray,
  setDataExplorerUrl
} from '@/utils/search.js'

export default {
  name: 'variantdb-search',
  components: {
    Page,
    Header,
    Section,
    FormContainer,
    Form,
    FormLegend,
    FormSection,
    SearchResultsBox,
    SearchInput,
    SearchButton,
    CheckboxInput,
    CheckboxGroup
  },
  data () {
    return {
      includeVusPlus: false,
      patientSearchResults: initSearchResultsObject(),
      variantSearchResults: initSearchResultsObject(),
      patientFilters: {
        umcg: null,
        belongsToSample: null,
        'belongsToSamplePreparation.belongsToLabProcedure': null
      },
      variantFilters: {
        '%23CHROM': null,
        start: null,
        ADLASgeneNames: null,
        classificationStaf: null
      },
      selectedClassificationTypes: [],
      classificationTypes: [
        { value: '1', label: 'Benign' },
        { value: '2', label: 'Likely Benign' },
        { value: '3', label: 'Variant of Uncertain Significance (VUS)' },
        { value: '4', label: 'Likely Pathogenic' },
        { value: '5', label: 'Pathogenic' },
        { value: '6', label: 'Other' }
      ]
    }
  },
  methods: {
    parseVariantLocation (value) {
      const locationValues = value.split(',')
      const chromosomes = []
      const startPositions = []
      locationValues.forEach(val => {
        const valueSplit = val.split(':')
        if (valueSplit.length > 0) {
          chromosomes.push(valueSplit[0])
          startPositions.push(valueSplit[1])
        }
      })
      this.variantFilters['%23CHROM'] = chromosomes.join(',')
      this.variantFilters.start = startPositions.join(',')
    },
    updateVusPlus () {
      this.includeVusPlus = !this.includeVusPlus
      if (this.includeVusPlus) {
        this.variantFilters.vusplus = this.includeVusPlus.toString()
      } else {
        this.variantFilters.vusplus = null
      }
    },
    updateClassificationTypes () {
      this.variantFilters.classificationStaf = this.selectedClassificationTypes.join()
    },
    resetPatientSearchResults () {
      this.patientSearchResults = initSearchResultsObject()
    },
    resetVariantSearchResults () {
      this.variantSearchResults = initSearchResultsObject()
    },
    searchPatients () {
      this.resetPatientSearchResults()
      this.patientSearchResults.isSearching = true

      const filters = removeNullObjectKeys(this.patientFilters)
      const apiParams = objectToUrlFilterArray(filters)
      const apiUrl = `/api/v2/variantdb_variant?q=${apiParams}`
      
      Promise.all([
        fetchData(apiUrl)
      ]).then(response => {
        const data = response[0]
        const totalRecordsFound = data.total
        this.patientSearchResults.totalRecordsFound = totalRecordsFound
        this.patientSearchResults.wasSuccessful = true
        
        if (totalRecordsFound > 0) {
          this.patientSearchResults.resultsUrl = setDataExplorerUrl('variantdb_variant', apiParams)
        }
        this.patientSearchResults.isSearching = false
      }).catch(error => {
        this.patientSearchResults.isSearching = false
        this.patientSearchResults.wasSuccessful = false
        this.patientSearchResults.hasFailed = true
        this.patientSearchResults.errorMessage = error.message
      })
    },
    searchVariants () {
      this.resetVariantSearchResults()
      this.variantSearchResults.isSearching = true
      
      const filters = removeNullObjectKeys(this.variantFilters)
      const apiParams = objectToUrlFilterArray(filters)
      const apiUrl = `/api/v2/variantdb_variant?q=${apiParams}`
      
      Promise.all([
        fetchData(apiUrl)
      ]).then(response => {
        const data = response[0]
        const totalRecordsFound = data.total
        this.variantSearchResults.totalRecordsFound = totalRecordsFound
        this.variantSearchResults.wasSuccessful = true
        
        if (totalRecordsFound > 0) {
          this.variantSearchResults.resultsUrl = setDataExplorerUrl('variantdb_variant', apiParams)
        }
        this.variantSearchResults.isSearching = false
      }).catch(error => {
        this.variantSearchResults.isSearching = false
        this.variantSearchResults.wasSuccessful = false
        this.variantSearchResults.hasFailed = true
        this.variantSearchResults.errorMessage = error.message
      })
    }
  }
}
</script>

<style lang="scss" scoped>

#variantdb-search-instructions {
  background-color: $gray-000;
}

</style>
