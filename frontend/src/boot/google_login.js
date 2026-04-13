import { boot } from 'quasar/wrappers'
// import something here
// var gapi = require('gapi')
// import './googleclient'
// https://www.npmjs.com/package/gapi

// leave the export, even if you don't use it
export default boot(async ({ app, router }) => {
  // something to do
  app.config.globalProperties.$gapi = window.gapi
})
