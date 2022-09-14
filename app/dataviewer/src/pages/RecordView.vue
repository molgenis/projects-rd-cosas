<template>
  <div id="record-view" class="app-page">
    <header>
      <h1>Record View</h1>
    </header>
    <main>
      <form>
        <CheckboxGroup
          id="datatables"
          :options="datatables"
          title="Select Data Sources"
          caption="Customize the data shown in the cards by selecting one or more of the following options"
        />
      </form>
      <div class="flex">
        <SummaryCard
          v-for="row in data"
          :key="row.subjectID"
          :title="row.subjectID"
          :status="row.subjectStatus.value"
          summaryTitle="Patient Overivew"
          :summaryData="prepRowData(row)"
        />
      </div>
    </main>
  </div>
</template>

<script>
import { request, gql } from 'graphql-request'
import SummaryCard from './SummaryCard'
import CheckboxGroup from './CheckboxGroup.vue'

export default {
  name: 'RecordView',
  components: {
    SummaryCard,
    CheckboxGroup
  },
  data() {
    return {
      data: null,
      datatables: ["diagnoses",'samples','sequences','files']
    }
  },
  methods: {
    prepRowData (row) {
      return Object.keys(row).reduce((newRow, key) => {
        if (typeof row[key] == 'object') {
          newRow[key]=row[key][Object.keys(row[key])[0]]
        } else {
          newRow[key]=row[key]
        }
        return newRow
      }, {})
    },
    async getSubjects() {
      const query = gql`
      {
        subjects(limit:3) {
          subjectID
          belongsToFamily
          subjectStatus {
            value
          }
          genderAtBirth {
            value
          }
          dateOfBirth
          belongsToMother {
            subjectID
          }
          belongsToFather {
            subjectID
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