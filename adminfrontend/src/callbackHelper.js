// This class contains functions to help callbacks

function callbackWithError (callback, msg, obj) {
  const retobj = {
    message: msg,
    orig: obj
  }
  console.log(retobj)
  callback.error(retobj)
}
function callbackWithSimpleError (callback, msg) {
  callbackWithError(callback, msg, undefined)
}
function callbackWithNotImplemented (callback) {
  callbackWithError(callback, 'Not Implemented', undefined)
}

// Used as the error function of an axios call
function webserviceError (callback, response) {
  let rjmmsg = 'Error'

  if (typeof (response.response) === 'undefined') {
    if (typeof (response.message) === 'undefined') {
      rjmmsg = 'Bad Response UNKNOWN'
    } else {
      rjmmsg = 'Bad Response ' + response.message
    }
  } else if (typeof (response.response.data) !== 'undefined') {
    if (typeof (response.response.data.errorMessages) !== 'undefined') {
      rjmmsg = 'Bad Response(' + response.response.data.errorMessages.length + ') ' + response.response.data.errorMessages
    } else {
      rjmmsg = 'Data Bad Response ' + response.response.status
    }
  } else {
    rjmmsg = 'Nested Bad Response ' + response.response.status
  }
  callbackWithError(callback, rjmmsg, response)
}

function getResponseStatusIfItHasOneOtherwiseNegativeOne (response) {
  if (typeof (response) === 'undefined') {
    return -1
  }
  if (typeof (response.response) !== 'undefined') {
    response = response.response
  }
  if (typeof (response.status) === 'undefined') {
    return -1
  }
  return response.status
}

function getDoNothingCallback () {
  const callback = {
    ok: function (response) {
      // return
    },
    error: function (response) {
      // return
    }
  }
  return callback
}

function consoleLogCallback () {
  const callback = {
    ok: function (response) {
      console.log('consoleLogCallback ok', response)
    },
    error: function (response) {
      console.log('consoleLogCallback error', response)
    }
  }
  return callback
}

// function to get human error message from error
function getErrorFromResponse (respError) {
  if (typeof (respError.orig) !== 'undefined') {
    if (typeof (respError.orig.response) !== 'undefined') {
      if (typeof (respError.orig.response.data) !== 'undefined') {
        if (typeof (respError.orig.response.data.message) !== 'undefined') {
          return respError.orig.response.data.message
        }
      }
    }
  }
  return respError.message
}

export default {
  callbackWithError,
  callbackWithSimpleError,
  callbackWithNotImplemented,
  webserviceError,
  getDoNothingCallback,
  getErrorFromResponse,
  getResponseStatusIfItHasOneOtherwiseNegativeOne,
  consoleLogCallback
}
