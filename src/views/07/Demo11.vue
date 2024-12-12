<!--
 * @Description: 
 * @Author: 唐健峰
 * @Date: 2024-07-08 13:02:26
 * @LastEditors: ${author}
 * @LastEditTime: 2024-07-09 13:42:37
-->
<template>
    <div class="top-0 right-0 bg-blue-500 text-white p-4">
        <n-space vertical>
            <n-select v-model:value="value" :options="options" @update:value="handleSelect" />
        </n-space>
    </div>
    <div class="w-full h-full">
        <div id="leaflet-map" style="height: 100vh;"></div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
import * as L from 'leaflet';
import 'leaflet.heat/dist/leaflet-heat.js'
import 'leaflet/dist/leaflet.css';
import * as d3 from 'd3'
import { NSpace, NSelect } from 'naive-ui'

const map = ref<L.Map | null>(null);
const heatLayer = ref<L.HeatLayer | null>(null);
const markers = ref<L.LayerGroup | null>(null);

const value = ref(null);
const options = ref([
    { label: '养老机构', value: 1 },
    { label: '长者照护之家', value: 2 },
    { label: '老年日间照护机构', value: 3 },
    { label: '助餐服务点', value: 4 },
    { label: '社区养老服务组织', value: 5 },
    { label: '社区综合为老服务中心', value: 6 },
    { label: '护理站', value: 7 },
    { label: '护理院', value: 8 },
]);

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

// 处理选择事件
async function handleSelect(val: number) {
    console.log('Selected value:', val);
    if (map.value) {
        const data = await getData('07/06-NursingHome-SH.json');
        if (data) {
            const filteredData = await getAgencyType(val, data);
            renderMap(filteredData);
        }
    }
}

// 渲染地图
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

        data.forEach((value) => {
            const marker = L.circleMarker([value.latitude, value.longitude]).addTo(markers.value as L.LayerGroup);
            marker.bindPopup(value.agencyName);
        });

        const latlngs = data.map(item => [item.latitude, item.longitude]);

        // @ts-ignore
        heatLayer.value = L.heatLayer(latlngs, {
            radius: 25, // 设置热力图点的半径
            blur: 15,   // 设置热力图的模糊程度
            maxZoom: 10, // 在地图缩放的最大程度上显示热力图
            gradient: {  // 设置热力图的颜色和透明度
                0: 'rgba(0, 0, 255, 0.1)',   // 蓝色，透明度 0.1
                0.5: 'rgba(0, 255, 0, 0.1)',  // 青柠色，透明度 0.1
                1: 'rgba(255, 0, 0, 0.1)',   // 红色，透明度 0.1
            }
        }).addTo(map.value as any);
    }
}


onMounted(async () => {
    map.value = L.map('leaflet-map').setView([31.227849, 121.400471], 10);
    const data = await getData('07/06-NursingHome-SH.json');
    if (data) {
        renderMap(data);
    }

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