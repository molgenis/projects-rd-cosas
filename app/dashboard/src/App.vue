<template>
  <div id="dashboard">
    <Header
      id="dashboard"
      title="COSAS Dashboard"
      subtitle="Monitor and analyze daily imports"
      :imageSrc="images.dashboardImage"
    />
    <main class="dashboard-content">
      <Section id="data-highlights" aria-labelledby="cosas-highlights-title">
        <DataHighlightContainer
          id="cosas-highlights"
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
        <p class="viz-note">
          <span v-if="mostRecentImport.date">
            Data was last updated on {{ mostRecentImport.date }}
          </span>
          <span v-else class="text-error">Error: unable to retrieve latest metadata.</span>
        </p>
      </Section>
      <Section
        id="dashboard-cosas-summary"
        class="dashboard-section cosas-data-table"
        aria-labelledby="dashboard-cosas-summary-title"
      >
        <h2 id="dashboard-cosas-summary-title">Database over the last 30 days</h2>
        <p>Data is imported into COSAS at regular intervals. The following table displays the change in values over the last 30 days. For more information, see the <a href="/menu/plugins/dataexplorer?entity=cosasreports_imports&hideselect=true">Daily Import</a> table to view the raw data.</p>
        <DataTable
          tableId="daily-import-summary"
          :data="dailyImportSummary"
          caption="Growth of the COSAS database over the last 30 days"
          :columnOrder="['category','starting.value','final.value', 'difference']"
        />
      </Section>
      <Section
        id="dashboard-coverage-report"
        class="dashboard-section cosas-data-table"
        aria-labelledby="dashboard-coverage-report-title"
      >
        <h2 id="dashboard-coverage-report-title">COSAS Coverage Report</h2>
        <p>How much of the COSAS database is used? COSAS has 6 primary tables, 7 secondary tables, and 24 reference tables. To understand how much data is in COSAS, the following tables provide a summary of the primary tables. This includes the columns that are used and how much data is stored in those columns.</p>
        <p>The data used in the following tables was updated on {{ dateAttributeSummaryDataUpdated }}. If you would like to view the raw data, please follow the link to the <a href="/menu/plugins/dataexplorer?entity=cosasreports_attributesummary&hideselect=true">COSAS Attribute Summary Table</a>.</p>
        <DataTable
          tableId="subject-attributes"
          caption="Summary of subject table attributes"
          :data="attributeSummaryData.subjects"
          :columnOrder="attributeSummaryColumnOrder"
        />
        <DataTable
          tableId="clinical-attributes"
          caption="Summary of clinical table attributes"
          :data="attributeSummaryData.clinical"
          :columnOrder="attributeSummaryColumnOrder"
        />
        <DataTable
          tableId="samples-attributes"
          caption="Summary of sample table attributes"
          :data="attributeSummaryData.samples"
          :columnOrder="attributeSummaryColumnOrder"
        />
        <DataTable
          tableId="sampleprep-attributes"
          caption="Summary of sample preparation table attributes"
          :data="attributeSummaryData.samplePreparation"
          :columnOrder="attributeSummaryColumnOrder"
        />
        <DataTable
          tableId="sequencing-attributes"
          caption="Summary of sequencing table attributes"
          :data="attributeSummaryData.sequencing"
          :columnOrder="attributeSummaryColumnOrder"
        />
      </Section>
    </main>
    <div id="dashboard-footer" class="footer">
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
      dailyImportSummary: {},
      mostRecentImport: {
        subjects: 'NA',
        samples: 'NA',
        sequencing: 'NA'
      },
      attributeSummaryData: {},
      dateAttributeSummaryDataUpdated: null,
      attributeSummaryColumnOrder: [
        'column',
        'expected',
        'actual',
        'difference',
        'complete',
        'key.type'
      ],
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
          'starting.value': this.stringAsNumber(dataFiltered.min[0][column]),
          'final.value': this.stringAsNumber(dataFiltered.max[0][column])
        }
        row.difference = row['final.value'] - row['starting.value']
        return row
      })
    },
    transformAttributeSummaryData (data) {
      this.dateAttributeSummaryDataUpdated = data.items[0].dateLastUpdated
      data.items.forEach(row => {
        if (!this.attributeSummaryData[row.databaseTable]) {
          this.attributeSummaryData[row.databaseTable] = []
        }
        this.attributeSummaryData[row.databaseTable].push({
          column: row.databaseColumn,
          actual: row.countOfValues,
          expected: row.totalValues,
          difference: row.differenceInValues,
          complete: `${row.percentComplete * 100}%`,
          'key.type': row.databaseKey !== undefined ? row.databaseKey.value : ''
        })
      })
    }
  },
  mounted () {
    Promise.all([
      this.fetchData('/api/v2/cosasreports_imports?sort=date:desc&num=30'),
      this.fetchData('/api/v2/cosasreports_attributesummary?')
    ]).then((result) => {
      this.setMostRecentItem(result[0])
      this.transformImportData(result[0])
      this.transformAttributeSummaryData(result[1])
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

.text-error {
  color: hsl(12, 100%, 50%);
  font-weight: 500;
}

#dashboard {
  color: #3f454b;

  .footer {
    padding: 2em 1em;
    background-color: hsl(218, 98%, 8%);
  }

  .dashboard-section {
    width: 90%;
    margin: 0 auto;

    @media screen and (min-width: 972px) {
      max-width: 1024px;
    }
  }
  
}

#data-highlights-section {
  background: hsl(0, 0%, 86%);
}

#dashboard-coverage-report-section {
  table {
    thead {
      font-size: 11ppt;
    }
    tbody {
      td.column-complete {
        text-align: right;
      }
    }
  }
}

</style>
