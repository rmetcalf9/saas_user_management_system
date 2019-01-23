/*
Functions shared between frontend and adminfrontend

(This and callbackHelper)
*/

function getURLsToTryForAPI (currentURL) {
  // TODO how do we know what vx should be?
  console.log('TODO Work out on prod vx based on current url: ', currentURL)
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
