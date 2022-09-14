
<template>
  <div>
    <nav class="navbar">
      <ul class="navbar-links">
        <li>
          <router-link :to="{name: 'recordView'}">
            Record Viewer
          </router-link>
        </li>
      </ul>
    </nav>
    <div id="__top">
      <router-view :session="session" :page="page" />
    </div>
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

.navbar {
  .navbar-links {
    list-style: none;
    padding: 0;
    margin: 0;
  }
}
</style>