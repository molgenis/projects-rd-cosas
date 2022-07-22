<template>
  <label :for="id" class="input__label">
    <span>{{ label }}</span>
    <span class="input__description">{{ description }}</span>
  </label>
</template>

<script>
export default {
  name: 'input-label',
  props: {
    id: {
      type: String,
      required: true
    },
    label: {
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
.input__label {
  display: block;
  color: $gray-900;
  
  .input__description {
    display: block;
    font-size: 11pt;
    color: $gray-400;
  }
}
</style>
