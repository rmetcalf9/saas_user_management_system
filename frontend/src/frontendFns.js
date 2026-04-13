import saasAPiClientCallBackend from './saasAPiClientCallBackend.js'
// import callbackHelper from './callbackHelper'2
import { useTenantInfoStore } from 'stores/tenantInfo'

// callback dosent have to do anything as proceeLoginResponse is called from here
function callLoginAPI ({ credentialJSON, callback, processLoginResponseInstance, registering, router }) {
  const tenantInfoStore = useTenantInfoStore()
  const loginRequestPostData = {
    credentialJSON,
    authProviderGUID: tenantInfoStore.selectedAuth.guid
  }
  // TODO ReIntroduce ticket functinoality
  // if (typeof (store.state.globalDataStore.ticketInUse) !== 'undefined') {
  //   if (store.state.globalDataStore.ticketInUse !== null) {
  //     if (store.state.globalDataStore.ticketInUse !== 'null') {
  //       loginRequestPostData['ticket'] = store.state.globalDataStore.ticketInUse
  //     }
  //   }
  // }

  const localCallback = {
    ok: function (response) {
      callback.ok(response)
      if (typeof (processLoginResponseInstance) !== 'undefined') {
        processLoginResponseInstance.processLoginOKResponse(response, loginRequestPostData)
      }
    },
    error: function (response) {
      callback.error(response)
    }
  }
  let method = 'POST'
  let path = '/authproviders'
  if (typeof (registering) !== 'undefined') {
    if (registering) {
      method = 'PUT'
      path = '/register'
    }
  }
  saasAPiClientCallBackend.callApi({
    prefix: 'login',
    router,
    path: '/' + tenantInfoStore.selectedAuthTenantName + path,
    method,
    postdata: loginRequestPostData,
    callback: localCallback
  })
}

function passwordERRORMessage (passwordd, passwordd2) {
  if (/[A-Z]/.test(passwordd) !== true) {
    return 'Password must contain at least one uppercase letter'
  }
  if (/[a-z]/.test(passwordd) !== true) {
    return 'Password must contain at least one lowercase letter'
  }
  if (/\d/.test(passwordd) !== true) {
    return 'Password must contain at least one number'
  }
  if (passwordd.length < 5) {
    return 'Password must be at least 5 characters'
  }
  if (passwordd !== passwordd2) {
    return 'Passwords must match'
  }
  return 'Password'
}

function isSet (value) {
  if (value === null) {
    return false
  }
  if (typeof (value) === 'undefined') {
    return false
  }
  if (value === 'undefined') {
    return false
  }
  return true
}

export default {
  passwordERRORMessage,
  isSet,
  callLoginAPI
}
