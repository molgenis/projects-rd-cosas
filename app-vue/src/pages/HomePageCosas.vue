<template>
  <Page>
    <Header
      id="cosas-header"
      title="COSAS"
      subtitle="Search the COSAS Database"
      :imageSrc="require('@/assets/header-bg-2.jpg')"
    />
    <main>
      <Section id="quick-links" style="text-align: center;" class="page__section__plain">
        <h2>Quick Links</h2>
        <p>Scroll down to learn more about COSAS or use the links below to view a specific page.</p>
        <router-link :to="{name: 'cosasdashboard'}" class="action-link" style="width: 250px;">
          COSAS Dashboard
        </router-link>
      </Section>
      <Section id="cosas-search-form">
        <!-- <h2>Search the COSAS Database</h2>
        <p>Search for specific records or apply filters to create subsets of the data.</p> -->
        <Form
          id="cosas-files-search-form"
          class="cosas-search-form"
          title="Search for Files"
          description="Find specific records using one or more of the filters below. You can also search for multiple values at a time. To do so, format the values with a comma e.g., 'value 1, value 2, ...'."
        >
          <FormSection>
            <SearchInput
              id="subjectID"
              label="Search for patients"
              description="Enter MDN/UMCGnr"
              @search="(value) => fileFilters.subjectID = value"
            />
          </FormSection>
          <FormSection>
            <SearchInput
              id="belongsWithFamilyMembers"
              label="Search for family members"
              description="Enter MDN/UMCGnr of the patient's mother, father, siblings, etc."
              @search="(value) => fileFilters.belongsWithFamilyMembers = value"
            />
          </FormSection>
          <SearchButton id="search-subjects" @click="searchFiles"/>
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
              @search="(value) => clinicalBelongsToSubject = value"
            />
          </FormSection>
          <FormSection>
            <SearchInput
              id="clinicalObservedPhenotype"
              label="Klinisch Fenotype (HPO)"
              description="Enter one or more HPO codes, e.g., 'HP:0001270,HP:0001638'"
              @search="(value) => clinicalObservedPhenotype = value"
            />
          </FormSection>
          <SearchButton id="search-clinical" />
        </Form>
      </Section>
    </main>
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

import { removeNullObjectKeys, objectToUrlFilterArray } from '../utils/search.js'

export default {
  name: 'cosas-homepage',
  components: {
    Page,
    Header,
    Section,
    Form,
    FormSection,
    SearchButton,
    SearchInput
  },
  data () {
    return {
      fileFilters: {
        subjectID: null,
        belongsWithFamilyMembers: null
      }
    }
  },
  methods: {
    searchFiles () {
      const filters = removeNullObjectKeys(this.fileFilters)
      const filterUrl = objectToUrlFilterArray(filters)
      console.log(filterUrl)
    }
  }
}
</script>

<style lang="scss" scoped>
.cosas-search-form {
  border-top-color: #7EA172;
}
</style>
