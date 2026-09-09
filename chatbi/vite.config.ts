/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // T1 语义服务（uvicorn :8901）；后端未起时 /api/profile 请求失败 → 壳自动降级 mock 模式
      '/api': 'http://localhost:8901',
    },
  },
  test: {
    environment: 'jsdom',
  },
})
