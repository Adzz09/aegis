import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: process.env.PROXY_TARGET || 'http://localhost:8000',
        changeOrigin: true
      },
      '/ws': {
        target: process.env.PROXY_TARGET || 'http://localhost:8000',
        changeOrigin: true,
        ws: true
      }
    }
  }
})
