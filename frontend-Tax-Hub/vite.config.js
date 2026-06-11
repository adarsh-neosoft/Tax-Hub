import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ironStackRoot = path.resolve(__dirname, 'node_modules/iron-stack-ui')

// Use iron-stack-ui source (supports customRoutes) instead of stale dist bundle.
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: [
      { find: /^iron-stack-ui$/, replacement: path.resolve(ironStackRoot, 'lib/index.js') },
      { find: /^@\//, replacement: `${path.resolve(ironStackRoot, 'src')}/` },
    ],
  },
})
