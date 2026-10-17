import fs from 'node:fs'
import path from 'node:path'
import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

const API = process.env.API_URL ?? 'http://127.0.0.1:8000'
const DEMO = path.resolve(import.meta.dirname, '../api/demo_cache/images') // gitignored, built by `python -m demo_cache.build`

// Dev only: serves the licensed demo images so the wizard's "Cached: …" buttons can upload them.
const demoImages = (): Plugin => ({
  name: 'demo-images',
  configureServer(server) {
    server.middlewares.use('/demo-images/', (req, res, next) => {
      const file = path.join(DEMO, path.basename(req.url ?? ''))
      if (!file.endsWith('.png') || !fs.existsSync(file)) return next()
      res.setHeader('Content-Type', 'image/png')
      fs.createReadStream(file).pipe(res)
    })
  },
})

export default defineConfig({
  plugins: [react(), tailwindcss(), demoImages()],
  server: {
    // same origin for the session cookie: /api/* goes to FastAPI with the prefix removed
    fs: { allow: ['.', '../../docs'] },
    proxy: { '/api': { target: API, rewrite: (p) => p.replace(/^\/api/, '') } },
  },
})
