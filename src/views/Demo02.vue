<!--
 * @Description: 
 * @Author: 唐健峰
 * @Date: 2024-07-01 13:42:29
 * @LastEditors: ${author}
 * @LastEditTime: 2024-07-06 22:06:34
-->
<template>
    <v-chart class="chart" :option="option" autoresize />
</template>

<script setup lang="ts">
import { readFileAndProcessExcel } from '@/tools/excelReader';
//@ts-ignore
import { use } from 'echarts/core';
//@ts-ignore
import { CanvasRenderer } from 'echarts/renderers';
//@ts-ignore
import { PieChart } from 'echarts/charts';
//@ts-ignore
import {
    //@ts-ignore
    TitleComponent,
    //@ts-ignore
    TooltipComponent,
    //@ts-ignore
    LegendComponent,
} from 'echarts/components';
import VChart, { THEME_KEY } from 'vue-echarts';
import { ref, provide } from 'vue';

use([
    CanvasRenderer,
    PieChart,
    TitleComponent,
    TooltipComponent,
    LegendComponent,
]);

provide(THEME_KEY, 'dark');

let data = ref<any[]>([]);

const option = ref({
    title: {
        text: '增速（%）',
        left: 'center',
    },
    tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b} : {c} %',
    },
    series: [
        {
            name: '增速前十',
            type: 'pie',
            radius: '55%',
            center: ['50%', '60%'],
            data: Array.from({ length: 10 }, () => ({ value: 0, name: '' })),
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)',
                },
            },
        },
    ],
});
readFileAndProcessExcel('/data.xlsx').then((result) => {
    let data = result; // 假设 result 是一个数组
    data.sort((a, b) => b["增速（%）"] - a["增速（%）"]);

    for (let index = 0; index < 10 && index < data.length; index++) {
        option.value.series[0].data[index].value = data[index]["增速（%）"];
        option.value.series[0].data[index].name = data[index]["地区"];
    }
});

</script>

<style scoped>
.chart {
    height: 100vh;
}
</style>