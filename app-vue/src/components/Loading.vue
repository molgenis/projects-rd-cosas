<template>
  <div class="loading__box">
    <svg class="icon" aria-hidden="true" width="32" height="24" viewBox="0 0 24 24">
      <circle class="dot" cx="7.5" cy="12.5" r="5" />
      <circle class="dot" cx="11.5" cy="12.5" r="5" />
      <circle class="dot" cx="16.5" cy="12.5" r="5" />
    </svg>
    <p class="message">{{ message }}</p>
  </div>
</template>

<script>
export default {
  name: 'loading-component',
  props: {
    message: {
      type: String,
      required: false,
      default: 'Loading'
    }
  }
}
</script>

<style lang="scss" scoped>
@keyframes blink {
  from {opacity: 0;}
  to {opacity: 1;}
}
.loading__box {
  text-align: center;
  .icon {
    .dot {
      fill: $green-300;
      &:nth-of-type(1) {
        animation: blink 1s 0s infinite;
      }
      &:nth-of-type(2) {
        animation: blink 1s 0.2s infinite;
      }
      &:nth-of-type(3) {
        animation: blink 1s .4s infinite
      }
    }
  }
  .message {
    margin-top: 12px;
  }
}
</style>
