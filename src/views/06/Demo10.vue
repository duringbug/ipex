<!--
 * @Description: 
 * @Author: 唐健峰
 * @Date: 2024-07-08 13:02:26
 * @LastEditors: ${author}
 * @LastEditTime: 2024-07-09 13:08:01
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

const map = ref<L.Map | null>(null);


onMounted(async () => {

    async function getData(path: string, count: number): Promise<any[] | undefined> {
        try {
            const data = await d3.json(path) as any[]
            if (data.length <= count) {
                return data;
            } else {
                const shuffledData = data.sort(() => Math.random() - 0.5);
                return shuffledData.slice(0, count);
            }
        } catch (error) {
            return undefined
        }
    }

    map.value = L.map('leaflet-map').setView([31.227849, 121.400471], 10);
    const data = await getData('06/data.json', 10)
    data?.forEach((value, index) => {
        const marker = L.marker([value.lat, value.lng]).addTo(map.value as any);
        marker.bindPopup(value.time)
    })
    const latlngs = data?.map(item => [item.lat, item.lng]);
    //@ts-ignore
    const heat = L.heatLayer(latlngs, {
        radius: 25, // 设置热力图点的半径
        blur: 15,   // 设置热力图的模糊程度
        maxZoom: 10, // 在地图缩放的最大程度上显示热力图
        gradient: {  // 设置热力图的颜色和透明度
            0: 'rgba(0, 0, 255, 0.1)',   // 蓝色，透明度 0.5
            0.5: 'rgba(0, 255, 0, 0.1)',  // 青柠色，透明度 0.5
            1: 'rgba(255, 0, 0, 0.1)',
        }
    }).addTo(map.value as any);
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
});
</script>

<style scoped></style>