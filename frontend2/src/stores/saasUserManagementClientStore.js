import { defineStore } from 'pinia'
import callbackHelper from '../callbackHelper'
import axios from 'axios'
import { Cookies } from 'quasar'
import saasApiClientServerRequestQueue from '../saasApiClientServerRequestQueue'

export function getRjmStateChangeObj () {
  const userManagementClientStoreStore = useUserManagementClientStoreStore()
  return {
    getFromState: getFromStateFn(userManagementClientStoreStore),
    executeAction: executeActionOnStateFn(userManagementClientStoreStore)
  }
}

/* State getter and setter */

function getFromStateFn (userManagementClientStoreStore) {
  return function (getterFunctionName) {
    return userManagementClientStoreStore[getterFunctionName]
  }
}
function executeActionOnStateFn (userManagementClientStoreStore) {
  return function (actionName, params) {
    return userManagementClientStoreStore[actionName](params)
  }
}

/* END */

function loginUIBaseURLInt () {
  const rjmStateChangeObj = getRjmStateChangeObj()
  const baseUrl = rjmStateChangeObj.getFromState('loginService').baseUrl
  const tenantName = rjmStateChangeObj.getFromState('loginService').tenantName
  if (typeof (baseUrl) === 'undefined') {
    console.log('ERROR undefined loginservice baseurl found in loginUIBaseURLInt')
  }
  if (baseUrl === 0) {
    console.log('ERROR 0 loginservice baseurl found in loginUIBaseURLInt')
  }
  return baseUrl + 'public/web/frontend/#/' + tenantName
}

export function refreshJWTToken (callback, curpath, startAllBackendCallQueuesFn) {
  const rjmStateChangeObj = getRjmStateChangeObj()
  const processState = rjmStateChangeObj.getFromState('loginService').processState
  if (processState === -1) {
    callbackHelper.callbackWithSimpleError(callback, 'No login function registered')
    return
  }
  if (processState === 1) {
    callbackHelper.callbackWithSimpleError(callback, 'Mutiple calls to refreshJWT Token')
    return
  }
  const refreshToken = rjmStateChangeObj.getFromState('pendingRefreshToken')
  if (refreshToken === null) {
    callbackHelper.callbackWithSimpleError(callback, 'refreshJWTToken with no pendingRefreshToken')
    return
  }
  const loginServicePublicURL = rjmStateChangeObj.getFromState('loginService').baseUrl + 'public/'
  rjmStateChangeObj.executeAction('registerStartOfTokenRefresh')
  const url = loginServicePublicURL + 'api/login/' + rjmStateChangeObj.getFromState('loginService').tenantName + '/refresh'
  console.log('REFRESH url', url)
  const config = {
    method: 'POST',
    url,
    data: { token: refreshToken }
  }

  axios(config).then(
    (response) => {
      const rjmStateChangeObj2 = getRjmStateChangeObj()
      if (response.data.ThisTenantRoles.includes('hasaccount')) {
        const cookieToSave = response.data
        cookieToSave.loginTenantName = rjmStateChangeObj.getFromState('loginService').tenantName
        Cookies.set('saasUserManagementClientStoreCredentials', cookieToSave, {
          secure: !window.location.href.includes('localhost'), // otherwise cookie not set on dev machines
          expires: 90 // expire in 90 days
        })
        rjmStateChangeObj2.executeAction('registerEndOfTokenRefreshSuccess', { responseData: response.data })
        startAllBackendCallQueuesFn({ rjmStateChange: rjmStateChangeObj2, calledAtEndOfRefresh: true })
        callback.ok(response)
      } else {
        rjmStateChangeObj2.executeAction('registerEndOfTokenRefreshFail')
        // Clear cookie as refresh token will no work any more
        Cookies.remove('saasUserManagementClientStoreCredentials')
        console.log('FAIL Refresh result A:', response)
        rjmStateChangeObj2.executeAction('requestUserReloginFn', { message: 'Logged in user has no account', curpath })
      }
    },
    (response) => {
      const rjmStateChangeObj3 = getRjmStateChangeObj()
      rjmStateChangeObj3.executeAction('registerEndOfTokenRefreshFail')
      // Clear cookie as refresh token will no work any more
      Cookies.remove('saasUserManagementClientStoreCredentials')
      console.log('FAIL Refresh result B:', response)
      rjmStateChangeObj3.executeAction('requestUserReloginFn', { message: 'User needs to log in again', curpath })
    }
  )
}

export const useUserManagementClientStoreStore = defineStore('userManagementClientStore', {
  state: () => ({
    isEndpointsRegistered: false,
    loginService: {
      baseUrl: undefined,
      tenantName: undefined,
      /*
      -1 = login process not registered
      0 = NOT_LOGGEDIN
      1 = REFRESH_IN_PROGRESS
      2 = LOGGEDIN
      */
      processState: 0
    },
    endpointInfo: {},
    /*

    Endpoint identification process is a process that tries to get
    server info from all possible endpoints until it is sucessful
    this will vary between prod and dev
    serverinfo is not availiable until the process is complete

    endpointInfo key is id
    endpointInfo structures are:
    {
      name:
      apiCallQueue: [], //SEE apiCallQueue note below
      queueProcessingInProgress: false,
      endpointIdentificationProcessState: 0,  0=? 1=id process started, 2=id process complete serverinfo loaded
      apiPrefixIdentificationProcessConfig: {
        possibleApiPrefixes: [ { prefix: 'A', connectingthroughnginx: false }, ... ]
      }
      apiPrefix: {
        prefix: 'https://xxxx.com/a/b', connectingthroughnginx: false
      },
      serverInfo: {}
    }

    endpointIdentificationProcessState values:
    0 = NOT RUN
    1 = RUNNING
    2 = ENDPOINT IDENTIFIED

    apiCallQueue values:
    { path, method, postdata, callback, curpath, authtype }
    // possible auth types:
    //  none - never attach token to call
    //  always - always attach token to call
    //  ifloggedin - if logged in then attach token to call, otherwise don't
    */
    pendingRefreshToken: null,
    loggedInInfo: {},
    requestUserReloginFn: undefined
  }),

  getters: {
    getIsEndpointsRegistered (state) {
      return state.isEndpointsRegistered
    },
    getIsParticularEndpointsRegistered (state) {
      return function (endpointName) {
        return endpointName in state.endpointInfo
      }
    },
    getEndpointInfo (state) {
      return function (endpointName) {
        return state.endpointInfo[endpointName]
      }
    },
    isLoggedIn (state) {
      return state.loginService.processState === 2
    },
    hasRole (state) {
      return function (roleName) {
        if (!state.isLoggedIn) return false
        if (typeof (state.loggedInInfo.ThisTenantRoles) === 'undefined') return false
        return state.loggedInInfo.ThisTenantRoles.includes(roleName)
      }
    },
    loginUIBaseURL (state) {
      return loginUIBaseURLInt()
    },
    getLoginUIURLFn (state) {
      return function (message, loginPath, returnAddress) {
        let newHREF = loginUIBaseURLInt() + loginPath
        let addedParam = false
        addedParam = true
        newHREF = newHREF + '?usersystem_returnaddress=' + encodeURIComponent(returnAddress)

        if (typeof (message) !== 'undefined') {
          if (addedParam) {
            newHREF = newHREF + '&'
          } else {
            newHREF = newHREF + '?'
          }
          newHREF = newHREF + 'usersystem_message=' + encodeURIComponent(message)
        }
        return newHREF
      }
    }
  },
  actions: {
    callApi ({ endpoint, path, method, postdata, callback, curpath, orveridePublicPrivatePart, authtype }) {
      // console.log('callAuthedAPI ', path)
      this.endpointInfo[endpoint].apiCallQueue.push({ path, method, postdata, callback, curpath, authtype, orveridePublicPrivatePart })
      const rjmStateChange = getRjmStateChangeObj()
      saasApiClientServerRequestQueue.processAPICallQueue({
        rjmStateChange,
        endpoint: rjmStateChange.getFromState('getEndpointInfo')(endpoint),
        calledAtEndOfRefresh: false,
        curpath,
        startAllBackendCallQueuesFn: saasApiClientServerRequestQueue.getStartAllBackendCallQueuesFn({ curpath })
      })
    },
    callAuthedAPI ({ endpoint, path, method, postdata, callback, curpath, orveridePublicPrivatePart }) {
      if (this.loginService.processState === 0) {
        // not logged in
        callbackHelper.callbackWithSimpleError(callback, 'Trying to call authed API but not logged in')
        return
      }
      if (this.loginService.processState === -1) {
        // not logged in
        callbackHelper.callbackWithSimpleError(callback, 'Trying to call authed API but login process not registered')
        return
      }
      if (typeof (curpath) === 'undefined') {
        callbackHelper.callbackWithSimpleError(callback, 'Error callAuthedAPI called with no curpath set')
        return
      }
      this.callApi({ endpoint, path, method, postdata, callback, curpath, orveridePublicPrivatePart, authtype: 'always' })
    },
    callAuthedOrAnonAPI ({ endpoint, path, method, postdata, callback, curpath, orveridePublicPrivatePart }) {
      this.callApi({ endpoint, path, method, postdata, callback, curpath, orveridePublicPrivatePart, authtype: 'ifloggedin' })
    },
    takeFirstMessageOffQueue ({ endpoint }) {
      this.endpointInfo[endpoint].apiCallQueue.shift()
    },
    startQueueProcessing ({ endpoint }) {
      this.endpointInfo[endpoint].queueProcessingInProgress = true
    },
    endQueueProcessing ({ endpoint }) {
      this.endpointInfo[endpoint].queueProcessingInProgress = false
    },
    logout () {
      Cookies.remove('saasUserManagementClientStoreCredentials')
      this.loginService.processState = 0
      this.loggedInInfo = {}
    },
    endpointsAreRegistered () {
      this.isEndpointsRegistered = true
    },
    registerStartOfTokenRefresh () {
      this.loginService.processState = 1
      this.pendingRefreshToken = null
    },
    registerEndOfTokenRefreshSuccess ({ responseData }) {
      this.loginService.processState = 2
      this.pendingRefreshToken = responseData.refresh.token
      this.loggedInInfo = responseData
    },
    registerEndOfTokenRefreshFail () {
      this.loginService.processState = 0
    },
    registerLoginEndpoint ({ baseUrl, tenantName }) {
      this.loginService.baseUrl = baseUrl
      this.loginService.tenantName = tenantName
      this.loginService.processState = 0 // Always start with not logged in
    },
    setLoginFromCookie ({ cookieData }) {
      this.loginService.processState = 2
      this.loggedInInfo = cookieData
      this.pendingRefreshToken = this.loggedInInfo.refresh.token
    },
    registerEndpoint ({ endpointName, apiPrefixIdentificationProcessConfig, finishEndPointIdentificationHook }) {
      if (typeof (endpointName) !== 'string') {
        console.log('ERROR Store registerEndpoint wrong type of endpointName supplied', endpointName, typeof (endpointName))
        throw new Error('ERROR Store registerEndpoint wrong type of endpointName supplied')
      }
      this.endpointInfo[endpointName] = {
        name: endpointName,
        apiCallQueue: [],
        queueProcessingInProgress: false,
        endpointIdentificationProcessState: 0,
        apiPrefixIdentificationProcessConfig,
        apiPrefix: {},
        serverInfo: {},
        finishEndPointIdentificationHook
      }
    },
    registerRequestUserReloginFn ({ requestUserReloginFn }) {
      this.requestUserReloginFn = requestUserReloginFn
    },
    setEndpointIdentificationProcessState ({ endpointName, newState }) {
      if (typeof (endpointName) !== 'string') {
        console.log('ERROR Store setEndpointIdentificationProcessState wrong type of endpointName supplied', endpointName, typeof (endpointName))
        throw new Error('ERROR Store setEndpointIdentificationProcessState wrong type of endpointName supplied')
      }
      this.endpointInfo[endpointName].endpointIdentificationProcessState = newState
    },
    finishedEndpointIdentificationProcess ({ endpointName, sucessfulapiprefix, serverInfo }) {
      if (typeof (endpointName) !== 'string') {
        console.log('ERROR Store finishedEndpointIdentificationProcess wrong type of endpointName supplied', endpointName, typeof (endpointName))
        throw new Error('ERROR Store finishedEndpointIdentificationProcess wrong type of endpointName supplied')
      }
      const newEndpointObject = {
        name: endpointName,
        endpointIdentificationProcessState: 2,
        apiPrefix: sucessfulapiprefix,
        serverInfo,
        queueProcessingInProgress: false,
        // Unchanged properties below
        apiPrefixIdentificationProcessConfig: this.endpointInfo[endpointName].apiPrefixIdentificationProcessConfig,
        // Don't set apiCallQueue to empty list as calls may build up during endpoint identification
        apiCallQueue: this.endpointInfo[endpointName].apiCallQueue,
        finishEndPointIdentificationHook: this.endpointInfo[endpointName].finishEndPointIdentificationHook
      }
      this.endpointInfo[endpointName] = newEndpointObject
    },
    processRecievedJWTretervialtoken ({ jwtretervialtoken, callback, curpath, startAllBackendCallQueuesFn }) {
      console.log('TODO REM processRecievedJWTretervialtoken processState=', this.loginService.processState)
      if (this.loginService.processState !== 0) {
        console.log('saasUserManagementClientStore - Not processing RecievedJWTretervialtoken as not in LOGGEDOUT STATE')
        return
      }
      const callback2 = {
        ok: function (response) {
          console.log('processRecievedJWTretervialtoken got OK back')
          callback.ok(response)
        },
        error: function (response) {
          console.log('processRecievedJWTretervialtoken ERR', response)
          callback.error(response)
        }
      }
      this.pendingRefreshToken = jwtretervialtoken
      refreshJWTToken(callback2, curpath, startAllBackendCallQueuesFn)
    }
  }
})
