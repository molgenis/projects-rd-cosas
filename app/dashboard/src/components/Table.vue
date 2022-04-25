<template>
  <div class="datatable-container">
    <table :id="tableId" class="datatable">
      <caption v-if="caption" class="datatable-caption">{{caption}}</caption>
    </table>
  </div>
</template>

<script>
import * as d3 from 'd3'

export default {
  name: 'DataTable',
  props: {
    tableId: {
      type: String,
      required: true
    },
    data: {
      type: Array,
      required: true
    },
    columnOrder: {
      type: Array,
      required: false
    },
    caption: {
      type: String,
      required: false,
      default: null
    }
  },
  methods: {
    renderTable () {
      // select <table> element
      const tableId = this.$el.childNodes[0].id
      const table = d3.select(`#${tableId}`)
      
      // create <thead> element
      const tableHeader = table.append('thead')
      tableHeader.append('tr')
        .selectAll('th')
        .data(this.columnOrder)
        .enter()
        .append('th')
        .attr('data-column-name', column => column)
        .text(column => column)

      // create <tbody> element
      const tableBody = table.append('tbody')
      const tableRows = tableBody.selectAll('tr')
        .data(this.data)
        .enter()
        .append('tr')
        
      // for each row in the input data, create <td> element
      const tableCells = tableRows.selectAll('tr')
        .data(row => {
          return this.columnOrder.map(column => {
            return { column: column, value: row[column] }
          })
        })
        .enter()
        .append('td')
        .attr('data-value', cell => cell.value)
        .text(cell => cell.value)

      tableCells.attr('class', cell => {
        let css = `column-${cell.column} data-value`
        const type = typeof cell.value
        css += ` value-${type}`
        if (type === 'number') {
          if (cell.value > 0) {
            css += ' value-positive'
          } else if (cell.value < 0) {
            css += ' value-negative'
          } else {
            css += ' value-zero'
          }
        }
        return css
      })
    }
  },
  watch: {
    data () {
      if (this.data) {
        this.renderTable()
      }
    }
  }
}
</script>

<style lang="scss">

$text-dark: #252525;
$text-default: #3f454b;

.datatable-container {
  width: 100%;
  text-align: left;
  color: $text-default;

  .datatable {
    border-spacing: 0;
    
    .datatable-caption {
      caption-side: top;
      font-size: 14pt;
      margin: 12px 0;
      font-weight: 600;
      color: $text-dark;
    }
    
    thead {
      tr {
        th {
          font-weight: 600;
          padding: 4px 12px;
          text-transform: uppercase;
          letter-spacing: 2px;
          border-bottom: 1px solid $text-dark;
          color: $text-dark;
        }
      }
    }
    
    tbody {
      tr {
        td {
          padding: 16px 12px;
          
          &.value-number {
            text-align: right;
          }
        }

        &:nth-child(even) {
          background-color: #f6f6f6;
        }
      }
    }
  }
}
</style>
