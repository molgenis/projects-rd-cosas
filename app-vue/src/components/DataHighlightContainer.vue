<template>
  <div :id="id" class="highlight-container">
    <span class="visually-hidden">{{ description }}</span>
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'data-highlight-container',
  props: {
    id: {
      type: String,
      required: true
    },
    description: {
      type: String,
      required: true
    }
  }
}
</script>

<style lang="scss" scoped>
.highlight-container {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 12px;
  box-sizing: padding-box;
}
</style>
