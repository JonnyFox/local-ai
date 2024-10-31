module.exports = function (ctx) {
  return {
    framework: {
      iconSet: 'material-icons', // Optional, set your preferred icon set
      components: [
        // List the Quasar components you want to use
      ],
      directives: [
        // List the Quasar directives you want to use
      ],
      plugins: [
        // List the Quasar plugins you want to use
      ]
    },
    css: [
      'app.scss' // Your global styles
    ],
    build: {
      vueRouterMode: 'history' // Required for Vue Router
    }
  }
}
