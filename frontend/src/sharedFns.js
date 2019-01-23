/*
Functions shared between frontend and adminfrontend

(This and callbackHelper)
*/
import callbackHelper from './callbackHelper'
import axios from 'axios'

function getURLsToTryForAPI (currentURL, tenantName) {
  // TODO how do we know what vx should be?
  console.log('TODO Work out on prod vx based on current url and tenantName: ', currentURL, tenantName)
  // Note: Always on the public API
  return [
    '/vx/public/',
    'http://somefunnyhostname.com:8098/',
    'http://somefunnyhostname.com:5098/',
    'http://127.0.0.1:8098/'
  ]
}

function TryToConnectToAPIRecurring (locationsToTry, callback, apiPath) {
  var toTry = locationsToTry.pop()

  var config = {
    method: 'GET',
    url: toTry + apiPath
  }
  console.log('Tyring to reach API at ' + config.url)
  axios(config).then(
    (response) => {
      callback.ok({
        origResponse: response,
        sucessfulURL: toTry
      })
    },
    (response) => {
      if (locationsToTry.length > 0) {
        TryToConnectToAPIRecurring(locationsToTry, callback, apiPath)
      } else {
        callbackHelper.callbackWithSimpleError(callback, 'Failed to connect to public login API')
      }
    }
  )
}

function TryToConnectToAPI (currentHREF, tenantName, callback, apiPath) {
  var possiblePublicApiLocations = getURLsToTryForAPI(currentHREF, tenantName)
  TryToConnectToAPIRecurring(possiblePublicApiLocations.reverse(), callback, apiPath)
}

export default {
  TryToConnectToAPI: TryToConnectToAPI
}
