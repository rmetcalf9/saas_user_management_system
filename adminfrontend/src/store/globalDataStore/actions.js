// Adminfrontend GlobalStore Actions
/*
export function someAction (context) {
}
*/
import shared from '../../sharedFns.js'

export const readServerInfo = ({ dispatch, commit, state }, params) => {
  if (state.apiPrefix !== null) {
    params.callback.ok(null)
    return
  }
  commit('updateTenantName', params.tenantName)
  var callback = {
    ok: function (response) {
      console.log('Success API response recieved')
      commit('updateApiPrefix', response.sucessfulApiPrefix)
      commit('updateServerInfo', response.origResponse.data)
      params.callback.ok(response.origResponse)
    },
    error: params.callback.error
  }
  shared.TryToConnectToAPI(params.currentHREF, params.tenantName, callback, '/login/serverinfo')
}
