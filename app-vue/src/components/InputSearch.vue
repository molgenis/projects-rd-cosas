<template>
  <div>
    <label :for="id" class="input__label">
      {{ label }}
      <span class="input__description" v-if="description">{{ description }}</span>
    </label>
    <input
      :id="id"
      name="query"
      type="search"
      class="input__search"
      v-model="value"
      @submit="(event) => event.preventDefault()"
      @input="onSearch"
    />
  </div>
</template>

<script>
export default {
  name: 'input-search',
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
  },
  methods: {
    onSearch () {
      this.$emit('search', this.value)
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
  border: 1px solid #bdbdbd;
  padding: 6px;
  padding-left: 12px;
  border-radius: 4px;
  box-shadow: inset 0 2px 4px 0 hsl(0, 0%, 85%);
  margin: 12px 0;
}
</style>
