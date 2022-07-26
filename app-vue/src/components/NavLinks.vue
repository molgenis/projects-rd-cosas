<template>
  <div class="navlinks">
    <ul>
      <li><router-link :to="{name: 'home'}">Home</router-link></li>
      <li><router-link :to="{name: 'cosas'}">COSAS</router-link></li>
      <li><router-link :to="{name: 'variantdb'}">VariantDB</router-link></li>
      <li><router-link :to="{name: 'help'}">Help</router-link></li>
    </ul>
  </div>
</template>
  
<script>
export default {
  name: 'navigation-links'
}
</script>

<style lang="scss" scoped>
.navlinks {
  ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    
    li {
      box-sizing: content-box;
      margin-left: 16px;
      
      &:first-child {
        margin-left: 0;
      }
      
      a {
        color: currentColor;
        text-decoration: underline;
      }
    }
  }
}
</style>
