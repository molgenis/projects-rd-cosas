<template>
  <div class="loading__box">
    <svg class="loading__icon" width="48" height="16" viewBox="0 0 48 16" fill="none" preserveAspectRatio="xMinYMin" xmlns="http://www.w3.org/2000/svg">
      <circle class="dot" cx="8" cy="8" r="6" />
      <circle class="dot" cx="24" cy="8" r="6" />
      <circle class="dot" cx="40" cy="8" r="6" />
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
  .loading__icon {
    width: 72px;
    height: 38px;
    .dot {
      fill: $green-300;
      &:nth-of-type(1) {
        animation: blink 1.1s 0s infinite;
      }
      &:nth-of-type(2) {
        animation: blink 1.1s 0.3s infinite;
      }
      &:nth-of-type(3) {
        animation: blink 1.1s .5s infinite
      }
    }
  }
  .message {
    margin-top: 12px;
  }
}
</style>
