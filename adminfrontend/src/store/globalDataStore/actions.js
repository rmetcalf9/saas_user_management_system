// Adminfrontend GlobalStore Actions
/*
export function someAction (context) {
}
*/
import shared from '../../sharedFns.js'
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

function _getRefreshFunctions (commit, state) {
  return {
    startRefreshFN: function () {
      commit('START_REFRESH')
    },
    endRefreshFN: function () {
      commit('END_REFRESH')
    },
    isRefreshInProgressFN: function () {
      return state.refeshTokenInProgress
    },
    refreshCompleteFN: function () {
      for (var curIdx in state.refeshTokenInfoStoredResponses) {
        // console.log('Launching refresh delayed API call')
        state.refeshTokenInfoStoredResponses[curIdx].ok('undefined')
      }
      commit('REFRESH_STORED_RESPONSE_PROCESS_COMPLETE')
    },
    addPostRefreshActionFN: function (callback) {
      commit('RECORD_REFRESH_STORED_RESPONSE', callback)
    }
  }
}

export const callAdminAPI = ({ dispatch, commit, state }, params) => {
  // console.log('ADMINAPICALL:', params)
  if (typeof (params.curPath) === 'undefined') {
    callbackHelper.callbackWithSimpleError(params.callback, 'Bad call no current path')
    return
  }

  var refreshFns = _getRefreshFunctions(commit, state)

  if (state.apiPrefix === null) {
    var callback = {
      ok: function (response) {
        shared.callAuthedAPI(commit, state, params['path'], params['method'], params['postdata'], params.callback, params.curPath, params.headers, refreshFns, 'admin', state.tenantName, state.apiPrefix)
      },
      error: params.callback.error
    }
    readServerInfo(state, commit, window.location.href, callback)
    return
  }

  shared.callAuthedAPI(commit, state, params['path'], params['method'], params['postdata'], params.callback, params.curPath, params.headers, refreshFns, 'admin', state.tenantName, state.apiPrefix)
}
