import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: '0.0.0.0',  // 监听所有网络接口，允许公网访问
    allowedHosts: ['unfreeze-doorframe-manliness.ngrok-free.dev'],  // 允许ngrok域名访问
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
