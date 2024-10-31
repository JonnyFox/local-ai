const { defineConfig } = require('@vue/cli-service')
const path = require('path')

module.exports = defineConfig({
  transpileDependencies: [
    'quasar'
  ],

  configureWebpack: process.env.NODE_ENV !== 'production'
    ? {
        devtool: 'source-map',
        watch: process.env.NODE_ENV !== 'production',
        watchOptions: {
          ignored: /node_modules/,
          poll: 1000
        },
        resolve: {
          symlinks: false,
          alias: {
            globalize$: path.resolve(__dirname, 'node_modules/globalize/dist/globalize.js'),
            globalize: path.resolve(__dirname, 'node_modules/globalize/dist/globalize'),
            cldr$: path.resolve(__dirname, 'node_modules/cldrjs/dist/cldr.js'),
            cldr: path.resolve(__dirname, 'node_modules/cldrjs/dist/cldr'),
            vue: path.resolve(__dirname, './node_modules/vue')
          },
          extensions: ['.ts', '.js', '.json']
        }
      }
    : {},

  pluginOptions: {
    quasar: {
      importStrategy: 'kebab',
      rtlSupport: false
    }
  }
})
