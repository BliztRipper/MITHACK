import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

const API = process.env.API_URL ?? 'http://127.0.0.1:8000'
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // same origin for the session cookie: /api/* goes to FastAPI with the prefix removed
    fs: { allow: ['.', '../../docs'] },
    proxy: { '/api': { target: API, rewrite: (p) => p.replace(/^\/api/, '') } },
  },
})
