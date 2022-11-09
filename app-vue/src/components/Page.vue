<template>
  <main class="page">
    <slot></slot>
    <PageFooter />
  </main>
</template>

<script>
import PageFooter from '@/components/PageFooter.vue'

export default {
  name: 'uiPage',
  components: { PageFooter }
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
 
  .molgenis_logo {
    width: 124px;
  }
}
</style>
