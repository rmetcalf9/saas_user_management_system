// import something here
// var gapi = require('gapi')
import './googleclient'
// https://www.npmjs.com/package/gapi

// leave the export, even if you don't use it
export default ({ app, router, Vue }) => {
  // something to do
  Vue.prototype.$gapi = window.gapi
}
