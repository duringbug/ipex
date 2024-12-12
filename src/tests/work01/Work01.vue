<template>
    <div>
        <div>
            <canvas id="pc" :width="imgAttribute.width" :height="imgAttribute.height" style="border:1px solid #c3c3c3;">
                Your browser does not support the canvas element.
            </canvas>
        </div>
        <div id="chart" style="width: 600px; height: 400px;"></div>
        <NButton @click="toggleChartType">切换图表类型</NButton>
        <canvas id="pc02" :width="imgAttribute02.width" :height="imgAttribute02.height"
            style="border:1px solid #c3c3c3;">
            Your browser does not support the canvas element.
        </canvas>
        <div id="chart02" style="width: 600px; height: 400px;"></div>
        <NButton @click="toggleChartType02">切换图表类型02</NButton>
        <canvas id="pc_origin" :width="imgAttribute.width" :height="imgAttribute.height"
            style="border:1px solid #c3c3c3;">
            Your browser does not support the canvas element.
        </canvas>
        <NButton @click="fetchNextImage">下一张图片</NButton>
    </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue';
import * as echarts from 'echarts'; // 导入ECharts
import { sendRequestToPythonBackend, sendRequestToPythonBackend02 } from '@/tools/httpServer';
import { KMeans, KMeansWithConvergence } from '@/tools/computed';
import { useBackendKMeans } from '@/config/config';
import { NButton } from 'naive-ui';

interface ImgAttribute {
    img: Uint8ClampedArray;
    width: number;
    height: number;
}

const imgAttribute = ref<ImgAttribute>({
    img: new Uint8ClampedArray(0),
    width: 0,
    height: 0
});

const imgAttribute02 = ref<ImgAttribute>({
    img: new Uint8ClampedArray(0),
    width: 0,
    height: 0
});

const chartType = ref<'bar' | 'pie'>('bar'); // 定义 chartType 变量
const chartType02 = ref<'bar' | 'pie'>('bar'); // 定义 chartType02 变量

let currentImageIndex = ref(1); // 当前图片索引

async function renderPc(img: Uint8ClampedArray, id: string) {
    const canvas = document.getElementById(id) as HTMLCanvasElement;
    const context = canvas.getContext('2d');

    if (context) {
        const width = canvas.width;
        const height = canvas.height;

        // 创建 ImageData 对象
        const imageData = new ImageData(img, width, height);

        // 清空 canvas
        context.clearRect(0, 0, width, height);

        // 将图像数据绘制到 canvas 上
        context.putImageData(imageData, 0, 0);
    } else {
        console.error('Unable to get 2D context for canvas');
    }
}

async function getRGBAImageData(imageUrl: string) {
    try {
        // 使用 fetch 获取图像数据
        const response = await fetch(imageUrl);
        const blob = await response.blob();

        // 使用 createImageBitmap 转换为图像位图
        const bitmap = await createImageBitmap(blob);

        // 创建一个 OffscreenCanvas
        const offscreenCanvas = new OffscreenCanvas(bitmap.width, bitmap.height);
        const ctx = offscreenCanvas.getContext('2d');
        if (!ctx) {
            throw new Error('Unable to get 2D context');
        }

        // 在 OffscreenCanvas 上绘制图像位图
        ctx.drawImage(bitmap, 0, 0);

        // 获取图像的像素数据
        const imageData = ctx.getImageData(0, 0, offscreenCanvas.width, offscreenCanvas.height);
        // 更新 imgAttribute 对象的值
        imgAttribute.value = {
            img: imageData.data,
            width: offscreenCanvas.width,
            height: offscreenCanvas.height
        };
        imgAttribute02.value = {
            img: imageData.data,
            width: offscreenCanvas.width,
            height: offscreenCanvas.height
        };
    } catch (error) {
        throw new Error('Error loading image:' + error);
    }
}

async function normalImageData(imageData: Uint8ClampedArray, clusters: number[][]): Promise<Uint8ClampedArray> {
    clusters.forEach((cluster: number[]) => {
        if (cluster.length === 0) {
            return;
        }
        let totalR = 0, totalG = 0, totalB = 0, totalA = 0;
        cluster.forEach((index: number) => {
            totalR += imageData[4 * index];
            totalG += imageData[4 * index + 1];
            totalB += imageData[4 * index + 2];
            totalA += imageData[4 * index + 3];
        });
        const numPixels = cluster.length;
        const avgR = Math.round(totalR / numPixels);
        const avgG = Math.round(totalG / numPixels);
        const avgB = Math.round(totalB / numPixels);
        const avgA = Math.round(totalA / numPixels);
        console.log(`Cluster average RGBA: (${avgR}, ${avgG}, ${avgB}, ${avgA})`);
        cluster.forEach((index: number) => {
            imageData[4 * index] = avgR;
            imageData[4 * index + 1] = avgG;
            imageData[4 * index + 2] = avgB;
            imageData[4 * index + 3] = avgA;
        });
    });
    return imageData;
}

function visualizeClusters(clusters: number[][], imageData: Uint8ClampedArray, chartId: string, chartTypeRef: any) {
    const clusterData = clusters.map((cluster) => {
        let totalR = 0, totalG = 0, totalB = 0, totalA = 0;
        cluster.forEach((index) => {
            totalR += imageData[4 * index];
            totalG += imageData[4 * index + 1];
            totalB += imageData[4 * index + 2];
            totalA += imageData[4 * index + 3];
        });
        const numPixels = cluster.length;
        const avgR = Math.round(totalR / numPixels);
        const avgG = Math.round(totalG / numPixels);
        const avgB = Math.round(totalB / numPixels);
        const avgA = Math.round(totalA / numPixels);

        return {
            color: `rgba(${avgR},${avgG},${avgB},${avgA / 255})`,
            pixelCount: numPixels,
            brightness: (avgR + avgG + avgB) / 3 // 计算亮度
        };
    });

    // 根据亮度排序
    clusterData.sort((a, b) => a.pixelCount - b.pixelCount);

    const chart = echarts.init(document.getElementById(chartId) as HTMLDivElement);
    const option = {
        title: {
            text: 'Cluster Visualization'
        },
        tooltip: {},
        xAxis: {
            type: 'category',
            data: clusterData.map((_, index) => `Cluster ${index + 1}`),
            show: chartTypeRef.value === 'bar'
        },
        yAxis: {
            type: 'value',
            show: chartTypeRef.value === 'bar'
        },
        series: [{
            name: 'Pixel Count',
            type: chartTypeRef.value,
            data: chartTypeRef.value === 'bar' ? clusterData.map((data) => data.pixelCount) : clusterData.map((data, index) => ({
                value: data.pixelCount,
                name: `Cluster ${index + 1}`
            })),
            itemStyle: {
                color: (params: any) => clusterData[params.dataIndex].color
            }
        }]
    };

    chart.setOption(option as any);
}

function toggleChartType() {
    chartType.value = chartType.value === 'bar' ? 'pie' : 'bar';
    visualizeClusters(clusters, imgAttribute.value.img, 'chart', chartType); // 更新图表
}

function toggleChartType02() {
    chartType02.value = chartType02.value === 'bar' ? 'pie' : 'bar';
    visualizeClusters(clusters02, imgAttribute02.value.img, 'chart02', chartType02); // 更新图表
}

let clusters: number[][]; // 声明 clusters 变量
let clusters02: number[][]; // 声明 clusters 变量

async function fetchNextImage() {
    if (currentImageIndex.value) {
        const imageUrl = `02/images/0${currentImageIndex.value % 9}.jpg`;
        await getRGBAImageData(imageUrl);
        renderPc(imgAttribute.value.img, "pc_origin");

        if (useBackendKMeans) {
            clusters = await sendRequestToPythonBackend(imgAttribute.value.img, 50); // 后端获取数据
            clusters02 = await sendRequestToPythonBackend02(imgAttribute02.value.img, 50, imgAttribute02.value.width, imgAttribute02.value.height, 0.98, 0.005, 2);
        } else {
            clusters = await KMeans(imgAttribute.value.img, 100); // 前端调用 KMeans
            clusters02 = await KMeansWithConvergence(imgAttribute02.value.img, 20, imgAttribute02.value.width, imgAttribute02.value.height, 0.98, 0.005, 2);
        }

        const normalImageDataArray = await normalImageData(imgAttribute.value.img, clusters);
        renderPc(normalImageDataArray, "pc");
        const normalImageDataArray02 = await normalImageData(imgAttribute02.value.img, clusters02);
        renderPc(normalImageDataArray02, "pc02");

        // 可视化聚类
        visualizeClusters(clusters, imgAttribute.value.img, 'chart', chartType);
        visualizeClusters(clusters02, imgAttribute02.value.img, 'chart02', chartType02);

        currentImageIndex.value++;
    } else {
        console.log('All images fetched.');
    }
}

onMounted(async () => {
    await fetchNextImage(); // 加载第一张图片
});
</script>

<style scoped></style>
