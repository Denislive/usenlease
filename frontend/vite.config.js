import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  build: {
    outDir: 'dist',
    sourcemap: true, // Ensure the build output directory is set to 'dist'
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  define: {
    // Hardcoding the API base URL
    'import.meta.env.VITE_GOOGLE_PLACES_API_KEY': JSON.stringify('AIzaSyDsStVNZTck0RfRhwxUEyuqs22ycql05Zw'),
    'import.meta.env.VITE_API_BASE_URL': JSON.stringify('https://usenlease.com'),
    'import.meta.env.VITE_ENCRYPTION_KEY': JSON.stringify('mr1HukORlqQM1wvE/uEooNbF6cSL3WDT1aeUdRHAleY/ERuSLQo2FXu7z6TLKWIr'),
  },
});
