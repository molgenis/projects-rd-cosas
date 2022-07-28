<template>
  <Page>
    <Header
      id="variantdb-header"
      title="Variant DB"
      subtitle="Search for ...."
      :imageSrc="require('@/assets/header-bg-2.jpg')"
    />
    <Section id="variantdb-search" aria-labelledby="variantdb-search-title">
      <FormContainer>
        <Form id="variantdb-search-form" title="Search the variant database">
          <FormSection>
            <SearchInput
              id="UMCGnr"
              label="Search for MDN/UMCG Numbers"
              description="Search for patients and their relatives"
              @search="(value) => variantFilters.umcg = value"
            />
          </FormSection>
          <FormSection>
            <SearchInput
              id="DNAnumr"
              label="Enter DNA nummer"
              description="Search for a sample ID"
              @search="(value) => variantFilters.belongsToSample = value"
            />
          </FormSection>
          <FormSection>
            <SearchInput
              id="gene"
              label="Search for a specific gene"
              @search="(value) => variantFilters.gene = value"
            />
            <CheckboxInput
              id="showVusPlus"
              label="Would you also like to limit results by VUS+?"
              :value="false"
              @change="updateVusPlus"
            />
          </FormSection>
          <!-- <FormSection>
            <SearchInput
              id="chromosome"
              label="Search for a chromosome"
              description="Enter either 1,2,3,4,etc."
            />
          </FormSection> -->
          <SearchButton id="variantdb-search" @click="searchVariants" />
          <SearchResultsBox
          label="Unable to retrieve records"
          :isPerformingAction="variantSearch.isSearching"
          :actionWasSuccessful="variantSearch.wasSuccessful"
          :actionHasFailed="variantSearch.hasFailed"
          :actionErrorMessage="variantSearch.errorMessage"
          :totalRecordsFound="variantSearch.totalRecordsFound"
          :searchResultsUrl="variantSearch.resultsUrl"
        />
        </Form>
      </FormContainer>
    </Section>
  </Page>
</template>

<script>
import Page from '@/components/Page.vue'
import Header from '@/components/Header.vue'
import Section from '@/components/Section.vue'
import FormContainer from '@/components/FormContainer.vue'
import Form from '@/components/Form.vue'
import FormSection from '@/components/FormSection.vue'
import SearchResultsBox from '@/components/SearchResultsBox.vue'
import SearchButton from '@/components/ButtonSearch.vue'
import SearchInput from '@/components/InputSearch.vue'
import CheckboxInput from '@/components/CheckboxInput.vue'

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
    FormSection,
    SearchResultsBox,
    SearchInput,
    SearchButton,
    CheckboxInput
  },
  data () {
    return {
      includeVusPlus: false,
      variantFilters: {
        umcg: null,
        belongsToSample: null,
        gene: null,
        vusplus: null
      },
      variantSearch: initSearchResultsObject()
    }
  },
  methods: {
    updateVusPlus () {
      this.includeVusPlus = !this.includeVusPlus
      if (this.includeVusPlus) {
        this.variantFilters.vusplus = this.includeVusPlus.toString()
      } else {
        this.variantFilters.vusplus = null
      }
    },
    resetVariantSearch () {
      this.variantSearch = initSearchResultsObject()
    },
    searchVariants () {
      this.resetVariantSearch()
      this.variantSearch.isSearching = true

      const filters = removeNullObjectKeys(this.variantFilters)
      const apiParams = objectToUrlFilterArray(filters).join(';')
      const apiUrl = `/api/v2/variantdb_variant?q=${apiParams}`
      
      Promise.all([
        fetchData(apiUrl)
      ]).then(response => {
        const data = response[0]
        const totalRecordsFound = data.total
        this.variantSearch.totalRecordsFound = totalRecordsFound
        this.variantSearch.wasSuccessful = true
        
        if (totalRecordsFound > 0) {
          const idsForUrl = data.items.map(row => {
            return row.belongsToSubject // set correct ID when db is ready
          })
          const urlParams = objectToUrlFilterArray(
            { belongsToSubject: idsForUrl.join(',') }
          )
          const dataExplorerUrl = setDataExplorerUrl('variantdb_variant', urlParams)
          this.variantSearch.resultsUrl = dataExplorerUrl
        }
        this.variantSearch.isSearching = false
      }).catch(error => {
        this.variantSearch.isSearching = false
        this.variantSearch.wasSuccessful = false
        this.variantSearch.hasFailed = true
        this.variantSearch.errorMessage = error.message
      })
      // const userInput = removeNullObjectKeys(this.filters)
      // const filterUrl = objectToUrlFilterArray(userInput)
      // // windowReplaceUrl('variantdb_variant', filterUrl)
      // console.log(filterUrl)
    }
  }
}
</script>

<style lang="scss">
#variantdb-search-form {
  border-top-color: #A4031F;
}
</style>
