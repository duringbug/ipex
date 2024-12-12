<template>
    <canvas id="pc" :width="imgAttribute.width" :height="imgAttribute.height" style="border:1px solid #c3c3c3;">
        Your browser does not support the canvas element.
    </canvas>
    <canvas id="pc02" :width="imgAttribute02.width" :height="imgAttribute02.height" style="border:1px solid #c3c3c3;">
        Your browser does not support the canvas element.
    </canvas>
    <canvas id="pc_origin" :width="imgAttribute.width" :height="imgAttribute.height" style="border:1px solid #c3c3c3;">
        Your browser does not support the canvas element.
    </canvas>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue';
import { sendRequestToPythonBackend, sendRequestToPythonBackend02 } from '@/tools/httpServer'
import { KMeans, KMeansWithPoints, KMeansWithConvergence } from '@/tools/computed'
import { useBackendKMeans } from '@/config/config'

interface imgAttribute {
    img: Uint8ClampedArray
    width: number
    height: number
}

const imgAttribute = ref<imgAttribute>({
    img: new Uint8ClampedArray(0),
    width: 0,
    height: 0
});

const imgAttribute02 = ref<imgAttribute>({
    img: new Uint8ClampedArray(0),
    width: 0,
    height: 0
});

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
            totalR += imageData[4 * index]
            totalG += imageData[4 * index + 1]
            totalB += imageData[4 * index + 2]
            totalA += imageData[4 * index + 3]
        })
        const numPixels = cluster.length;
        const avgR = Math.round(totalR / numPixels);
        const avgG = Math.round(totalG / numPixels);
        const avgB = Math.round(totalB / numPixels);
        const avgA = Math.round(totalA / numPixels);
        console.log(`Cluster average RGBA: (${avgR}, ${avgG}, ${avgB}, ${avgA})`);
        cluster.forEach((index: number) => {
            imageData[4 * index] = avgR
            imageData[4 * index + 1] = avgG
            imageData[4 * index + 2] = avgB
            imageData[4 * index + 3] = avgA
        })
    });
    return imageData
}

onMounted(async () => {
    await getRGBAImageData('02/images/08.jpg')
    renderPc(imgAttribute.value.img, "pc_origin")
    let clusters: number[][];  // 声明 clusters 变量
    let clusters02: number[][];  // 声明 clusters 变量

    if (useBackendKMeans) {
        clusters = await sendRequestToPythonBackend(imgAttribute.value.img, 50);  // 后端获取数据
        clusters02 = await sendRequestToPythonBackend02(imgAttribute02.value.img, 50, imgAttribute02.value.width, imgAttribute02.value.height, 0.98, 0.005, 2)
    } else {
        console.log('begin')
        clusters = await KMeans(imgAttribute.value.img, 20);  // 前端调用 KMeans
        console.log('KMeans end')
        clusters02 = await KMeansWithConvergence(imgAttribute02.value.img, 20, imgAttribute02.value.width, imgAttribute02.value.height, 0.98, 0.002, 2);  // 前端调用 KMeansWithPoints
        console.log('KMeansWithConvergence end')
    }
    imgAttribute.value.img = await normalImageData(imgAttribute.value.img, clusters)
    renderPc(imgAttribute.value.img, "pc")
    imgAttribute02.value.img = await normalImageData(imgAttribute02.value.img, clusters02)
    renderPc(imgAttribute02.value.img, "pc02")
})
</script>

<style scoped></style>