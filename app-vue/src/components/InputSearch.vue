<template>
  <div>
    <InputLabel :id="id" :label="label" :description="description" />
    <input
      :id="id"
      name="query"
      type="search"
      class="input__search"
      v-model="value"
      @submit.prevent
      @input="$emit('search', value)"
    />
  </div>
</template>

<script>
import InputLabel from './InputLabel.vue'

export default {
  name: 'input-search',
  components: {
    InputLabel
  },
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
  },
  data () {
    return {
      value: null
    }
  }
}
</script>

<style lang="scss" scoped>
.input__search {
  display: block;
  width: 100%;
  background: none;
  border: none;
  border: 1px solid $gray-200;
  padding: 6px;
  padding-left: 12px;
  border-radius: 4px;
  box-shadow: $box-shadow-inset;
  margin: 12px 0;
}
</style>
