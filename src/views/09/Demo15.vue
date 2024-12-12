<!--
 * @Description: 
 * @Author: 唐健峰
 * @Date: 2024-07-11 13:39:56
 * @LastEditors: ${author}
 * @LastEditTime: 2024-07-11 14:06:05
-->
<template>
    <div>
        <div class="flex items-center justify-center">
            <NInputNumber v-model:value="x" size="small"></NInputNumber>
            <NInputNumber v-model:value="y" size="small"></NInputNumber>
            <NInputNumber v-model:value="z" size="small"></NInputNumber>
        </div>
        <div class="flex items-center justify-center">
            <div class="w-56 bg-orange-500 text-center text-xl rounded-lg">{{ v['volume'] }}</div>
        </div>
    </div>
</template>
<script setup lang="ts">
import { sendRequestToTest } from '@/tools/httpServer'
import { ref, onMounted, watch } from 'vue';
import { NInputNumber } from 'naive-ui';
interface VolumeResponse {
    volume: number;
}
const v = ref<VolumeResponse>({ volume: 0 });
const x = ref<number>(0);
const y = ref<number>(0);
const z = ref<number>(0);
async function getVolume(x: number, y: number, z: number) {
    v.value = await sendRequestToTest(x, y, z)
}

watch([x, y, z], () => {
    getVolume(x.value, y.value, z.value);
});

onMounted(async () => {
    getVolume(x.value, y.value, z.value)
})
</script>
<style scoped></style>