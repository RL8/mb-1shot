import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [vue()],
    server: {
      port: 3000,
      strictPort: true, // Professional: Fail fast instead of port hunting
      host: '0.0.0.0',
      // Pro tip: Auto-open browser only in development
      open: env.NODE_ENV !== 'production',
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:3001',
          changeOrigin: true
        }
      }
    },
    build: {
      outDir: 'dist'
    },
    // Define global constants for environment variables
    define: {
      __APP_NAME__: JSON.stringify(env.VITE_APP_NAME),
      __APP_VERSION__: JSON.stringify(env.VITE_APP_VERSION),
      __API_URL__: JSON.stringify(env.VITE_API_URL)
    }
  }
}) 