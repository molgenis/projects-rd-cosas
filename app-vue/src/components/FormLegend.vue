<template>
  <legend class="form__legend">
    {{ title }}
    <span v-if="description" class="form__legend__description">{{ description }}</span>
  </legend>
</template>

<script>
export default {
  name: 'form-legend',
  props: {
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      required: false
    }
  }
}
</script>

<style lang="scss" scoped>
.form__legend {
  font-size: 12pt;
  color: $body-heading;
  
  .form__legend__description {
    display: block;
    font-size: 11pt;
    color: $body-caption;
  }
}
</style>
