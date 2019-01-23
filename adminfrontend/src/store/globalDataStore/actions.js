// Adminfrontend GlobalStore Actions
/*
export function someAction (context) {
}
*/
import shared from '../../sharedFns.js'
import { Cookies } from 'quasar'

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

export const callAdminAPI = ({ dispatch, commit, state }, params) => {
  var cookie = Cookies.get('usersystemUserCredentials')

  shared.callAPI(state.apiPrefix, true, '/admin/' + state.tenantName + params['path'], params['method'], params['postdata'], params.callback, cookie.jwtData, cookie.refresh)
}
