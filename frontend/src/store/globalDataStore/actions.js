// Frontend GlobalStore Actions
/*
export function someAction (context) {
}
*/

import shared from '../../sharedFns.js'
import callbackHelper from '../../callbackHelper'

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

export const callLoginAPI = ({ dispatch, commit, state }, params) => {
  var refreshFns = _getRefreshFunctions(commit, state)

  shared.callAPI(refreshFns, state.tenant, state.apiPrefix, false, '/login/' + state.tenant + params['path'], params['method'], params['postdata'], params.callback)
}

export const callCurrentAuthAPI = ({ dispatch, commit, state }, params) => {
  // console.log('callCurrentAuthAPI:', params)
  if (typeof (params.curPath) === 'undefined') {
    callbackHelper.callbackWithSimpleError(params.callback, 'Bad call no current path')
    return
  }
  var refreshFns = _getRefreshFunctions(commit, state)

  if (state.apiPrefix === null) {
    callbackHelper.callbackWithSimpleError(params.callback, 'apiPrefix not set - this should never happen')
    return
  }
  // Not needed in frontend as the apiPrefix is always filled in
  //  this is because checkTenant is always called
  // if (state.apiPrefix === null) {
  //   var callback = {
  //     ok: function (response) {
  //       shared.callAuthedAPI(commit, state, params['path'], params['method'], params['postdata'], params.callback, params.curPath, params.headers, refreshFns, 'admin', state.tenantName, state.apiPrefix)
  //     },
  //     error: params.callback.error
  //   }
  //   readServerInfo(state, commit, window.location.href, callback)
  //   return
  // }

  shared.callAuthedAPI(commit, state, params['path'], params['method'], params['postdata'], params.callback, params.curPath, params.headers, refreshFns, 'currentAuth', state.tenant, state.apiPrefix)
}
