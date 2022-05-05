<template>
  <section class="summary-card" aria-labelledby="">
    <div class="summary-card-header">
      <h3>{{ title }}</h3>
      <div><span>{{ status }}</span></div>
    </div>
    <!-- <div class="summary-card-body">
    </div> -->
  </section>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      required: true
    },
    status: String
  }
}
</script>

<style lang="scss">
.summary-card {
  box-sizing: border-box;
  padding: 1em;
  background-color: #ffffff;
  border-radius: 12px;
  margin: 12px;
  
  .summary-card-header {
    display: flex;
    flex-direction: row;
    align-items: center;
    
    h3 {
      flex: auto;
    }
    
    div {
      box-sizing: padding-box;
      padding: 4px;
      text-align: center;
      border-radius: 24px;
      width: 5rem;
      background-color: #D2F5F9;
      span {
        color: #068D9D;
        font-size: 11pt;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
      }
    }
  }
}
</style>