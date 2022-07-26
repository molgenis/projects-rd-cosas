<template>
  <div class="form__container">
    <slot></slot>
  </div>
</template>

<script>

export default {
  name: 'form-container'
}
</script>

<style lang="scss" scoped>
.form__container {
  box-sizing: padding-box;
  background-color: $gray-000;
  padding: 2em;
  border-radius: 6px;
  box-shadow: $box-shadow;
  border-top: 5px solid $gray-900;
  border-radius: 0 0 6px 6px;
  max-width: 600px;
  margin: 0 auto;
  margin-bottom: 2em;
}
</style>
