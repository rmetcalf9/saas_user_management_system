// Frontend GlobalStore Actions
/*
export function someAction (context) {
}
*/

import shared from '../../sharedFns.js'

export const checkAuthProviders = ({ dispatch, commit, state }, params) => {
  commit('updateTenant', params.tenantName)

  var callback = {
    ok: function (response) {
      console.log('Success API response recieved')
      commit('updateApiPrefix', response.sucessfulApiPrefix)
      commit('updateTenantInfo', response.origResponse.data)
      params.callback.ok(response.origResponse)
    },
    error: params.callback.error
  }
  shared.TryToConnectToAPI(params.currentHREF, params.tenantName, callback, '/login/' + params.tenantName + '/authproviders')

  // state.drawerState = opened
}

export const callLoginAPI = ({ dispatch, commit, state }, params) => {
  shared.callAPI(state.tenant, state.apiPrefix, false, '/login/' + state.tenant + params['path'], params['method'], params['postdata'], params.callback)
}
