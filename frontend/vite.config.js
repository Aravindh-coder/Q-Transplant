import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 5174,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true,
        secure: false,
        ws: true
      }
    }
  }
});
