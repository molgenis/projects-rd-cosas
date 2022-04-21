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
          <p>Data is imported into COSAS at regular intervals. The following table displays the change in values over the last 30 days. For more information, see the <a href="/menu/plugins/dataexplorer?entity=cosasreports_imports&hideselect=true">Daily Import</a> table to view the raw data.</p>
          <DataTable
            tableId="daily-import-summary"
            :data="dailyImportSummary"
            caption="Growth of the COSAS database over the last 30 days"
            :columnOrder="['category','startingValue','finalValue', 'difference']"
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
import DataTable from './components/Table.vue'

export default {
  data () {
    return {
      dailyImportSummary: [],
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
    DataTable
  },
  methods: {
    async fetchData (url) {
      const response = await fetch(url)
      const data = await response.json()
      return data
    },
    setMostRecentItem (data) {
      const firstRow = data.items[0]
      firstRow.subjects = firstRow.subjects.toLocaleString('en')
      firstRow.samples = firstRow.samples.toLocaleString('en')
      firstRow.sequencing = firstRow.sequencing.toLocaleString('en')
      this.mostRecentImport = firstRow
    },
    minDate (data, dateVar) {
      return new Date(Math.min(...data.map(row => new Date(row[dateVar]))))
    },
    maxDate (data, dateVar) {
      return new Date(Math.max(...data.map(row => new Date(row[dateVar]))))
    },
    stringAsNumber (value) {
      return typeof value === 'string' ? parseFloat(value.replace(/,/g, '')) : value
    },
    transformImportData (data) {
      const dateRange = {
        min: this.minDate(data.items, 'date').toISOString().split('T')[0],
        max: this.maxDate(data.items, 'date').toISOString().split('T')[0]
      }
      const dataFiltered = {
        min: data.items.filter(row => row.date === dateRange.min),
        max: data.items.filter(row => row.date === dateRange.max)
      }
      
      const columns = ['subjects', 'samples', 'sequencing']
      this.dailyImportSummary = columns.map(column => {
        const row = {
          category: column,
          startingValue: this.stringAsNumber(dataFiltered.min[0][column]),
          finalValue: this.stringAsNumber(dataFiltered.max[0][column])
        }
        row.difference = row.finalValue - row.startingValue
        return row
      })
    }
  },
  mounted () {
    Promise.all([
      this.fetchData('/api/v2/cosasreports_imports?sort=date:desc&num=30')
    ]).then((dailyImportData) => {
      this.setMostRecentItem(dailyImportData[0])
      this.transformImportData(dailyImportData[0])
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
