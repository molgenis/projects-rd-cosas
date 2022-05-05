<template>
  <div>
    <h1>Hello World</h1>
    <button id="counter" @click="plusOne">{{ count }}</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      count: 0,
    };
  },
  methods: {
    plusOne() {
      this.count++;
    },
  },
};
</script>

<style lang="scss">

</style>