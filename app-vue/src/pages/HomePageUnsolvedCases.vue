<template>
  <Page>
    <Header
      id="ucu-header"
      title="Unsolved Cases Portal"
      subtitle="...."
      :imageSrc="require('@/assets/header-bg-2.jpg')"
    />
    <main>
      <Section id="test">
        <h2>Hello world!</h2>
      </Section>
    </main>
  </Page>
</template>

<script>
import Page from '../components/Page.vue'
import Header from '../components/Header.vue'
import Section from '../components/Section.vue'

export default {
  name: 'cosas-homepage',
  components: {
    Page,
    Header,
    Section
  }
}
</script>
