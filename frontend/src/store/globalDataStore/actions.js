/*
export function someAction (context) {
}
*/

import callbackHelper from '../../callbackHelper'
import axios from 'axios'

function TryToConnectToPublicAPI (locationsToTry, callback, commit, tenantName) {
  var toTry = locationsToTry.pop()

  var config = {
    method: 'GET',
    url: toTry + 'api/login/' + tenantName + '/authproviders'
  }
  console.log('Tyring to reach API at ' + config.url)
  axios(config).then(
    (response) => {
      commit('updateUrlToReachPublicAPI', toTry)
      commit('updateTenant', tenantName)
      callback.ok(response)
    },
    (response) => {
      if (locationsToTry.length > 0) {
        TryToConnectToPublicAPI(locationsToTry, callback, commit, tenantName)
      } else {
        callbackHelper.callbackWithSimpleError(callback, 'Failed to connect to public login API')
      }
    }
  )
}

export const checkAuthProviders = ({ dispatch, commit }, params) => {
  // TODO how do we know what vx should be?
  var possiblePublicApiLocations = [
    '/vx/public/',
    'http://somefunnyhostname.com:8098/',
    'http://somefunnyhostname.com:5098/',
    'http://127.0.0.1:8098/'
  ]

  var callback = {
    ok: function (response) {
      commit('updateauthProviders', response.data)
      params.callback.ok(response)
    },
    error: params.callback.error
  }

  TryToConnectToPublicAPI(possiblePublicApiLocations.reverse(), callback, commit, params.tenantName)

  // state.drawerState = opened
}
