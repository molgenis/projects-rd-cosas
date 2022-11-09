<template>
  <footer class="page-footer">
    <div class="footer-main">
      <div class="footer-main-content">
        <div class="footer-section footer-navigation">
          <p><strong>For Users</strong></p>
          <UnorderedList :noListStyle="true">
            <li><a href="/login">Sign in</a></li>
            <li><router-link :to="{name: 'cosas'}">COSAS Data Finder</router-link></li>
            <li><router-link :to="{name: 'variantdb'}">Variant Data Finder</router-link></li>
          </UnorderedList>
        </div>
        <div class="footer-section footer-navigation">
          <p><strong>For Management</strong></p>
          <UnorderedList :noListStyle="true">
            <li><router-link :to="{name: 'cosasdashboard'}">COSAS Dashboard</router-link></li>
          </UnorderedList>
        </div>
        <div class="footer-section footer-navigation">
          <p><strong>Information</strong></p>
          <UnorderedList :noListStyle="true">
            <li><router-link :to="{name: 'help'}">Frequently Asked Questions</router-link></li>
          </UnorderedList>
        </div>
        <div class="footer-section footer-logos">
          <a href="https://www.molgenis.org">
            <span class="visually-hidden">visit the molgenis website to learn more</span>
            <img
              :src="require('@/assets/molgenis-logo-blue-small.png')"
              alt="molgenis open source data platform"
              class="molgenis_logo"
            />
          </a>
        </div>
      </div>
    </div>
    <div class="footer-meta molgenis-citation">
      <p>This database was created using <a href="https://www.molgenis.org/">MOLGENIS open source software</a> v{{ molgenisVersion }} released on {{ molgenisBuildDate }}.</p>
    </div>
  </footer>
</template>

<script>
import UnorderedList from './Lists.vue'

export default {
  name: 'page-footer',
  components: {
    UnorderedList
  },
  data () {
    return {
      molgenisVersion: null,
      molgenisBuildDate: null
    }
  },
  methods: {
    async fetchData (url) {
      const response = await fetch(url)
      return response.json()
    },
    getAppContext () {
      Promise.all([
        this.fetchData('/app-ui-context')
      ]).then(response => {
        const data = response[0]
        this.molgenisVersion = data.version
        
        const buildDate = new Date(data.buildDate.split(' ')[0])
        const month = buildDate.toLocaleString('default', { month: 'long' })
        const day = buildDate.getDay()
        const year = buildDate.getFullYear()
        this.molgenisBuildDate = `${day} ${month} ${year}`
      })
    }
  },
  mounted () {
    this.getAppContext()
  }
}
</script>

<style lang="scss" scoped>
.page-footer {
  .footer-main {
    box-sizing: padding-box;
    padding: 2em 5em;
    color: $gray-050;
    background-color: $gray-900;
    
    .footer-main-content {
      display: flex;
      justify-content: flex-start;
      align-items: flex-start;
      flex-direction: row;
      flex-wrap: wrap;
      gap: 2em;
      max-width: $max-width;
      margin: 0 auto;
        
      .footer-navigation {
        flex-grow: 2;
      }

      .footer-logos {
        display: flex;
        justify-content: flex-start;
        align-items: flex-start;
        flex-direction: column;
        flex-grow: 1;
        gap: 18px;
      }
    }
  }
  
  .footer-meta {
    box-sizing: padding-box;
    padding: 0.8em;
    background-color: $blue-200;
    
    &.molgenis-citation {
      background-color: $gray-050;
      text-align: center;
      font-size: 10pt;
    }
  }
}
</style>
