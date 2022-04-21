<template>
  <div id="dashboard">
    <Header
      id="dashboard"
      title="COSAS Dashboard"
      subtitle="Monitor and analyze daily imports"
      :imageSrc="images.dashboardImage"
    />
    <main class="dashboard-content">
      <Section id="data-highlights">
        <DataHighlightContainer
          id="cosas"
          description="overview of the cosas database: the number of patients, samples, and experiments"
        >
          <DataHighlightBox
            id="Patients"
            title="Total Patients"
            :value="mostRecentImport.subjects"
          />
          <DataHighlightBox
            id="Samples"
            title="Total Samples"
            :value="mostRecentImport.samples"
          />
          <DataHighlightBox
            id="Experiments"
            title="Total Sequences"
            :value="mostRecentImport.sequencing"
          />
        </DataHighlightContainer>
        <p class="viz-note">Data was last updated on {{ mostRecentImport.date }}</p>
      </Section>
      <Section id="viz">
        <div class="col-sm-12 col-md-10">
          <h2>Database over the last 30 days</h2>
          <p>Data is imported into COSAS at regular intervals. The following table displays the change in values over the last 30 days.</p>
          <p>For more information, see the <a href="/menu/plugins/dataexplorer?entity=cosasreports_imports&hideselect=true">Daily Import</a>table to view the raw data.</p>
        </div>
      </Section>
    </main>
    <div id="dashboard-footer" class="bg-dark footer">
      <img
        :src="images.logo"
        alt="molgenis open source data platform"
        class="molgenis-logo"
      />
    </div>
  </div>
</template>

<script>
import Header from './components/Header.vue'
import Section from './components/Section.vue'
import DataHighlightContainer from './components/DataHighlightContainer.vue'
import DataHighlightBox from './components/DataHighlightBox.vue'
export default {
  data () {
    return {
      reportData: [],
      earliestItem: {},
      images: {
        logo: require('../src/assets/Logo_Blue_Small.png'),
        dashboardImage: require('../src/assets/stairs.jpg')
      }
    }
  },
  components: {
    Header,
    Section,
    DataHighlightBox,
    DataHighlightContainer
  },
  methods: {
    async fetchReportData () {
      const response = await fetch('/api/v2/cosasreports_imports?sort=date:desc&num=30')
      const data = await response.json()
      return data
    },
    async fetchAttributeSummaryData () {
      const response = await fetch('/api/v2/cosasreports_attributesummary')
      const data = await response.json()
      return data
    },
    setMostRecentItem (data) {
      const mostRecentItem = data.items[0]
      mostRecentItem.subjects = mostRecentItem.subjects.toLocaleString('en')
      mostRecentItem.samples = mostRecentItem.samples.toLocaleString('en')
      mostRecentItem.sequencing = mostRecentItem.sequencing.toLocaleString('en')
      this.mostRecentImport = mostRecentItem
    },
    stringAsNumber (value) {
      return typeof value === 'string' ? parseFloat(value.replace(/,/g, '')) : value
    },
    transformReportData (data) {
      const reportData = []
      const dateByMaxAndMinDates = [data.items[0], data.items[data.items.length - 1]]
      dateByMaxAndMinDates.forEach(row => {
        Object.keys(row).forEach(key => {
          if (['subjects', 'samples', 'sequencing'].indexOf(key) > -1) {
            reportData.push({
              category: key,
              date: new Date(row.date),
              value: this.stringAsNumber(row[key])
            })
          }
        })
      })
      // const dateRange = dateByMaxAndMinDates.map(row => row.date)
      
      // data.items.forEach((item, index) => {
      //   reportData.push(
      //     {
      //       group: 'subjects',
      //       index: index,
      //       date: new Date(item.date),
      //       value: this.stringAsNumber(item.subjects)
      //     },
      //     {
      //       group: 'samples',
      //       index: index,
      //       date: new Date(item.date),
      //       value: this.stringAsNumber(item.samples)
      //     },
      //     {
      //       group: 'sequencing',
      //       index: index,
      //       date: new Date(item.date),
      //       value: this.stringAsNumber(item.sequencing)
      //     }
      //   )
      // })
      this.reportData = reportData
    }
  },
  mounted () {
    Promise.all([
      this.fetchReportData(),
      this.fetchAttributeSummaryData()
    ]).then((dailyImportData, attributeSummaryData) => {
      this.setMostRecentItem(dailyImportData[0])
      this.setEarlistItem(dailyImportData[0])
      this.transformReportData(attributeSummaryData[0])
    })
  }
}
</script>

<style lang="scss">
@import './src/styles/base.scss';

.visually-hidden {
  position: absolute;
  clip: rect(1px 1px 1px 1px); /* IE6, IE7 */
  clip: rect(1px, 1px, 1px, 1px);
  overflow: hidden;
  height: 1px;
  width: 1px;
  margin: -1px;
  white-space: nowrap;
}

.viz-note {
  margin-top: 12px;
  font-size: 11pt;
  font-style: italic;
  color: hsl(210, 9%, 47%);
}

#dashboard {
  color: #3f454b;

  .footer {
    padding: 2em 1em;
  }
}

#data-highlights-section {
  background: hsl(0, 0%, 86%);
}

#viz-section {
  background: #f6f6f6;
}

</style>
