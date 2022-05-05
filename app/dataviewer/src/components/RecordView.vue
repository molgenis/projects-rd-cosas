<template>
  <div id="record-view" class="app-page">
    <header>
      <h1>Record View</h1>
    </header>
    <main>
      {{ data }}
      <div class="flex">
        <SummaryCard title="Test 1" status="Hello"></SummaryCard>
        <SummaryCard title="Test 2" status="Hello"></SummaryCard>
      </div>
    </main>
  </div>
</template>

<script>
import { request, gql } from 'graphql-request'
import SummaryCard from './SummaryCard'

export default {
  name: 'RecordView',
  components: {
    SummaryCard
  },
  data() {
    return {
      data: null
    }
  },
  methods: {
    async getSubjects() {
      const query = gql`
      {
        subjects(limit:10) {
          subjectID
          belongsToFamily
          subjectStatus {
            value
          }
        }
      }
      `
      const data = await request('graphql', query)
      this.data = data['subjects']
    }
  },
  mounted() {
    this.getSubjects()
  }
};
</script>

<style lang="scss">
.flex {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  margin: 16px 0;
  gap: 12px;
  & > * {
    flex: auto;
  }
}
</style>