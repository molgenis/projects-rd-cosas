<template>
  <div class="checkbox">
    <input
      :id="id"
      type="checkbox"
      class="checkbox__input"
      v-model="selection"
    />
    <label :for="id" class="checkbox__label">
      {{ label }}
    </label>
  </div>
</template>

<script>
export default {
  name: 'checkbox-input',
  props: {
    id: {
      type: String,
      required: true
    },
    value: {
      type: Boolean,
      default: () => false
    },
    label: {
      type: String,
      required: true
    }
  },
  computed: {
    selection: {
      get () {
        return this.value
      },
      set (value) {
        this.$emit('input', value)
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.checkbox {
  display: flex;
  flex-direction: row;
  align-items: center;
  .checkbox__input {
    margin-top: -3px;
    margin-right: 6px;
  }
  .checkbox__label {
    line-height: 1.4;
  }
}
</style>
