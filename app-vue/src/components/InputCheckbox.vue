<template>
  <div class="checkbox">
    <input
      type="checkbox"
      :id="id"
      class="input__checkbox"
      v-model="choice"
    />
    <label :for="id" class="input__label">{{ label }}</label>
  </div>
</template>

<script>
export default {
  name: 'input-checkbox',
  props: {
    id: {
      type: String,
      required: true
    },
    label: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      choice: null
    }
  },
  methods: {
    onInput () {
      this.$emit('input', this.choice)
    }
  }
}
</script>

<style lang="scss" scoped>
.checkbox {
  display: flex;
  flex-direction: row;
  align-items: center;
  .input__checkbox {
    margin-top: -3px;
    margin-right: 6px;
  }
  
  .input__label {
    line-height: 1.4;
  }
}
</style>
