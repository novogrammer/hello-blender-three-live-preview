import { defineConfig, type Plugin } from 'vite'

function reloadOnModelAssetChange(): Plugin {
  return {
    name: 'reload-on-model-asset-change',
    apply: 'serve',
    handleHotUpdate({ file, server }) {
      if (!file.includes('/public/models/')) {
        return
      }

      server.ws.send({
        type: 'full-reload',
      })

      return []
    },
  }
}

export default defineConfig({
  plugins: [reloadOnModelAssetChange()],
})
