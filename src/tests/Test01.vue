<template>
    <div ref="container"></div>
</template>

<script lang="ts" setup>
import * as d3 from 'd3';
import { onMounted, ref } from 'vue';
import { readFileAndProcessCSV } from '@/tools/csvReader';

// 声明图表的尺寸和边距
const width = 928;
const height = 500;
const marginTop = 20;
const marginRight = 30;
const marginBottom = 30;
const marginLeft = 40;

const container = ref<HTMLDivElement | null>(null);

onMounted(async () => {
    try {
        const data = await readFileAndProcessCSV('aapl.csv');

        // 格式化数据
        const formattedData = data.map(d => ({
            date: new Date(d.date),
            close: +d.close
        }));

        // 声明x轴（水平位置）比例尺
        const x = d3.scaleUtc()
            .domain(d3.extent(formattedData, d => d.date) as [Date, Date])
            .range([marginLeft, width - marginRight]);

        // 声明y轴（垂直位置）比例尺
        const y = d3.scaleLinear()
            .domain([0, d3.max(formattedData, d => d.close) as number])
            .range([height - marginBottom, marginTop]);

        // 声明颜色比例尺
        const color = d3.scaleSequential(y.domain(), d3.interpolateTurbo);

        // 声明折线生成器
        const line = d3.line<any>()
            .x(d => x(d.date))
            .y(d => y(d.close));

        // 创建SVG容器
        const svg = d3.create("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", `0 0 ${width} ${height}`)
            .attr("style", "max-width: 100%; height: auto; height: intrinsic;");

        // 添加x轴
        svg.append("g")
            .attr("transform", `translate(0,${height - marginBottom})`)
            .call(d3.axisBottom(x).ticks(width / 80).tickSizeOuter(0));

        // 添加y轴，移除域线，添加网格线和标签
        svg.append("g")
            .attr("transform", `translate(${marginLeft},0)`)
            .call(d3.axisLeft(y).ticks(height / 40))
            .call(g => g.select(".domain").remove())
            .call(g => g.selectAll(".tick line").clone()
                .attr("x2", width - marginLeft - marginRight)
                .attr("stroke-opacity", 0.1))
            .call(g => g.append("text")
                .attr("x", -marginLeft)
                .attr("y", 10)
                .attr("fill", "currentColor")
                .attr("text-anchor", "start")
                .text("↑ Daily close ($)"));

        // 添加颜色渐变
        const gradientId = "gradient";
        svg.append("linearGradient")
            .attr("id", gradientId)
            .attr("gradientUnits", "userSpaceOnUse")
            .attr("x1", 0)
            .attr("y1", height - marginBottom)
            .attr("x2", 0)
            .attr("y2", marginTop)
            .selectAll("stop")
            .data(d3.ticks(0, 1, 10))
            .join("stop")
            .attr("offset", d => d)
            .attr("stop-color", color.interpolator());

        // 添加折线
        svg.append("path")
            .datum(formattedData)
            .attr("fill", "none")
            .attr("stroke", `url(#${gradientId})`)
            .attr("stroke-width", 1.5)
            .attr("stroke-linejoin", "round")
            .attr("stroke-linecap", "round")
            .attr("d", line);

        // 将SVG元素添加到容器中
        if (container.value) {
            container.value.appendChild(svg.node()!);
        }
    } catch (error) {
        console.error('Failed to read and process CSV file:', error);
    }
});
</script>

<style scoped>
/* 你可以在这里添加样式 */
</style>