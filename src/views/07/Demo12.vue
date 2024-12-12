<!--
 * @Description: 
 * @Author: 唐健峰
 * @Date: 2024-07-08 13:02:26
 * @LastEditors: ${author}
 * @LastEditTime: 2024-07-09 15:17:36
-->
<template>
    <div class="w-full h-full">
        <div id="leaflet-map" style="height: 100vh;"></div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import * as L from 'leaflet';
import 'leaflet.heat/dist/leaflet-heat.js'
import 'leaflet/dist/leaflet.css';
import * as d3 from 'd3'
import { readFileAndProcessCSV } from '@/tools/csvReader'

const map = ref<L.Map | null>(null);
const heatLayer = ref<L.HeatLayer | null>(null);
const markers = ref<L.LayerGroup | null>(null);
let data = [] as any[]

function renderMap(data: any[]) {
    if (map.value && data) {
        // 移除现有的标记和热力图
        if (markers.value) {
            markers.value.clearLayers();
        } else {
            markers.value = L.layerGroup().addTo(map.value as any);
        }
        if (heatLayer.value) {
            map.value.removeLayer(heatLayer.value as any);
        }

        const latlngs = data.map(item => [item.lan, item.lng]);

        // @ts-ignore
        heatLayer.value = L.heatLayer(latlngs, {
            radius: 10, // 设置热力图点的半径
            blur: 10,   // 设置热力图的模糊程度
            maxZoom: 5, // 在地图缩放的最大程度上显示热力图
            gradient: {  // 设置热力图的颜色和透明度
                0: 'rgba(0, 0, 255, 0.1)',   // 蓝色，透明度 0.1
                0.5: 'rgba(0, 255, 0, 0.1)',  // 青柠色，透明度 0.1
                1: 'rgba(255, 0, 0, 0.1)',   // 红色，透明度 0.1
            }
        }).addTo(map.value as any);
    }
}


async function getData(path: string): Promise<any[] | undefined> {
    try {
        const data = await d3.json(path) as any[];
        // 验证数据
        const validatedData = data.filter(item => {
            return typeof item.agencyType === 'number' &&
                typeof item.agencyName === 'string' &&
                typeof item.longitude === 'string' &&
                typeof item.latitude === 'string';
        });
        return validatedData;
    } catch (error) {
        console.error('Error loading or validating data:', error);
        return undefined;
    }
}


async function getAgencyType(type: number, data: any[]): Promise<any[]> {
    const agencyTypeData = data.filter(item => {
        return item.agencyType === type;
    });
    return agencyTypeData;
}

onMounted(async () => {
    map.value = L.map('leaflet-map').setView([31.227849, 121.400471], 10);

    const data0 = await readFileAndProcessCSV('07/t/t0.csv')
    const data1 = await readFileAndProcessCSV('07/t/t1.csv')
    const data2 = await readFileAndProcessCSV('07/t/t2.csv')
    const data3 = await readFileAndProcessCSV('07/t/t3.csv')
    data = [data0, data1, data2, data3];
    if (data) {

        const popup = L.popup();
        function onMapClick(e: any) {
            popup
                .setLatLng(e.latlng)
                .setContent("You clicked the map at " + e.latlng.toString())
                .openOn(map.value as L.Map);
        }
        map.value.on('click', onMapClick);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map.value as L.Map);

        renderMap(data0);

        const timestamp01 = Date.now(); // 获取当前时间戳

        setInterval(async (timestamp02 = Date.now()) => {
            const index = (Math.floor((timestamp02 - timestamp01 + 200) / 1000)) % 4
            renderMap(data[index])
        }, 1000);
    }
});
</script>

<style scoped></style>