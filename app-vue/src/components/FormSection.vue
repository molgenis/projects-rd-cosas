<template>
  <div class="form__section">
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'form-section'
}
</script>

<style lang="scss" scoped>
.form__section {
  box-sizing: border-box;
  padding-top: 4px;
}
</style>
