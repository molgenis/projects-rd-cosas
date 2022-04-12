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
          <h2>Database at a glance</h2>
          <p>Data is imported into COSAS every day. The following chart shows the change in the total number of subjects, samples, and sequences over the last 30 days. This chart is meant to give an indication of the growth. Actually growth may be difficult to detect visually as the difference between days may be very minimal (i.e., less than 100 cases). Please consult the reports table <a href="/menu/plugins/dataexplorer?entity=cosasreports_imports&hideselect=true">Daily Import </a> to view the raw data.</p>
        </div>
        <div class="col-sm-9">
          <GroupedTimeSeries
            chartId="daily-imports-timeseries"
            :data="reportData"
            group="group"
            x="date"
            y="value"
            xlab="Date"
            ylab=null
          />
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
import GroupedTimeSeries from './components/GroupedTimeSeries.vue'

export default {
  data () {
    return {
      reportData: [],
      mostRecentImport: {},
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
    DataHighlightContainer,
    GroupedTimeSeries
  },
  methods: {
    async fetchReportData () {
      const response = await fetch('/api/v2/cosasreports_imports?sort=date:desc&num=30')
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
      data.items.forEach((item, index) => {
        reportData.push(
          {
            group: 'subjects',
            index: index,
            date: new Date(item.date),
            value: this.stringAsNumber(item.subjects)
          },
          {
            group: 'samples',
            index: index,
            date: new Date(item.date),
            value: this.stringAsNumber(item.samples)
          },
          {
            group: 'sequencing',
            index: index,
            date: new Date(item.date),
            value: this.stringAsNumber(item.sequencing)
          }
        )
      })
      this.reportData = reportData
    }
  },
  mounted () {
    Promise.all([
      this.fetchReportData()
    ]).then((data) => {
      this.setMostRecentItem(data[0])
      this.transformReportData(data[0])
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
