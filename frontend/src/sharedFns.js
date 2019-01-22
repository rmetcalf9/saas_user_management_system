/*
Functions shared between frontend and adminfrontend

(This and callbackHelper)
*/

function getURLsToTryForAPI () {
  // TODO how do we know what vx should be?
  return [
    '/vx/public/',
    'http://somefunnyhostname.com:8098/',
    'http://somefunnyhostname.com:5098/',
    'http://127.0.0.1:8098/'
  ]
}

export default {
  getURLsToTryForAPI: getURLsToTryForAPI
}
