<template>
  <Page>
    <Header
            id="variantdb-header"
            title="Variant DB"
            subtitle="Search for ...." />
    <Section id="">
      <h2>Search the Variant database</h2>
      <p>Find specific records or filter for classified variants using any of the filters below.</p>
      <Form id="variantdb-search-form" title="Search">
        <FormSection>
          <SearchInput
            id="UMCGnr"
            label="Enter UMCGnr"
            description="Search for a patient by ID"
            @search="(value) => onInput(value, 'umcg')"
          />
          <SearchButton
            id="search-id"
            name="Search"
            @click="() => onClick(['umcg'])"
          />
        </FormSection>
        <FormSection>
          <SearchInput
            id="gene"
            label="Search for a specific gene"
            description="e.g., TTN, ...."
            @search="(value) => onInput(value, 'gene')"
          />
          <CheckboxInput
            id="showVusPlus"
            label="Also search for VUS+?"
            @change="() => { showVusPlus =! showVusPlus }"
          />
          <RadioButtons
            v-show="showVusPlus"
            id="vusPlus"
            name="vusPlus"
            label="Filter results by VUS+"
            description="Select either True or False. Untick the checkbox to remove this option."
            :values="['true', 'false']"
            :labels="['True', 'False']"
            @change="(value) => onInput(value, 'vusplus')"
          />
          <SearchButton
            id="search-vusplus"
            @click="() => onClick(['gene', 'vusplus'], 'vusplus', !showVusPlus)"
          />
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
    onInput (value, prop) {
      this[prop] = value
    },
    onClick (arrayOfPropNames, keyToRemove, keyToRemoveState) {
      // const baseUrl = '/menu/plugins/dataexplorer?entity=variantdb_variant&mod=data&hideselect=true
      let urlFilters = arrayOfPropNames
      if (keyToRemoveState) {
        urlFilters = arrayOfPropNames.filter(name => name !== keyToRemove)
      }
      
      const filters = urlFilters.map(filter => `${filter}==${this[filter]}`).join(';')
      console.log(arrayOfPropNames, keyToRemoveState, filters)
    }
  }
}
</script>

<style lang="scss">
#variantdb-header {
  background-image: url("~@/assets/header-bg-2.jpg");
  background-position: 100% 0;
  background-size: cover;
}

#variantdb-search-form {
  margin: 0 auto;
  max-width: 425px;
  
  .form__section {
    position: relative;
    
    .search__button {
      width: 125px;
      margin-top: 24px;
    }
  }
}
</style>
