<template>
  <div :id="setidentifier" class="highlight-container">
    <span class="visually-hidden">{{ description }}</span>
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'DataHighlightContainer',
  props: ['id', 'description'],
  computed: {
    setidentifier () {
      return this.id.toLowerCase().replace(' ', '') + '-highlights-container'
    }
  }
}
</script>

<style lang="scss">
.highlight-container {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 12px;
  box-sizing: padding-box;
  
  .highlight-box {
    flex-grow: 1;
  }
}
</style>
