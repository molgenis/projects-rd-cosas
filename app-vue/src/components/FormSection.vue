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
  margin-bottom: 1.5em;
}
</style>
