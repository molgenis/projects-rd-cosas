<template>
  <Page>
    <Header
      id="variantdb-header"
      title="Variant DB"
      subtitle="Search for ...."
      :imageSrc="require('@/assets/header-bg-2.jpg')"
    />
    <Section id="variantdb-search" aria-labelledby="variantdb-search-title">
      <!-- <h2 id="variantdb-search-title">Search the Variant database</h2>
      <p>Find specific records or filter for classified variants using any of the filters below.</p> -->
      <Form
        id="variantdb-search-form"
        title="Search the variant database"
        description="Find specific records using one or more of the filters below. You can also search for multiple values at a time. To do so, format the values with a comma e.g., 'value 1, value 2, ...'."
      >
        <FormSection>
          <SearchInput
            id="UMCGnr"
            label="Enter UMCGnr"
            description="Search for a patient by ID"
            @search="(value) => filters.umcg = value"
          />
        </FormSection>
        <FormSection>
          <SearchInput
            id="DNAnumr"
            label="Enter DNA nummer"
            description="Search for a sample ID"
            @search="(value) => filters.belongsToSample = value"
          />
        </FormSection>
        <FormSection>
          <SearchInput
            id="gene"
            label="Search for a specific gene"
            description="e.g., TTN, ...."
            @search="(value) => filters.gene = value"
          />
          <CheckboxInput
            id="showVusPlus"
            label="Would you also like to limit results by VUS+?"
            @change="updateVusPlus"
          />
          <RadioButtons
            v-show="showVusPlus"
            id="vusPlus"
            name="vusPlus"
            label="Filter results by VUS+"
            description="Select either True or False. Untick the checkbox to remove this option."
            :values="['true', 'false']"
            :labels="['True', 'False']"
            @input="(value) => filters.vusplus = value"
          />
        </FormSection>
        <!-- <FormSection>
          <SearchInput
            id="chromosome"
            label="Search for a chromosome"
            description="Enter either 1,2,3,4,etc."
          />
        </FormSection> -->
        <SearchButton id="variantdb-search" @click="search" />
      </Form>
    </Section>
  </Page>
</template>

<script>
import Page from '../components/Page.vue'
import Header from '../components/Header.vue'
import Section from '../components/Section.vue'
import Form from '../components/Form.vue'
import FormSection from '../components/FormSection.vue'

import SearchButton from '../components/ButtonSearch.vue'
import SearchInput from '../components/InputSearch.vue'
import RadioButtons from '../components/InputRadioButtons.vue'
import CheckboxInput from '../components/CheckboxInput.vue'

import { removeNullObjectKeys, objectToUrlFilterArray } from '../utils/search.js'

export default {
  name: 'variantdb-search',
  components: {
    Page,
    Header,
    Section,
    Form,
    FormSection,
    SearchInput,
    RadioButtons,
    SearchButton,
    CheckboxInput
  },
  data () {
    return {
      filters: {
        umcg: null,
        belongsToSample: null,
        gene: null,
        vusplus: null
      },
      showVusPlus: false
    }
  },
  methods: {
    updateVusPlus () {
      this.showVusPlus = !this.showVusPlus
      if (!this.showVusPlus) {
        this.filters.vusplus = null
      }
    },
    search () {
      const userInput = removeNullObjectKeys(this.filters)
      const filterUrl = objectToUrlFilterArray(userInput)
      console.log(filterUrl)
      // this.windowReplaceUrl('variantdb_variant',filterUrl)
    }
  }
}
</script>

<style lang="scss">
#variantdb-search-form {
  border-top-color: #A4031F;
}
</style>
