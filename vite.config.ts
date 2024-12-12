/*
 * @Description: 
 * @Author: 唐健峰
 * @Date: 2024-07-01 13:42:29
 * @LastEditors: ${author}
 * @LastEditTime: 2024-07-03 14:54:48
 */
import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  assetsInclude: ['**/*.xlsx'],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    }
  }
})
