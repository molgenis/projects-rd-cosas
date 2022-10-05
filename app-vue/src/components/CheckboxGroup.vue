<template>
  <div class="checkbox__group">
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'checkbox-group'
}
</script>

<style lang="scss" >
.checkbox__group {
  div {
    display: flex;
    flex-direction: row;
    align-items: center;
    input[type="checkbox"] {
      margin-top: -3px;
      margin-right: 6px;
    }
    label {
      line-height: 1.4;
    }
  }
}
</style>
