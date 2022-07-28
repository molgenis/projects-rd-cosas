<template>
  <div class="page">
    <slot></slot>
    <div class="page__footer">
      <div class="logo-navlinks">
        <img
        :src="require('@/assets/molgenis-logo-blue-small.png')"
        alt="molgenis open source data platform"
        class="molgenis_logo"
        />
        <NavLinks />
      </div>
      <p class="molgenis-citation"><small>This database was created using the open source MOLGENIS software {{ molgenisVersion }} on {{ molgenisBuildDate }}</small></p>
    </div>
  </div>
</template>

<script>
import NavLinks from '@/components/NavLinks.vue'
import { fetchData } from '@/utils/search'

export default {
  name: 'uiPage',
  components: {
    NavLinks
  },
  data () {
    return {
      molgenisVersion: null,
      molgenisBuildDate: null
    }
  },
  methods: {
    getAppContext () {
      Promise.all([
        fetchData('/app-ui-context')
      ]).then(response => {
        const data = response[0]
        this.molgenisVersion = data.version
        this.molgenisBuildDate = data.buildDate
      })
    }
  },
  mounted () {
    this.getAppContext()
  }
}
</script>

<style lang="scss">
.mg-page,
.mg-app,
.container-fluid,
.row,
.col-sm-8,
.col-sm-3 {
  padding: 0;
}

.mg-page .mg-page-content {
  margin-top: 0;
}

footer.footer {
  display: none;
}

.page {
  min-height: 100vh;
  background-color: $gray-050;
  
  .page__section__plain {
    background-color: $gray-000;
  }
  
  .page__footer {
    box-sizing: padding-box;
    padding: 2em;
    background-color: $gray-900-alt;
    color: $gray-050;
    
    .logo-navlinks {
      display: flex;
      justify-content: flex-start;
      align-items: center;
      
      .navlinks {
        margin-left: 24px;
      }
    }
    
    .molgenis-citation {
      margin-top: 12px;
      color: $gray-200;
    }
    
    .molgenis_logo {
      width: 124px;
    }
  }
}
</style>
