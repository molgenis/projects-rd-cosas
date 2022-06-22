<template>
  <form class="form" @submit="(e) => e.preventDefault()">
    <legend class="form__tile">{{ title }}</legend>
    <div class="form__sections">
      <slot></slot>
    </div>
  </form>
</template>

<script>
export default {
  name: 'ui-form',
  props: {
    title: {
      type: String,
      required: true
    }
  }
}
</script>

<style lang="scss">
.form {
  .form__section {
    box-sizing: border-box;
    padding: 1.25em;
    background-color: #fff;
    margin-bottom: 32px;
    border-radius: 8px;
    box-shadow: 0 0 5px 3px hsla(0, 0%, 0%, 0.08);
  }
  
  .input__label {
    display: block;
    color: #252525;
    
    .input__description {
      display: block;
      font-size: 11pt;
      color: #616365;
    }
  }
}
</style>
