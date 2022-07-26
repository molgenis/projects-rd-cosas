<template>
  <Page>
    <Header
      id="helpHeader"
      title="Help"
      subtitle="Frequently asked questions, troubleshooting issues, and more"
    />
    <Section id="troubleshooting-searches">
      <h2>Troubleshooting Search Queries</h2>
      <p>In this section, you can find information on how to resolve issues with the search and what error messages mean. In the event that something goes wrong during a search, an error message will be displayed below the search button. The message will give you an error code, reason, and the URL that was used to search. This information is useful for diagnosing potential bugs or other issues. If you encounter any issues, take a look at the questions below.</p>
      <h3>I've received the message "Found 0 records". What does this mean?</h3>
      <p>The message "Found 0 records" means that there are no matching records in the database based on the search criteria that you provided. Make sure the value is entered correctly, try entering a new value, or adjusting the filters. If you continue to receive zero results, then it is likely that the data is not yet available in a database.</p>
      <h3>My search returns a "Bad Request (400)" error. How do I correct this?</h3>
      <p>This error occurrs when all search fields are blank. Make sure at least one of the search fields is filled in or selected.</p>
    </Section>
  </Page>
</template>

<script>
import Page from '@/components/Page.vue'
import Header from '@/components/Header.vue'
import Section from '@/components/Section.vue'

export default {
  name: 'troubleshooting-page',
  components: {
    Page,
    Header,
    Section
  }
}
</script>

<style lang="scss" scoped>
</style>
