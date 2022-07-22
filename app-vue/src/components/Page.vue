<template>
  <div class="page">
    <slot></slot>
    <div class="page__footer">
      <img :src="MolgenisLogo" alt="molgenis open source data platform" class="molgenis_logo"/>
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'uiPage',
  data () {
    return {
      MolgenisLogo: require('@/assets/molgenis-logo-blue-small.png')
    }
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
    padding: 2em 1em;
    background-color: $gray-900-alt;
    
    .molgenis_logo {
      width: 124px;
    }
  }
}
</style>
