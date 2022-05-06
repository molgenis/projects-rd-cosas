<template>
  <table class="stacked-data-table" role="grid">
    <thead role="presentation">
      <tr role="row">
        <th role="columnheader" v-for="column in Object.keys(data)" :key="column">
          {{ column }}
        </th>
      </tr>
    </thead>
    <tbody role="presentation">
      <tr role="row" v-for="column in Object.keys(data)" :key="column">
        <th role="rowheader">{{ column }}</th>
        <td role="gridcell">{{ data[column] }}</td>
      </tr>
    </tbody>
  </table>
</template>

<script>
export default {
  name: 'StackedDataTable',
  props: {
    columnNames: Array,
    data: {
      type: Object,
      required: false
    }
  }
};
</script>

<style lang="scss">
  .stacked-data-table {
    display: block;
    border-collapse: collapse;
    margin: 12px 0;
    
    thead {
      position: absolute;
      width: 1px;
      height: 1px;
      clip: rect(0, 0, 0, 0);
      clip: rect(0 0 0 0);
      overflow: hidden;
    }
    
    tbody {
      display: block;
      tr {
        display: flex;
        flex-direction: row;
        background-color: #ffffff;
        
        th, td {
          padding: 6px 16px;
        }
        
        th {
          font-weight: 400;
          font-size: 11pt;
          letter-spacing: 0.02em;
          color: #353535;
          width: 50%;
        }
        td {
          width: 50%;
          text-align: right;
          font-weight: 600;
          font-size: 11pt;
          color: #353535;
          letter-spacing: 0.04em;
        }
      }  
    }
  }
</style>