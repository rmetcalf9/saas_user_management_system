
// callback dosent have to do anythin as proceeLoginResponse is called from here
function callLoginAPI ({ store, credentialJSON, callback, processLoginResponseInstance, registering }) {
  var loginRequestPostData = {
    credentialJSON: credentialJSON,
    authProviderGUID: store.state.globalDataStore.selectedAuthProvGUID
  }
  if (typeof (store.state.globalDataStore.ticketInUse) !== 'undefined') {
    if (store.state.globalDataStore.ticketInUse !== null) {
      if (store.state.globalDataStore.ticketInUse !== 'null') {
        loginRequestPostData['ticket'] = store.state.globalDataStore.ticketInUse
      }
    }
  }
  var localCallback = {
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
  var method = 'POST'
  var path = '/authproviders'
  if (typeof (registering) !== 'undefined') {
    if (registering) {
      method = 'PUT'
      path = '/register'
    }
  }
  store.dispatch('globalDataStore/callLoginAPI', {
    method: method,
    path: path,
    callback: localCallback,
    postdata: loginRequestPostData
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
  passwordERRORMessage: passwordERRORMessage,
  isSet: isSet,
  callLoginAPI: callLoginAPI
}
