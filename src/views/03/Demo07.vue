<template>
    <div class="flex flex-col items-center">
        <n-button class="text-orange-500" type="tertiary" @click="handleClick">
            点击
        </n-button>
        <div v-if="showChart1" ref="chartRef" :style="{ width: chartWidth, height: '100vh' }"></div>
        <div v-if="showChart2" ref="chartRef02" :style="{ width: chartWidth, height: '100vh' }"></div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, onBeforeUnmount } from 'vue';
import * as echarts from 'echarts';
import * as d3 from 'd3';
import { readFileAndProcessCSV } from '../../tools/csvReader';
import { NButton } from 'naive-ui';

interface AQIData {
    aqi: number;
    id: number;
    lan: number;
    lng: number;
    time: number;
    tz: string;
}

const aqiData = ref<AQIData[]>([]);
const chartRef = ref<HTMLDivElement | null>(null);
const chartRef02 = ref<HTMLDivElement | null>(null);
const chartWidth = ref<string>('100%');
const showChart1 = ref<boolean>(false);
const showChart2 = ref<boolean>(false);

function renderChart() {
    if (chartRef.value) {
        echarts.dispose(chartRef.value);
        const chartInstance = echarts.init(chartRef.value);
        const options = {
            title: {
                text: 'AQI Scatter Plot 1',
            },
            tooltip: {
                trigger: 'item',
                formatter: (params: any) => {
                    return `AQI: ${params.value[2]}<br>Longitude: ${params.value[0]}<br>Latitude: ${params.value[1]}`;
                },
            },
            xAxis: {
                type: 'value',
                name: 'Longitude',
                scale: true
            },
            yAxis: {
                type: 'value',
                name: 'Latitude',
                scale: true
            },
            series: [
                {
                    name: 'AQI',
                    type: 'scatter',
                    symbolSize: (data: number[]) => data[2] / 30,
                    data: aqiData.value.map((item) => [item.lng, item.lan, item.aqi]),
                },
            ],
        };
        chartInstance.setOption(options as any);
    }
}

function renderD3Chart() {
    if (chartRef02.value && aqiData.value.length > 0) {
        const margin = { top: 20, right: 30, bottom: 30, left: 40 };
        const width = chartRef02.value.clientWidth - margin.left - margin.right;
        const height = chartRef02.value.clientHeight - margin.top - margin.bottom;

        d3.select(chartRef02.value).select('svg').remove();

        const svg = d3.select(chartRef02.value)
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        // 设置 x 轴比例尺
        const x = d3.scaleLinear()
            .domain([70, 140])  // x 轴范围从 70 到 140
            .range([0, width]);

        // 设置 y 轴比例尺
        const y = d3.scaleLinear()
            .domain([15, 55])   // y 轴范围从 15 到 55
            .range([height, 0]);

        svg.selectAll('circle')
            .data(aqiData.value)
            .enter().append('circle')
            .attr('cx', d => x(d.lng))
            .attr('cy', d => y(d.lan))
            .attr('r', d => Math.sqrt(d.aqi) / 3)
            .attr('fill', d => `rgba(70, 130, 180, ${Math.min(d.aqi / 200, 1)})`);  // 设置填充颜色和透明度

        svg.append('g')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(x).tickSizeOuter(0));

        svg.append('g')
            .call(d3.axisLeft(y).tickSizeOuter(0));
    }
}

function handleResize() {
    renderChart();
    renderD3Chart();
}

function handleClick() {
    if (!showChart2.value && !showChart1.value) {
        showChart1.value = true
        nextTick(() => {
            renderChart();
        });
    } else if (!showChart2.value && showChart1.value) {
        showChart2.value = true
        nextTick(() => {
            renderD3Chart();
        });
    }
}

onMounted(async () => {
    const result = await readFileAndProcessCSV('/03/02-AQIData.csv');
    aqiData.value = result;
    await nextTick(); // 确保DOM元素已经渲染完毕
    renderChart();
    renderD3Chart();

    window.addEventListener('resize', handleResize);
});

onBeforeUnmount(() => {
    window.removeEventListener('resize', handleResize);
});

</script>

<style scoped></style>
<!-- npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p -->
