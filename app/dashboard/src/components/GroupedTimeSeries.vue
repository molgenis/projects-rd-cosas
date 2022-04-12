
<template>
  <div class="chart-container grouped-time-series-container">
    <svg
      :id="chartId"
      width="100%"
      height="100%"
      :viewBox="viewBox"
      preserveAspectRatio="xMinYMin"
      class="d3-chart d3-time-series-chart"
    ></svg>
  </div>
</template>

<script>
import * as d3 from 'd3'

export default {
  name: 'GroupedTimeSeries',
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
    xlab: {
      type: String
    },
    ylab: {
      type: String
    },
    chartWidth: {
      type: Number,
      default: 600
    },
    chartHeight: {
      type: Number,
      default: 325
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
        left: 50
      })
    }
  },
  data () {
    return {
      chart: null,
      color: '#307473'
    }
  },
  computed: {
    viewBox () {
      return `0 0 ${this.chartWidth * this.chartScaling} ${this.chartHeight}`
    },
    chartData () {
      return Array.from(d3.group(this.data, d => d[this.group]), ([key, value]) => ({ key, value }))
    },
    chartRange () {
      return {
        xmin: d3.min(this.data, d => d[this.x]),
        xmax: d3.max(this.data, d => d[this.x]),
        ymin: d3.min(this.data, d => d[this.y]),
        ymax: d3.max(this.data, d => d[this.y])
      }
    },
    xAxisTitle () {
      return this.xlab ? this.xlab : this.x
    },
    yAxisTitle () {
      return this.ylab ? this.ylab : this.y
    }
  },
  methods: {
    renderChart () {
      if (this.chartData && this.chartRange) {
        console.log(this.chartData)
        this.chart = d3.select(`#${this.$el.childNodes[0].id}`)

        const g = this.chart.append('g')
          .attr('transform', `translate(${this.chartMargins.left}, ${this.chartMargins.top})`)
          .attr('class', 'chart-data-container')

        // define x and y axes
        const xScale = d3.scaleTime()
          .range([0, this.chartWidth - this.chartMargins.left - this.chartMargins.right])
          .domain([new Date(this.chartRange.xmin), new Date(this.chartRange.xmax)])
          
        const yScale = d3.scaleLinear()
          .range([this.chartHeight - this.chartMargins.top - this.chartMargins.bottom, 0])
          // .domain([this.chartRange.ymin, this.chartRange.ymax])
          .domain([0, this.chartRange.ymax])
          .nice()
            
        // bind x axis to chart
        this.chart.append('g')
          .attr('class', 'chart-axis chart-axis-x')
          .attr('transform', `translate(${this.chartMargins.left}, ${yScale(0) + this.chartMargins.top * 1.18})`)
          .call(d3.axisBottom(xScale).ticks(30).tickFormat(d3.timeFormat('%b-%d')))
          .selectAll('text')
          .attr('dx', '-0.3em')
          .attr('dy', '0.75em')
          .attr('text-anchor', 'start')
          .attr('transform', 'rotate(25)')
          .style('font-size', '7pt')

        // bind y axis to chart
        this.chart.append('g')
          .attr('class', 'chart-axis chart-axis-y')
          .attr('transform', `translate(${this.chartMargins.left}, ${this.chartMargins.top * 1.18})`)
          .call(d3.axisLeft(yScale))
        
        // define line generator
        const lineGenerator = d3.line()
          .x(d => xScale(d[this.x]))
          .y(d => yScale(d[this.y]))

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
        lineArea.append('path')
          .attr('d', d => lineGenerator(d.value))
          .attr('data-group', d => d.key)
          .attr('fill', 'none')
          .attr('stroke', this.color)
          .attr('stroke-width', '1px')
          .attr('stroke-linecap', 'round')
          .attr('class', 'grouped-path')
          .attr('stroke-dashoffset', -1000)
          .attr('stroke-dasharray', 1000)
          .transition()
          .delay(50)
          .duration(2000)
          .attr('stroke-dashoffset', 0)
          
        // add end of line labels
        lineArea.append('text')
          .attr('class', 'chart-group-labels line-group-labels')
          .datum(d => {
            return {
              label: d.key,
              value: d.value.splice(-1)[0][this.y]
            }
          })
          .attr('transform', d => `translate(${this.chartWidth - (this.chartMargins.right * 1.45)}, ${yScale(d.value)})`)
          .attr('data-group', d => d.label)
          .attr('dy', '2px')
          .style('font-size', '9pt')
          .style('fill', this.color)
          .style('text-transform', 'capitalize')
          .style('font-weight', '600')
          .text(d => d.label)

        // create axis labels
        if (this.xlab !== 'null') {
          this.chart.append('text')
            .attr('class', 'chart-text chart-axis-title chart-axis-x')
            .attr('x', (this.chartWidth / 2) + (this.chartMargins.left * -0.4))
            .attr('y', this.chartHeight - (this.chartMargins.bottom * 0.2))
            .attr('text-anchor', 'middle')
            .style('font-size', '11pt')
            .text(this.xAxisTitle)
        }

        if (this.ylab !== 'null') {
          this.chart.append('text')
            .attr('class', 'chart-text chart-axis-title chart-axis-y')
            .attr('x', (this.chartMargins.left * 0.4))
            .attr('y', (this.chartHeight / 2) + (this.chartMargins.top * -0.4))
            .attr('text-anchor', 'middle')
            .style('font-size', '11pt')
            .text(this.yAxisTitle)
        }
      }
    }
  },
  watch: {
    chartData () {
      this.renderChart()
    }
  }
}
</script>

<style lang="scss">
.d3-chart {
  .chart-text {
    .chart-axis-title {
      .chart-axis-x {
        .tick {
          text {
            font-size: 9pt;
          }
        }
      }
    }
  }
}
</style>
