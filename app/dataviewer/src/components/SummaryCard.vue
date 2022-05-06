<template>
  <section class="summary-card" aria-labelledby="">
    <div class="summary-card-header">
      <h3 class="header-title">{{ title }}</h3>
      <div class="header-status status-bubble">
        <span class="status-text">{{ status }}</span>
      </div>
    </div>
    <div class="summary-card-body">
      <h4 class="body-section-title">Patient Summary</h4>
      <StackedDataTable :data="summaryData"/>
      <h4 class="body-section-title">Linked Records</h4>
      <Accordion id="linkedSamples" title="Samples" :titleCount="randomInt()" />
      <Accordion id="linkedSequencingRuns" title="Sequencing Runs" :titleCount="randomInt()"/>
      <Accordion id="linkedFiles" title="Files" :titleCount="randomInt()" />
    </div>
  </section>
</template>

<script>
import StackedDataTable from "./StackedDataTable.vue"
import Accordion from "./Accordion.vue"

export default {
  components: {
    StackedDataTable,
    Accordion
  },
  props: {
    title: {
      type: String,
      required: true
    },
    status: String,
    summaryTitle: String,
    summaryData: Object
  },
  methods: {
    randomInt (max=39) {
      return Math.floor(Math.random() * max)
    }
  }
}
</script>

<style lang="scss">
.status-bubble {
  box-sizing: padding-box;
  padding: 3px;
  text-align: center;
  border-radius: 24px;
  background-color: #f6f6f6;
  
  .status-text {
    color: #3f454b;
    font-size: 10pt;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }
}

.summary-card {
  background-color: #ffffff;
  border-radius: 12px;
  margin: 12px;
  width: 325px;
  max-width: 425px;
  box-shadow: 0 0 4px 2px hsla(0, 0%, 0%, 0.2);
  
  .summary-card-header {
    box-sizing: border-box;
    padding: 1em;
  }
  
  .summary-card-header {
    display: flex;
    position: relative;
    flex-direction: row;
    align-items: center;
    
    .header-title {
      flex: auto;
      font-size: 13pt;
      letter-spacing: 0.06em;
    }
    
    .status-bubble {
      margin-top: -4px;
      width: 4rem;
      background-color: #D2F5F9;
      
      .status-text {
        color: #068D9D;
      }
    }
  }
  .summary-card-body {
    background-color: #f6f6f6;
    padding-top: 6px;

    .body-section-title {
      font-weight: 600;
      color: #5C626A;
      font-size: 12pt;
      letter-spacing: 0.04em;
      margin: 16px 0;
      margin-left: 16px;
    }
  }
}

</style>