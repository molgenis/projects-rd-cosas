
<template>
  <div class="chart-container grouped-line-chart-container">
    <svg
      :id="chartId"
      width="100%"
      height="100%"
      :viewBox="setViewBox"
      preserveAspectRatio="xMinYMin"
      class="d3-chart d3-grouped-line-chart"
    ></svg>
  </div>
</template>

<script>
import * as d3 from 'd3'

export default {
  name: 'GroupedLineChart',
  props: {
    chartId: {
      type: String,
      required: true
    },
    data: {
      type: Array,
      required: true
    },
    group: {
      type: String,
      required: true
    },
    x: {
      type: String,
      required: true
    },
    y: {
      type: String,
      required: true
    },
    chartWidth: {
      type: Number,
      default: 600
    },
    chartHeight: {
      type: Number,
      default: 375
    },
    chartScaling: {
      type: Number,
      default: 1
    },
    chartMargins: {
      type: Object,
      default: () => ({
        top: 15,
        right: 100,
        bottom: 50,
        left: 40
      })
    }
  },
  data () {
    return {
      chartData: { },
      chartRange: {
        xmin: 0,
        xmax: 0,
        ymin: 0,
        ymax: 100
      }
    }
  },
  computed: {
    setViewBox () {
      return `0 0 ${this.chartWidth * this.chartScaling} ${this.chartHeight}`
    }
  },
  methods: {
    prepChartData (data) {
      this.chartData = d3.groups(data, d => d[this.group])
      this.chartRange.xmin = d3.min(data, d => d[this.x])
      this.chartRange.xmax = d3.max(data, d => d[this.x])
      this.chartRange.ymin = d3.min(data, d => d[this.y])
      this.chartRange.ymax = d3.max(data, d => d[this.y])
    },
    renderChart () {
      const svg = d3.select(`#${this.chartId}`)
      
      const g = svg.append('g')
        .attr('transform', `translate(${this.chartMargins.left}, 0)`)
        .attr('class', 'chart-data-container')

      // define x and y axes
      const x = d3.scaleLinear()
        .domain([this.chartRange.xmin, this.chartRange.xmax])
        .nice()
        .range([0, this.chartWidth - this.chartMargins.left - this.chartMargins.right])
        
      const y = d3.scaleLinear()
        .domain([this.chartRange.ymin, this.chartRange.ymax])
        .nice()
        .range([this.chartHeight - this.chartMargins.top - this.chartMargins.bottom, 0])
          
      // bind axes to svg
      svg.append('g')
        .attr('class', 'chart-axis chart-axis-x')
        .attr('transform', `translate(${this.chartMargins.left}, ${this.chartMargins.top + y(0)})`)
        .call(d3.axisBottom(x))
 
      svg.append('g')
        .attr('class', 'chart-axis chart-axis-y')
        .attr('transform', `translate(${this.chartMargins.left + x(0)}, ${this.chartMargins.top})`)
        .attr(d3.axisLeft(y))
      
      // define line generator
      const lineGenerator = d3.line()
        .x(d => x(d.x))
        .y(d => y(d.y) + this.chartMargins.top)

      // create new <g> for each group
      const lineArea = g.append('g')
        .attr('class', 'chart-data')
        .selectAll('.chart-data')
        .data(this.chartData)
        .enter()
        .append('g')
        .attr('class', 'chart-data-group line-group')
        .attr('data-group', d => d.key)

      // build paths in each <g>
      // const paths = lineArea.append('path')
      lineArea.append('path')
        .attr('d', d => lineGenerator(d.values))
        .attr('data-group', d => d.key)
        .attr('fill', 'none')
        .attr('stroke', '#3f454b')
        .attr('stroke-width', '3px')
        .attr('stroke-linecap', 'round')
        .attr('class', 'grouped-path')
        .attr('stroke-dashoffset', 1000)
        .attr('stroke-dasharray', 1000)
        .transition()
        .delay(250)
        .duration(2000)
        .attr('stroke-dashoffset', 0)

      // create axis labels
      svg.append('text')
        .attr('class', 'chart-text chart-axis-title chart-axis-x')
        .attr('x', (this.chartWidth / 2) + (this.chartMargins.left * -0.4))
        .attr('y', this.chartHeight - (this.chartMargins.bottom * 0.2))
        .attr('text-anchor', 'middle')
        .attr('font-size', '11pt')
        .text(this.x)

      svg.append('text')
        .attr('class', 'chart-text chart-axis-title chart-axis-y')
        .attr('x', (this.chartHeight / 2) + (this.chartMargins.top * -0.4))
        .attr('y', 10)
        .attr('text-anchor', 'middle')
        .attr('font-size', '11pt')
        .attr(this.y)
    }
  },
  mounted () {
    this.prepChartData(this.data)
  },
  updated () {
    console.log('component updated')
    this.renderChart()
  }
}
</script>
