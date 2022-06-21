<template>
  <fieldset class="radio__group">
    <legend class="input__label">
      {{ name }}
      <span class="input__description" v-if="description">{{ description }}</span>
    </legend>
    <div class="radio__group__item" v-for="(value,index) in values" :key="value">
      <input
        type="radio"
        :id="id + '-' + value"
        :name="name"
        :value="value"
        v-model="selections"
        @change="onChange"
      />
      <label :for="id + '-' + value">
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
  },
  data () {
    return {
      selections: null
    }
  },
  methods: {
    onChange () {
      this.$emit('change', this.selections)
    }
  }
}
</script>

<style lang="scss" scoped>
.input__label {
  display: block;
  color: #252525;
  font-size: 12pt;
}
</style>
