<template>
  <fieldset class="radio__group">
    <legend class="input__label">
      {{ name }}
      <span class="input__description" v-if="description">{{ description }}</span>
    </legend>
    <div class="radio__group__item" v-for="(value,index) in values" :key="value">
      <label :for="id + '-' + value">
        <input
          type="radio"
          :name="name"
          :id="id + '-' + value"
          :value="value"
          @change="$emit('input', value)"
        />
        {{ labels ? labels[index] : value }}
      </label>
    </div>
  </fieldset>
</template>

<script>
export default {
  name: 'radio-buttons',
  props: {
    id: {
      type: String,
      required: true
    },
    name: {
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
    },
    values: {
      type: Array,
      required: true
    },
    labels: {
      type: Array,
      required: false
    }
  }
}
</script>

<style lang="scss" scoped>
.input__label {
  display: block;
  color: $gray-900;
  font-size: 12pt;
  
  .input__description {
    display: block;
    font-size: 11pt;
    color: $gray-500;
  }
}
</style>
