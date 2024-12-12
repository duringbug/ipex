<!--
 * @Description: 
 * @Author: 唐健峰
 * @Date: 2023-10-08 14:36:56
 * @LastEditors: ${author}
 * @LastEditTime: 2024-07-14 16:55:00
-->
<template>
  <div class="flex justify-evenly items-center bg-sky-300 text-2xl font-bold">
    <div class="border-2 py-2 hover:border-amber-400 px-2 underline">
      <router-link to="/work04" class=" hover:text-red-500">
        <div>动漫评价与活跃度可视化</div>
      </router-link>
    </div>
    <div class="border-2 py-2 hover:border-amber-400 px-2 underline">
      <router-link to="/work05" class=" hover:text-red-500">
        <div>动漫与声优对应可视化</div>
      </router-link>
    </div>
  </div>
  <div>
    <router-view />
  </div>
</template>
<script lang="ts">
import { readFileAndProcessExcel } from '@/tools/excelReader';
import Work01 from '@/tests/work01/Work01.vue'
import { defineComponent, ref } from 'vue';
export default {
  name: "App",
  components: {
    Work01
  },

  data() {
    return {
      data: [] as any[]
    }
  },

  computed: {
    // 动态记录route变化
    currentRoute(): string {
      return this.$route.path;
    }
  },
  beforeMount() {
  },
  async mounted() {
    this.data = await readFileAndProcessExcel('/data.xlsx')
    // console.log(this.data)
  },
  watch: {
  },
  methods: {
  },
};
</script>
<style scoped></style>