import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  
  server: {
    port: 5173,
    host: true,
    open: true,
    
    // 🔗 PROXY CONFIGURATION - CRITICO PER CONNESSIONE
    proxy: {
      '/api': {
        target: 'https://loving-comfort-production.up.railway.app',
        changeOrigin: true,
        secure: true,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('🚨 Proxy error:', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('🔄 Proxying to Railway:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('✅ Railway response:', proxyRes.statusCode, req.url);
          });
        },
      },
    },
  },
  
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})