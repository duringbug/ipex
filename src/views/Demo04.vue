<!--
 * @Description: 
 * @Author: 唐健峰
 * @Date: 2024-07-01 19:29:20
 * @LastEditors: ${author}
 * @LastEditTime: 2024-07-02 12:16:04
-->
<template>
    <div ref="container" class="chart-container"></div>
</template>

<script lang="ts" setup>
import * as d3 from 'd3';
import { onMounted, onUnmounted, ref } from 'vue';
import { readFileAndProcessCSV } from '@/tools/csvReader';
import { readFileAndProcessExcel } from '@/tools/excelReader'

const container = ref<HTMLDivElement | null>(null);

interface DataType {
    地区: string;
    '2022GDP（亿元）': number;
    '增速（%）': number;
}
let data: DataType[] = [];

function drawChart(data: DataType[]) {
    if (container.value) {
        container.value.innerHTML = '';
    }
    // 格式化数据
    const formattedData = data.map(d => ({
        city: d.地区,
        gdp: +d['2022GDP（亿元）'],
        rate: +d['增速（%）']
    }));

    const width = container.value?.clientWidth || 1200;
    console.log(container.value?.clientHeight)
    const height = container.value?.clientHeight || 500;
    const marginTop = 20;
    const marginRight = 20;
    const marginBottom = 30;
    const marginLeft = 60;

    const x = d3.scaleBand()
        .domain(data.map(d => d.地区)) // 使用所有地区作为输入域
        .range([marginLeft, width - marginRight])
        .padding(0.1); // 可选的内边距，用于分隔不同的条形或柱形


    // 修改 y 轴的 domain 设置，确保包含所有的 GDP 值
    const y = d3.scaleLinear()
        .domain([0, d3.max(formattedData, d => d.gdp) || 0])  // 确保 domain 范围适当
        .range([height - marginBottom, marginTop]);

    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height);

    svg.append("g")
        .attr("transform", `translate(0,${height - marginBottom})`)
        .call(d3.axisBottom(x));

    svg.append("g")
        .attr("transform", `translate(${marginLeft},0)`)
        .call(d3.axisLeft(y));

    // 修改柱状条形的 y 和 height 属性设置
    svg.selectAll(".bar")
        .data(formattedData)
        .enter().append("rect")
        .attr("class", "bar")
        .attr("x", d => x(d.city) || 0)
        .attr("width", x.bandwidth())
        .attr("y", d => y(Math.max(d.gdp, 0)))  // 使用 Math.max() 确保高度不为负数
        .attr("height", d => Math.abs(y(d.gdp) - y(0)))  // 计算高度时使用绝对值
        .attr("fill", "steelblue");

    // 将SVG元素添加到容器中
    if (container.value) {
        container.value.appendChild(svg.node()!);
    }
}

onMounted(async () => {
    try {
        const data = await readFileAndProcessExcel('data.xlsx');
        drawChart(data)
        window.addEventListener('resize', () => drawChart(data));
    } catch (error) {
        console.error('Failed to read and process XLSX file:', error);
    }
});
onUnmounted(() => {
    window.removeEventListener('resize', () => drawChart(data));
});
</script>

<style scoped>
/* 你可以在这里添加样式 */
.chart-container {
    width: 100%;
    height: 50vh;
}
</style>