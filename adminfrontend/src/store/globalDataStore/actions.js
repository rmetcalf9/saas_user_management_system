// Adminfrontend GlobalStore Actions
/*
export function someAction (context) {
}
*/
import shared from '../../sharedFns.js'
import { Cookies } from 'quasar'
import callbackHelper from '../../callbackHelper'

function readServerInfo (state, commit, currentHREF, callback) {
  if (state.apiPrefix !== null) {
    callback.ok(null)
    return
  }
  if (state.readServerInfoInProgress) {
    callbackHelper.callbackWithSimpleError(callback, 'Trying to readServerInfo Twice - TODO Code for this eventuality')
    return
  }
  commit('START_READ_SERVER_INFO')

  var callback2 = {
    ok: function (response) {
      console.log('Success API response recieved')
      commit('updateApiPrefix', response.sucessfulApiPrefix)
      commit('updateServerInfo', response.origResponse.data)
      commit('END_READ_SERVER_INFO')
      callback.ok(response.origResponse)
    },
    error: function (response) {
      commit('END_READ_SERVER_INFO')
      callback.error(response)
    }
  }
  shared.TryToConnectToAPI(currentHREF, state.tenantName, callback2, '/login/serverinfo')
}

function _callAdminAPI (state, path, method, postdata, callback, curPath) {
  var cookie = Cookies.get('usersystemUserCredentials')

  shared.callAPI(state.tenantName, state.apiPrefix, true, '/admin/' + state.tenantName + path, method, postdata, callback, cookie.jwtData, cookie.refresh, true, curPath)
}

export const callAdminAPI = ({ dispatch, commit, state }, params) => {
  if (typeof (params.curPath) === 'undefined') {
    callbackHelper.callbackWithSimpleError(params.callback, 'Bad call no current path')
    return
  }
  if (state.apiPrefix === null) {
    var callback = {
      ok: function (response) {
        _callAdminAPI(state, params['path'], params['method'], params['postdata'], params.callback, params.curPath)
      },
      error: params.callback.error
    }
    readServerInfo(state, commit, window.location.href, callback)
    return
  }

  _callAdminAPI(state, params['path'], params['method'], params['postdata'], params.callback, params.curPath)
}
