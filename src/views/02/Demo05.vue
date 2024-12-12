<!--
 * @Description: 
 * @Author: 唐健峰
 * @Date: 2024-07-02 13:08:36
 * @LastEditors: ${author}
 * @LastEditTime: 2024-07-02 13:40:34
-->
<template>
    <div>
        <canvas id="pc05" width="690" height="457" style="border:1px solid #c3c3c3;">
            Your browser does not support the canvas element.
        </canvas>
    </div>
    <div>
        <canvas id="pc06" width="564" height="374" style="border:1px solid #c3c3c3;">
            Your browser does not support the canvas element.
        </canvas>
    </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue';
import { readFileAndProcessCSV } from '@/tools/csvReader';

async function renderPc(img: HTMLImageElement, id: string) {
    const canvas = document.getElementById(id) as HTMLCanvasElement;
    const context = canvas.getContext('2d');
    if (context) {
        context.drawImage(img, 0, 0);

        // 获取图片所有像素的颜色信息
        const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
        return imageData;
    } else {
        throw new Error('Failed to getElementByIds')
    }
}


onMounted(async () => {
    try {
        const data = await readFileAndProcessCSV('02/02-AQIData.csv');

        // 格式化数据
        const formattedData = data.map(d => ({
            id: +d.id,
            aqi: +d.aqi,
            lan: +d.lan,
            lng: +d.lng,
            time: +d.time,
            tz: d.tz
        }));

        console.log(formattedData)

        // 练习2载入图片示例代码
        const img_05 = new Image();
        let data_05;
        const img_06 = new Image();
        img_05.src = '02/images/05.jpg';
        img_05.onload = async function () {
            data_05 = await renderPc(img_05, 'pc05');
            const pixelCount = data_05.data.length / 4
            let totalR = 0, totalG = 0, totalB = 0, totalA = 0;
            for (let i = 0; i < pixelCount; i++) {
                const r = data_05.data[i * 4];
                const g = data_05.data[i * 4 + 1];
                const b = data_05.data[i * 4 + 2];
                const a = data_05.data[i * 4 + 3];
                if (i == 200) {
                    console.log(`Pixel ${i}: R=${r}, G=${g}, B=${b}, A=${a}`);
                }
                totalR += r;
                totalG += g;
                totalB += b;
                totalA += a;
            }
            const avgR = totalR / pixelCount;
            const avgG = totalG / pixelCount;
            const avgB = totalB / pixelCount;
            const avgA = totalA / pixelCount;

            console.log(`Average Color: R=${avgR}, G=${avgG}, B=${avgB}, A=${avgA}`);
        };
        img_06.src = '02/images/06.jpg';
        img_06.onload = async function () {
            await renderPc(img_06, 'pc06');
        };
    } catch (error) {
        console.error('Failed to read and process CSV file:', error);
    }
});
</script>

<style scoped>
/* 你可以在这里添加样式 */
</style>