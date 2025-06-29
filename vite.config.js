import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    strictPort: true, // Professional: Fail fast instead of port hunting
    host: '0.0.0.0',
    // Pro tip: Auto-open browser only in development
    open: process.env.NODE_ENV !== 'production',
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist'
  }
}) 