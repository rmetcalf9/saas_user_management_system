/*
export function someAction (context) {
}
*/

import callbackHelper from '../../callbackHelper'
import axios from 'axios'

function TryToConnectToPublicAPI (locationsToTry, params) {
  var toTry = locationsToTry.pop()

  var config = {
    method: 'GET',
    url: toTry + 'api/login/usersystem/authproviders'
  }
  console.log('Tyring to reach API at ' + config.url)
  axios(config).then(
    (response) => {
      params.callback.ok(response)
    },
    (response) => {
      if (locationsToTry.length > 0) {
        TryToConnectToPublicAPI(locationsToTry, params)
      } else {
        callbackHelper.callbackWithSimpleError(params.callback, 'Failed to connect to public login API')
      }
    }
  )
}

export const checkAuthProviders = ({ dispatch }, params) => {
  console.log(params)

  // TODO how do we know what vx should be?
  var possiblePublicApiLocations = [
    '/vx/public/',
    'http://somefunnyhostname.com:8098/',
    'http://somefunnyhostname.com:5098/'
  ]

  TryToConnectToPublicAPI(possiblePublicApiLocations.reverse(), params)

  // state.drawerState = opened
}
