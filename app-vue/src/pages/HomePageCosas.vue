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
        <router-link to="/cosas-dashboard" class="action-link" style="width: 250px;">
          COSAS Dashboard
        </router-link>
      </Section>
      <Section id="cosas-search">
        <h2>Search the COSAS Database</h2>
        <p>Search for specific records or apply filters to create subsets of the data.</p>
        <Form id="cosas-search-form" title="Search for Patients" class="flex__form">
          <FormSection>
            <SearchInput
              id="subjectID"
              label="UMCGnummer"
              description="Search for a particular UMCGnr"
              @search="(value) => subjectsSubjectID = value"
            />
            <SearchButton
              id="search-subject-id"
              @click="() => onClick('umdm_subjects', 'subjectID', subjectsSubjectID)"
            />
          </FormSection>
          <FormSection>
            <SearchInput
              id="belongsToFamily"
              label="Familienummer"
              description="Find for patients by familienummer"
              @search="(value) => subjectsBelongsToFamily = value"
            />
            <SearchButton
              id="search-subject-belongs-to-family"
              @click="() => onClick('umdm_subjects', 'belongsToFamily', subjectsBelongsToFamily)"
            />
          </FormSection>
          <FormSection>
            <SearchInput
              id="belongsToMother"
              label="Moeder"
              description="Find patients by the mother's UMCGnr"
              @search="(value) => subjectsBelongsToMother = value"
            />
            <SearchButton
              id="search-subject-belongs-to-mother"
              @click="() => onClick('umdm_subjects', 'belongsToMother', subjectsBelongsToMother)"
            />
          </FormSection>
          <FormSection>
            <SearchInput
              id="belongsToFather"
              label="Vader"
              description="Find patients by the father's UMCGnr"
              @search="(value) => subjectsBelongsToFather = value"
            />
            <SearchButton
              id="search-subject-belongs-to-father"
              @click="() => onClick('umdm_subjects', 'belongsToFather', subjectsBelongsToFather)"
            />
          </FormSection>
        </Form>
        <Form
          id="cosas-search-form"
          title="Search for Diagnostic Information"
          class="flex__form"
        >
          <FormSection>
            <SearchInput
              id="clinicalSubjectID"
              label="UMCGnummer"
              description="Search for a particular UMCGnr"
              @search="(value) => clinicalBelongsToSubject = value"
            />
            <SearchButton
              id="search-clinical-belongsToSubject"
              @click="() => onClick('umdm_clinical', 'belongsToSubject', clinicalBelongsToSubject)"
            />
          </FormSection>
          <FormSection>
            <SearchInput
              id="clinicalObservedPhenotype"
              label="Klinisch Fenotype (HPO)"
              description="Enter one or more HPO codes, e.g., 'HP:0001270,HP:0001638'"
              @search="(value) => clinicalObservedPhenotype = value"
            />
            <SearchButton
              id="search-clinical-belongsToSubject"
              @click="() => onClick('umdm_clinical', 'observedPhenotype', clinicalObservedPhenotype, 'in')"
            />
          </FormSection>
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
  methods: {
    onClick (table, column, value, filterType) {
      const input = value.replaceAll(' ', '')
      const urlFilter = (typeof filterType !== 'undefined') && (filterType === 'in')
        ? `${column}==in=(${input})`
        : `${column}==${input}`

      this.windowReplaceUrl(table, urlFilter)
    },
    windowReplaceUrl (table, array) {
      const filtersEncoded = encodeURIComponent(array)
      
      const baseUrl = `/menu/plugins/dataexplorer?entity=${table}&mod=data&hideselect=true`
      const url = baseUrl + '&filter=' + filtersEncoded
      // window.location.replace(url)
      console.log(url)
    }
  }
}
</script>

<style lang="scss">
.flex__form {
  margin-bottom: 24px;

  .form__sections {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    // justify-content: center;
    align-items: flex-start;
    gap: 32px;
    
    .form__section {
      margin: 0;
      width: 300px;
    }
  }
}
</style>
