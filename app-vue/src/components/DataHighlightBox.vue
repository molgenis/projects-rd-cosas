<template>
  <div :id="id" :aria-labelledby="id + '-title'" class="highlight-box">
    <h3 :id="id + '-title'" class="highlight-box-title">{{ title }}</h3>
    <p class="highlight-box-value">{{ value }}</p>
  </div>
</template>

<script>
export default {
  name: 'DataHighlight',
  props: {
    id: {
      type: String,
      required: true
    },
    title: {
      type: String,
      required: true
    },
    value: {
      type: String,
      required: true
    }
  }
}
</script>

<style lang="scss" scoped>
.highlight-box {
  box-sizing: border-box;
  padding: 16px;
  border-radius: 8px;
  background-color: #7f332d;
  flex-grow: 1;
  box-shadow: 0 0 5px 3px hsla(0, 0%, 0%, 0.2);
  
  .highlight-box-title, .highlight-box-value {
    margin: 0;
  }

  .highlight-box-title {
    font-size: 11pt;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-weight: 600;
    line-height: 1.3;
    color: hsl(4, 48%, 82%);
  }

  .highlight-box-value {
    font-size: 24pt;
    padding: 12px 0;
    text-align: center;
    color: hsl(4, 48%, 98%);
  }
}
</style>
