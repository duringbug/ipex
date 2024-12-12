<!--
 * @Description: 
 * @Author: 唐健峰
 * @Date: 2024-07-05 13:44:29
 * @LastEditors: ${author}
 * @LastEditTime: 2024-07-06 22:05:16
-->
<template>
    <div>
        <div ref="chart1" style="width: 100%; height: 400px;"></div>
        <div ref="chart2" style="width: 100%; height: 400px;"></div>
        <div ref="chart3" style="width: 100%; height: 400px;"></div>
        <div ref="chart4" style="width: 100%; height: 400px;"></div>
        <div ref="chart5" style="width: 100%; height: 400px;"></div>
    </div>
</template>

<script setup lang="ts">
import { onMounted, ref, nextTick } from 'vue';
import * as echarts from 'echarts';
import { getWordFre } from '@/tools/httpServer';


const chart1 = ref<HTMLElement | null>(null);
const chart2 = ref<HTMLElement | null>(null);
const chart3 = ref<HTMLElement | null>(null);
const chart4 = ref<HTMLElement | null>(null);
const chart5 = ref<HTMLElement | null>(null);
// 可以根据需要添加更多的 chart 变量

onMounted(async () => {
    const res = await getWordFre();
    const data = res.data;


    await nextTick();

    if (chart1.value) {
        renderChart(chart1.value, data[0]); // 渲染第一组数据的图表
    }

    if (chart2.value) {
        renderChart(chart2.value, data[1]); // 渲染第二组数据的图表
    }

    if (chart3.value) {
        renderChart(chart3.value, data[0]); // 渲染第三组数据的图表
    }

    if (chart4.value) {
        renderChart(chart4.value, data[1]); // 渲染第四组数据的图表
    }

    if (chart5.value) {
        renderChart(chart5.value, data[0]); // 渲染第组数据的图表
    }

    // 可以根据需要继续处理更多的图表
});

function renderChart(chartElem: HTMLElement, data: Record<string, number>) {
    const myChart = echarts.init(chartElem as any);

    const sortedEntries = Object.entries(data)
        .sort((a, b) => b[1] - a[1]); // 按值降序排序

    const sortedKeys = sortedEntries.map(entry => entry[0]);
    const sortedValues = sortedEntries.map(entry => entry[1]);

    const options: echarts.EChartOption = {
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['词频']
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: sortedKeys,
            axisLabel: {
                interval: 0, // 每个标签都显示
                rotate: -45, // 旋转角度，负值表示逆时针旋转
                // 其他配置项可以根据需要添加
            }
        },
        yAxis: {
            type: 'value'
        },
        series: [{
            name: '词频',
            type: 'line',
            data: sortedValues as number[]
        }]
    };

    myChart.setOption(options);
}
</script>

<style scoped>
/* 可以添加一些样式来调整图表的外观 */
</style>