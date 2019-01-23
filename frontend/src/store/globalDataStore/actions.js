// Frontend GlobalStore Actions
/*
export function someAction (context) {
}
*/

import callbackHelper from '../../callbackHelper'
import axios from 'axios'
import shared from '../../sharedFns.js'

export const checkAuthProviders = ({ dispatch, commit, state }, params) => {
  commit('updateTenant', params.tenantName)

  var callback = {
    ok: function (response) {
      console.log('Success API response recieved')
      commit('updateUrlToReachPublicAPI', response.sucessfulURL)
      commit('updateTenantInfo', response.origResponse.data)
      params.callback.ok(response.origResponse)
    },
    error: params.callback.error
  }
  shared.TryToConnectToAPI(params.currentHREF, params.tenantName, callback, 'api/login/' + params.tenantName + '/authproviders')

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
