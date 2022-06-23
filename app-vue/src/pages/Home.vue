<template>
  <Page>
    <Header
      id="cosas-header"
      title="Genetica Diagnostics Portal"
      subtitle="Find, explore, and access data"
      :imageSrc="require('@/assets/header-bg-2.jpg')"
    />
    <main>
      <Section id="portal-welcome" aria-labelledby="portal-welcome-title" class="page__section__plain">
        <h2 id="portal-welcome-title" class="text-center">Welcome</h2>
          <p>Through the <strong>Genetica Diagnostics Portal</strong>! With this site, you can access a number of databases and systems available to members of the genetica department developed by the Molgenis team.</p>
      </Section>
      <Section id="portal-databases" aria-labelledby="portal-databases-title">
        <h2 id="portal-databases-title" class="text-center">View Databases</h2>
        <p>
          Sign in to any of the following databases using your UMCG
          credentials. If you have been given access to a system and it isn't
          in the list below, contact
          <a href="mailto:molgenis-support@umcg.nl"
            >molgenis-support@umcg.nl</a
          >.
        </p>
        <div id="database-cards">
          <InfoCard
            title="COSAS"
            text="View the Catalog of Sequences, Arrays, and Samples."
          >
            <router-link :to="{name: 'cosas'}" class="action-link">
              View
            </router-link>
          </InfoCard>
          <InfoCard
            title="Unsolved Cases"
            text="View and submit cases to the Unsolved Cases Portal."
          >
            <router-link :to="{name: 'ucu'}" class="action-link">
              View
            </router-link>
          </InfoCard>
          <InfoCard
            title="VariantDB"
            text="Find and explore variants in the Variants database."
          >
            <router-link :to="{name: 'variantdb'}" class="action-link">
              View
            </router-link>
          </InfoCard>
        </div>
      </Section>
      <Section id="portal-help" aria-labelledby="portal-help-title" class="page__section__plain">
        <h2 id="portal-help-title">Get help</h2>
        <p>Need help? Do you have a question about any of these systems? If so, please contact the support desk.</p>
        <ActionLink href="mailto:molgenis-support@umcg.nl" style="width: 225px;">
          Contact Support
        </ActionLink>
      </Section>
    </main>
  </Page>
</template>

<script>
import Page from '../components/Page.vue'
import Header from '../components/Header.vue'
import Section from '../components/Section.vue'
import InfoCard from '../components/InfoCard.vue'
import ActionLink from '../components/ActionLink.vue'

export default {
  name: 'gcc-home',
  components: {
    Page,
    Header,
    Section,
    InfoCard,
    ActionLink
  }
}
</script>

<style>
#portal-databases {
  background-color: #f6f6f6;
}

#database-cards {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  gap: 12px;
}

#portal-help {
  text-align: center;
}

</style>
