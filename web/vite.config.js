import path from 'node:path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  base: './',
  plugins: [react(), tailwindcss()],
  build: {
    outDir: '../api/static', // 👈 output goes into backend
    emptyOutDir: true,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:9999',
        changeOrigin: true,
        secure: false,
        // If your FastAPI routes do not include the '/api' prefix, uncomment the line below
        // rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
