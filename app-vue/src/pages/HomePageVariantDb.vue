<template>
  <Page>
    <Header
      id="variantdb-header"
      title="Variant DB"
      subtitle="Search for ...."
      :imageSrc="require('@/assets/header-bg-2.jpg')"
    />
    <Section id="variantdb-search" aria-labelledby="variantdb-search-title">
      <h2 id="variantdb-search-title">Search the Variant database</h2>
      <p>Find specific records or filter for classified variants using any of the filters below.</p>
      <Form id="variantdb-search-form" title="Search" class="flex">
        <FormSection>
          <SearchInput
            id="UMCGnr"
            label="Enter UMCGnr"
            description="Search for a patient by ID"
            @search="(value) => umcg = value"
          />
          <SearchButton id="search-id" @click="searchPatient" />
        </FormSection>
        <FormSection>
          <SearchInput
            id="gene"
            label="Search for a specific gene"
            description="e.g., TTN, ...."
            @search="(value) => gene = value"
          />
          <CheckboxInput
            id="showVusPlus"
            label="Also search for VUS+?"
            @change="showVusPlus = !showVusPlus"
          />
          <RadioButtons
            v-show="showVusPlus"
            id="vusPlus"
            name="vusPlus"
            label="Filter results by VUS+"
            description="Select either True or False. Untick the checkbox to remove this option."
            :values="['true', 'false']"
            :labels="['True', 'False']"
            @input="(value) => vusplus = value"
          />
          <SearchButton id="search-vusplus" @click="searchGene"/>
        </FormSection>
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
import CheckboxInput from '../components/InputCheckbox.vue'

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
      umcg: null,
      gene: null,
      vusplus: null,
      showVusPlus: false
    }
  },
  methods: {
    searchPatient () {
      const filters = [`umcg==${this.umcg}`]
      this.windowReplaceUrl(filters)
    },
    searchGene () {
      const filters = [`gene==${this.gene}`]
      if (this.showVusPlus) {
        filters.push(`vusPlus==${this.vusplus}`)
      }
      this.windowReplaceUrl(filters)
    },
    windowReplaceUrl (array) {
      const filters = array.join(';')
      const filtersEncoded = encodeURIComponent(filters)
      
      const baseUrl = '/menu/plugins/dataexplorer?entity=variantdb_variant&mod=data&hideselect=true'
      const url = baseUrl + '&filter=' + filtersEncoded
      window.open(url, '_blank')
    }
  }
}
</script>

<style lang="scss">
#variantdb-search-form {
  margin: 0 auto;
  max-width: 425px;
  
  // .form__sections {
  //   display: flex;
  //   justify-content: center;
  //   align-items: flex-start;
  //   flex-direction: row;
  //   flex-wrap: wrap;
  //   gap: 32px;
  // }
  
  .form__section {
    width: 350px;
    
    .search__button {
      // width: 125px;
      margin-top: 24px;
    }
  }
}
</style>
