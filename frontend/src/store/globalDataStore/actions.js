/*
export function someAction (context) {
}
*/

import callbackHelper from '../../callbackHelper'
import axios from 'axios'
import shared from '../../sharedFns.js'

function TryToConnectToPublicAPI (locationsToTry, callback, commit, tenantName) {
  var toTry = locationsToTry.pop()

  var config = {
    method: 'GET',
    url: toTry + 'api/login/' + tenantName + '/authproviders'
  }
  console.log('Tyring to reach API at ' + config.url)
  axios(config).then(
    (response) => {
      console.log('Success API response recieved')
      commit('updateUrlToReachPublicAPI', toTry)
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

export const checkAuthProviders = ({ dispatch, commit, state }, params) => {
  var possiblePublicApiLocations = shared.getURLsToTryForAPI(params.currentHREF)
  commit('updateTenant', params.tenantName)

  var callback = {
    ok: function (response) {
      commit('updateTenantInfo', response.data)
      params.callback.ok(response)
    },
    error: params.callback.error
  }
  TryToConnectToPublicAPI(possiblePublicApiLocations.reverse(), callback, commit, params.tenantName)

  // state.drawerState = opened
}

// LoginAPI requires no auth at all
export const callLoginAPI = ({ dispatch, commit, state }, params) => {
  var config = {
    method: params['method'],
    url: state.urlToReachPublicAPI + 'api/login/' + state.tenant + params['path'],
    data: params['postdata']
  }

  axios(config).then(
    (response) => {
      params.callback.ok(response)
    },
    (response) => {
      callbackHelper.webserviceError(params.callback, response)
    }
  )
}
