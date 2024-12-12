<template>
    <div>
        <button @click="sortData">Sort Data</button>
        <div ref="chart"></div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import * as d3 from 'd3';

const chart = ref(null);
const data = ref([120, 200, 150, 80, 70, 110, 130]);
const categoryData = ref(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']);

const width = 500;
const height = 300;
const margin = { top: 20, right: 30, bottom: 40, left: 40 };

let svg;

const renderChart = () => {
    // 清除之前的SVG内容
    d3.select(chart.value).select('svg').remove();

    // 创建SVG
    svg = d3.select(chart.value)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    // 设置x轴
    const x = d3.scaleBand()
        .domain(categoryData.value)
        .range([0, width - margin.left - margin.right])
        .padding(0.1);

    svg.append('g')
        .attr('transform', `translate(0,${height - margin.top - margin.bottom})`)
        .call(d3.axisBottom(x));

    // 设置y轴
    const y = d3.scaleLinear()
        .domain([0, d3.max(data.value, d => d)!])
        .nice()
        .range([height - margin.top - margin.bottom, 0]);

    svg.append('g')
        .call(d3.axisLeft(y));

    // 创建柱状图
    svg.selectAll('.bar')
        .data(data.value)
        .enter()
        .append('rect')
        .attr('class', 'bar')
        .attr('x', (_, i) => x(categoryData.value[i])!)
        .attr('y', d => y(d))
        .attr('width', x.bandwidth())
        .attr('height', d => height - margin.top - margin.bottom - y(d))
        .attr('fill', 'steelblue');
};

onMounted(renderChart);

const sortData = () => {
    let swapped;
    const n = data.value.length;
    let i = 0;

    const bubbleSortStep = () => {
        swapped = false;
        for (let j = 0; j < n - i - 1; j++) {
            if (data.value[j] > data.value[j + 1]) {
                [data.value[j], data.value[j + 1]] = [data.value[j + 1], data.value[j]];
                [categoryData.value[j], categoryData.value[j + 1]] = [categoryData.value[j + 1], categoryData.value[j]];
                swapped = true;
            }
        }
        i++;
        renderChart();
        if (swapped && i < n) {
            setTimeout(bubbleSortStep, 500);  // 延迟0.5秒进行下一步排序
        }
    };

    bubbleSortStep();
};
</script>

<style scoped>
.bar {
    fill: steelblue;
}
</style>