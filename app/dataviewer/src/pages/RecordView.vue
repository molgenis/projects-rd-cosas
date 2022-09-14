<template>
  <div id="record-view" class="app-page">
    <header>
      <h1>Record View</h1>
    </header>
    <main>
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
import SummaryCard from '@/components/SummaryCard'

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
    async getSubjects(limit=2) {
      const query = gql`
      {
        subjects(limit:${limit}) {
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
      return data['subjects']
    },
    async getSubjectMetadata (idString) {
      const query = gql`
      {
        sequencing (filter: {
          belongsToSamplePreparation: {
            belongsToSample: {
              belongsToSubject: {
                subjectID: {
                  equals: [${idString}]
                }
              }
            }
          }
        }) {
          sequencingID
          reasonForSequencing {
            value
          }
          sequencingMethod {
            value
          }
          belongsToSamplePreparation {
            belongsToSample {
              belongsToSubject {
                subjectID
              }
              reasonForSampling {
                value
              }
              biospecimenType {
                value
              }
            }
          }
        }
      }`
      const response = await request('graphql', query)
      console.log(response)
    },
    unpackLinkedSubjectMetadata (data) {
      
    }
  },
  mounted() {
    Promise.all([
      this.getSubjects()
    ]).then(results => {
      const subjectMetadata = results[0]
      this.data = subjectMetadata
      const subjectIDs = subjectMetadata.map(subject => `\"${subject.subjectID}\"`).join(',')
      console.log(subjectIDs)
      this.getSubjectMetadata(subjectIDs)
    // }).then(results => {
    //   const allSubjectData = results[0]
    //   console.log(allSubjectData)
    })
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