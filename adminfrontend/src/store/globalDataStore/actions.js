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
    commit('RECORD_READ_SERVER_INFO_STORED_RESPONSE', callback)
    console.log('Storing read server info saved response')
    // callbackHelper.callbackWithSimpleError(callback, 'Trying to readServerInfo Twice - TODO Code for this eventuality')
    return
  }
  commit('START_READ_SERVER_INFO')

  var callback2 = {
    ok: function (response) {
      console.log('Success API response recieved')
      commit('updateApiPrefix', response.sucessfulApiPrefix)
      commit('updateServerInfo', response.origResponse.data)
      commit('END_READ_SERVER_INFO')
      for (var curIdx in state.readServerInfoStoredResponses) {
        state.readServerInfoStoredResponses[curIdx].ok('undefined')
      }
      commit('READ_SERVER_INFO_STORED_RESPONSE_PROCESS_COMPLETE')
      callback.ok(response.origResponse)
    },
    error: function (response) {
      commit('END_READ_SERVER_INFO')
      // Not processing extra errors
      commit('READ_SERVER_INFO_STORED_RESPONSE_PROCESS_COMPLETE')
      callback.error(response)
    }
  }
  shared.TryToConnectToAPI(currentHREF, state.tenantName, callback2, '/login/serverinfo')
}

function _callAdminAPI (state, path, method, postdata, callback, curPath, headers) {
  var cookie = Cookies.get('usersystemUserCredentials')

  shared.callAPI(state.tenantName, state.apiPrefix, true, '/admin/' + state.tenantName + path, method, postdata, callback, cookie.jwtData, cookie.refresh, false, curPath, headers)
}

export const callAdminAPI = ({ dispatch, commit, state }, params) => {
  // console.log('ADMINAPICALL:', params)
  if (typeof (params.curPath) === 'undefined') {
    callbackHelper.callbackWithSimpleError(params.callback, 'Bad call no current path')
    return
  }
  if (state.apiPrefix === null) {
    var callback = {
      ok: function (response) {
        _callAdminAPI(state, params['path'], params['method'], params['postdata'], params.callback, params.curPath, params.headers)
      },
      error: params.callback.error
    }
    readServerInfo(state, commit, window.location.href, callback)
    return
  }

  _callAdminAPI(state, params['path'], params['method'], params['postdata'], params.callback, params.curPath, params.headers)
}
