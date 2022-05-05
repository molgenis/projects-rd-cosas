
<template>
  <div id="__top">
    <router-view :session="session" :page="page" />
  </div>
</template>

<script>

export default {
  data() {
    return {
      session: null,
      page: null
    };
  }
};
</script>

<style lang="scss">
#__top {
  box-sizing: content-box;
  padding: 2em;
  background-color: #f6f6f6;
  min-height: calc(100vh - 4em);
}
</style>