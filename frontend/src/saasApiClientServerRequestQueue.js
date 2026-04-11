/*
This file contains rotunes that handle the queuing of requests sent to the backend server
*/
import callbackHelper from './callbackHelper'
import axios from 'axios'
import { refreshJWTToken } from './stores/saasUserManagementClientStore'
import saasApiClientEndpointIdentificationProcess from './saasApiClientEndpointIdentificationProcess'

function getStartAllBackendCallQueuesFn ({ curpath }) {
  return function ({ rjmStateChange, calledAtEndOfRefresh }) {
    for (const endpointName in rjmStateChange.getFromState('endpointInfo')) {
      processAPICallQueue({
        rjmStateChange,
        endpoint: rjmStateChange.getFromState('getEndpointInfo')(endpointName),
        calledAtEndOfRefresh,
        curpath,
        startAllBackendCallQueuesFn: getStartAllBackendCallQueuesFn({ curpath })
      })
    }
  }
}

function startEndpointIdentificationprocessThenStartToProcessQueue ({ rjmStateChange, endpoint, curpath, startAllBackendCallQueuesFn }) {
  const callback = {
    // TODO WRONG CALLBACK of startEndpointIdentificationProcess GIVES ENDPOINT NAME
    ok: function ({ serverinfoResponse, endpointName, sucessfulapiprefix }) {
      processAPICallQueue({
        rjmStateChange,
        endpoint: rjmStateChange.getFromState('getEndpointInfo')(endpointName),
        calledAtEndOfRefresh: false,
        curpath,
        startAllBackendCallQueuesFn
      })
    },
    error: function (response) {
    }
  }
  saasApiClientEndpointIdentificationProcess.startEndpointIdentificationProcess({ endpointName: endpoint.name, callback, rjmStateChange })
}

function processAPICallQueue ({ rjmStateChange, endpoint, calledAtEndOfRefresh, curpath, startAllBackendCallQueuesFn }) {
  // console.log('call processAPICallQueue for endpoint', endpoint, state.loginProcessState)
  if (endpoint.queueProcessingInProgress) return
  const loginProcessState = rjmStateChange.getFromState('loginService').processState
  if (loginProcessState === 1) return // refresh in progress, it will call this fn again when completed
  if (loginProcessState === -1) return // login process not registered
  // if (loginProcessState === 0) return // not logged in Altered, processing API calls even if not logged in
  if (endpoint.endpointIdentificationProcessState === 0) {
    startEndpointIdentificationprocessThenStartToProcessQueue({ rjmStateChange, endpoint, curpath, startAllBackendCallQueuesFn })
    return // we are
  }
  if (endpoint.endpointIdentificationProcessState === 1) return // we are processing endpoint state this fn will call again when completed

  if (endpoint.queueProcessingInProgress) return // belt and braces second check

  rjmStateChange.executeAction('startQueueProcessing', { endpoint: endpoint.name })
  processAPICallQueueRecursive({ endpoint, rjmStateChange, calledAtEndOfRefresh, curpath, startAllBackendCallQueuesFn })
}

function processAPICallQueueRecursive ({ endpoint, rjmStateChange, calledAtEndOfRefresh, curpath, startAllBackendCallQueuesFn }) {
  const latestEndpointInfo = rjmStateChange.getFromState('getEndpointInfo')(endpoint.name)
  if (latestEndpointInfo.apiCallQueue.length === 0) {
    rjmStateChange.executeAction('endQueueProcessing', { endpoint: endpoint.name })
    // console.log('No calls to make')
    return
  }
  // // console.log('Calling')
  const apiCall = latestEndpointInfo.apiCallQueue[0]
  const urlToCall = getUrlToCall(latestEndpointInfo.apiPrefix, apiCall.path, apiCall.orveridePublicPrivatePart)
  const config = {
    method: apiCall.method,
    url: urlToCall,
    data: apiCall.postdata,
    headers: {}
  }
  let attachToken = false
  switch (apiCall.authtype) {
    case 'none':
      attachToken = true
      break
    case 'always':
      attachToken = true
      break
    case 'ifloggedin':
      if (rjmStateChange.getFromState('isLoggedIn')) {
        attachToken = true
      }
      break
  }
  // // console.log('callAPI ', apiCall.authtype, 'attachToken:', attachToken, ' state', state.loginProcessState)
  //
  if (attachToken) {
    // Possible optiomzation - check if jwt token has expired and go direct to refresh call
    // console.log(state.loggedInInfo.jwtData.JWTToken)
    const jwtToken = rjmStateChange.getFromState('loggedInInfo').jwtData.JWTToken
    config.headers['jwt-auth-token'] = jwtToken
    // Kong can only read Authorization header- https://docs.konghq.com/hub/kong-inc/jwt/
    config.headers.Authorization = 'Bearer ' + jwtToken
  }
  axios(config).then(
    (response) => {
      apiCall.callback.ok(response)
      rjmStateChange.executeAction('takeFirstMessageOffQueue', { endpoint: endpoint.name })
      processAPICallQueueRecursive({ rjmStateChange, endpoint, calledAtEndOfRefresh, curpath, startAllBackendCallQueuesFn })
    },
    (response) => {
      // Error respones
      if (callbackHelper.getResponseStatusIfItHasOneOtherwiseNegativeOne(response) === 401) {
        if (calledAtEndOfRefresh) {
          callbackHelper.callbackWithSimpleError(apiCall.callback, 'API Call Auth failed (refresh tried)')
          rjmStateChange.executeAction('takeFirstMessageOffQueue', { endpoint: endpoint.name })
          processAPICallQueueRecursive({ rjmStateChange, endpoint, calledAtEndOfRefresh, curpath, startAllBackendCallQueuesFn })
        } else {
          rjmStateChange.executeAction('endQueueProcessing', { endpoint: endpoint.name })
          // Passing undefined as callback
          refreshJWTToken(undefined, curpath, startAllBackendCallQueuesFn)
          // return (Not needed)
        }
      } else {
        callbackHelper.webserviceError(apiCall.callback, response)
        rjmStateChange.executeAction('takeFirstMessageOffQueue', { endpoint: endpoint.name })
        processAPICallQueueRecursive({ rjmStateChange, endpoint, calledAtEndOfRefresh, curpath, startAllBackendCallQueuesFn })
      }
    }
  )
}

function getUrlToCall (prefixRecord, apiPath, orveridePublicPrivatePart) {
  // apitype can be either 'public' or 'private' and it's the kong endpoint part of the url
  let apiTypeToUse = prefixRecord.apitype
  if (typeof (orveridePublicPrivatePart) !== 'undefined') {
    apiTypeToUse = orveridePublicPrivatePart
  }
  if (prefixRecord.connectingthroughnginx) {
    return prefixRecord.prefix + '/' + apiTypeToUse + '/api' + apiPath
  }
  return prefixRecord.prefix + '/api/' + apiTypeToUse + apiPath
}

export default {
  getStartAllBackendCallQueuesFn,
  processAPICallQueue
}
