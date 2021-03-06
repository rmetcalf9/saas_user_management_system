/*
Functions shared between frontend and adminfrontend

MUST EDIT THE ADMINFRONTEND version and use process to copy across

(This and callbackHelper)
*/
import callbackHelper from './callbackHelper'
import axios from 'axios'
import { Cookies } from 'quasar'

/*
Example values of currentURL:
https://api.metcarob.com/saas_user_management/test/v0/public/web/adminfrontend/#/usersystem/users
https://api.metcarob.com/saas_user_management/v0/public/web/adminfrontend/#/usersystem/users
http://somefunnyhostname.com:5080/public/web/adminfrontend/#/usersystem/users

*/
function getProdVer (currentURL) {
  var searchStr = '/saas_user_management/test/v'
  var testPos = currentURL.indexOf(searchStr)
  var searchStr2 = '/public/web/'
  if (testPos !== -1) {
    var midArg = currentURL.substring(currentURL.indexOf(searchStr) + searchStr.length)
    var secondPos = midArg.indexOf(searchStr2)
    if (secondPos === -1) {
      return {
        prod: false
      }
    }
    return {
      prod: true,
      ver: parseInt(midArg.substring(0, secondPos)),
      test: true,
      prefix: currentURL.substring(0, currentURL.indexOf(searchStr)) + searchStr + parseInt(midArg.substring(0, secondPos)) + '/'
    }
  } else {
    searchStr = '/saas_user_management/v'
    testPos = currentURL.indexOf(searchStr)
    if (testPos !== -1) {
      midArg = currentURL.substring(currentURL.indexOf(searchStr) + searchStr.length)
      secondPos = midArg.indexOf(searchStr2)
      if (secondPos === -1) {
        return {
          prod: false
        }
      }
      return {
        prod: true,
        ver: parseInt(midArg.substring(0, secondPos)),
        test: false,
        prefix: currentURL.substring(0, currentURL.indexOf(searchStr)) + searchStr + parseInt(midArg.substring(0, secondPos)) + '/'
      }
    }
  }
  return {
    prod: false
  }
}

function getAPIPrefixPossibilities (currentURL, tenantName) {
  // See https://github.com/rmetcalf9/saas_user_management_system/blob/master/FRONTEND_NOTES.MD
  // TODO how do we know what vx should be?
  var prodVer = getProdVer(currentURL)
  if (prodVer.prod === false) {
    console.log('NON prod detected url and tenantName: ', currentURL, ': tenantName:', tenantName)
    return [
      { prefix: 'http://127.0.0.1:8098/', connectingthroughnginx: false }, // run all parts on dev machine
      { prefix: 'http://127.0.0.1:8099/', connectingthroughnginx: true }, // dev container on dev machine
      { prefix: 'http://127.0.0.1:80/', connectingthroughnginx: true } // home container on dev machine
      // { prefix: 'http://localhost:8082/', connectingthroughnginx: false },
      // { prefix: 'http://somefunnyhostname.com:8098/', connectingthroughnginx: false }
    ]
  }
  console.log('prod detected url and tenantName: ', currentURL, tenantName)
  return [
    { prefix: prodVer.prefix, connectingthroughnginx: true } // container via Kong redirects
  ]
}

function getAPIPathToCall (APIprefix, authed, apiPath) {
  if (authed) {
    if (APIprefix.connectingthroughnginx) {
      return APIprefix.prefix + 'authed/api' + apiPath
    }
    return APIprefix.prefix + 'api/authed' + apiPath
  }
  if (APIprefix.connectingthroughnginx) {
    return APIprefix.prefix + 'public/api' + apiPath
  }
  return APIprefix.prefix + 'api/public' + apiPath
}

function TryToConnectToAPIRecurring (locationsToTry, callback, apiPath) {
  var apiPrefix = locationsToTry.pop()

  var config = {
    method: 'GET',
    url: getAPIPathToCall(apiPrefix, false, apiPath)
  }
  console.log('Trying to reach API at ' + config.url)
  axios(config).then(
    (response) => {
      console.log('SUCCESS!')
      callback.ok({
        origResponse: response,
        sucessfulApiPrefix: apiPrefix
      })
    },
    (response) => {
      console.log('FAILED')
      if (locationsToTry.length > 0) {
        TryToConnectToAPIRecurring(locationsToTry, callback, apiPath)
      } else {
        callbackHelper.callbackWithSimpleError(callback, 'Failed to connect to public login API')
      }
    }
  )
}

function TryToConnectToAPI (currentHREF, tenantName, callback, apiPath) {
  var possiblePublicApiLocations = getAPIPrefixPossibilities(currentHREF, tenantName)
  TryToConnectToAPIRecurring(possiblePublicApiLocations.reverse(), callback, apiPath)
}

function updateCookieWithRefreshToken (callback, apiPrefix, tenantName, refreshToken) {
  var config = {
    method: 'POST',
    url: getAPIPathToCall(apiPrefix, false, '/login/' + tenantName + '/refresh'),
    data: {'token': refreshToken}
  }
  // console.log(config)
  // console.log(refreshToken)

  axios(config).then(
    (response) => {
      callback.ok(response)
    },
    (response) => {
      callback.error(response)
    }
  )
}

function sendRefreshRequestToGetNewJWTAndSaveItAsACookie (
  refreshFns,
  tenantName,
  apiPrefix,
  authed,
  path,
  method,
  data,
  callback,
  curPath,
  headers,
  refreshToken,
  sessionInFromFrontendUI,
  frontendRecordReturnAddressFn
) {
  refreshFns.startRefreshFN()
  var callback2 = {
    ok: function (response) {
      // Save new token data to cookie (expires in 1 day)
      Cookies.set('usersystemUserCredentials', response.data, {expires: 1, path: '/'})

      // callback ok
      refreshFns.endRefreshFN()
      refreshFns.refreshCompleteFN()

      var cookie = Cookies.get('usersystemUserCredentials')
      callAPI(refreshFns, tenantName, apiPrefix, authed, path, method, data, callback, cookie.jwtData, cookie.refresh, true, curPath, headers)
    },
    error: function (response) {
      // Refresh may have been in progress when page changed so make sure it is stopped
      refreshFns.endRefreshFN()
      moveToFrontendUI(curPath, 'Session refresh failed', '', sessionInFromFrontendUI, frontendRecordReturnAddressFn)
      // callbackHelper.callbackWithSimpleError(callback, 'TODO - refresh failed - goto login and display Session refresh failed')
    }
  }
  updateCookieWithRefreshToken(callback2, apiPrefix, tenantName, refreshToken)
}

/*
refreshFns {
  startRefreshFN,
  endRefreshFN,
  refreshCompleteFN,
  isRefreshInProgressFN,
  addPostRefreshActionFN
}
*/

function callAPI (
  refreshFns,
  tenantName,
  apiPrefix,
  authed,
  path,
  method,
  data,
  callback,
  jwtTokenData,
  refreshTokenData,
  refreshAlreadyTried = false,
  curPath = undefined,
  headers = undefined,
  sessionInFromFrontendUI = false,
  frontendRecordReturnAddressFn = null
) {
  // Path at this point should be something like /admin/usersystem/persons?pagesize=10&offset=0
  // console.log('CALL API PATH:' + path)
  if (authed) {
    if (jwtTokenData === null) {
      callbackHelper.callbackWithSimpleError(callback, 'Missing jwtTokenData Data in callAPI')
    }
  }
  if (typeof (headers) === 'undefined') {
    headers = {}
  }
  var config = {
    method: method,
    url: getAPIPathToCall(apiPrefix, authed, path),
    data: data,
    headers: headers
  }
  if (authed) {
    // Possible optiomzation - check if jwt token has expired and go direct to refresh call
    config.headers['jwt-auth-token'] = jwtTokenData.JWTToken
    // Kong can only read Authorization header- https://docs.konghq.com/hub/kong-inc/jwt/
    config.headers['Authorization'] = 'Bearer ' + jwtTokenData.JWTToken
  }

  axios(config).then(
    (response) => {
      callback.ok(response)
    },
    (response) => {
      if (authed === false) {
        callbackHelper.webserviceError(callback, response)
        return
      }
      // 401 is unauthorized - this means token has expired or isn't present so it makes sense to retry
      // 403 is forbidden - in this case the user doesn't have the required access role so no point retrying
      if (callbackHelper.getResponseStatusIfItHasOneOtherwiseNegativeOne(response) !== 401) {
        callbackHelper.webserviceError(callback, response)
        return
      }
      // Only code 401 gets here
      if (!refreshAlreadyTried) {
        if (refreshFns.isRefreshInProgressFN()) {
          // console.log('Got a 401 but as a refresh is in progress storing it for retry')
          var callback3 = {
            ok: function (response) {
              // console.log('FUTURE CALLBACK OK')
              var cookie = Cookies.get('usersystemUserCredentials')
              callAPI(refreshFns, tenantName, apiPrefix, authed, path, method, data, callback, cookie.jwtData, cookie.refresh, true, curPath, headers)
            },
            error: callback.error
          }
          refreshFns.addPostRefreshActionFN(callback3)
          return
        }
        sendRefreshRequestToGetNewJWTAndSaveItAsACookie(
          refreshFns,
          tenantName,
          apiPrefix,
          authed,
          path,
          method,
          data,
          callback,
          curPath,
          headers,
          refreshTokenData.token,
          sessionInFromFrontendUI,
          frontendRecordReturnAddressFn
        )
      } else {
        // Refresh may have been in progress when page changed so make sure it is stopped
        refreshFns.endRefreshFN()
        moveToFrontendUI(curPath, 'Logged out due to inactivity', '', sessionInFromFrontendUI, frontendRecordReturnAddressFn)
        // callbackHelper.callbackWithSimpleError(callback, 'TODO - refresh tried - goto login and display Logged out due to inactivity')
      }
    }
  )
}

function getAlteredHost (origHost, hostLookupList) {
  for (var x in hostLookupList) {
    if (origHost.includes(hostLookupList[x].a)) {
      return hostLookupList[x].b
    }
  }
  console.log('Failed to lookup ' + origHost + ' - don\'t know how to login')
  return 'UNKNOWN'
}

function moveToFrontendUI (thisQuasarPath, message = undefined, frontendPath = undefined, movingFromFrontendUI = false, frontendRecordReturnAddressFn = null) {
  if (typeof (frontendPath) === 'undefined') {
    frontendPath = ''
  }

  if (thisQuasarPath.startsWith('/')) {
    thisQuasarPath = thisQuasarPath.substr(1)
  }

  var quasarPathForTenenat = '/' + thisQuasarPath.substr(0, thisQuasarPath.indexOf('/'))
  thisQuasarPath = '/' + thisQuasarPath

  var locationToGoTo = ''
  if (window.location.pathname.includes('/public/web/adminfrontend/')) {
    // running both in container and kong mode have /public/web/adminfrontend/ prefix so we can just replace adminfrontend with frontend to get url
    locationToGoTo = window.location.protocol + '//' + window.location.host + window.location.pathname.replace('/public/web/adminfrontend/', '/public/web/frontend/') + '#' + quasarPathForTenenat + frontendPath
  } else {
    // running on a dev machine is more complex as we need to switch over to anohter port
    var hostLookup = [
      {a: 'localhost:8082', b: 'localhost:8081'},
      {a: 'localhost:8081', b: 'localhost:8081'},
      {a: 'cat-sdts.metcarob-home.com:8082', b: 'cat-sdts.metcarob-home.com:8081'},
      {a: 'somefunnyhostname.com:5082', b: 'somefunnyhostname.com:5081'},
      {a: 'somefunnyhostname.com:5081', b: 'somefunnyhostname.com:5081'}
    ]
    locationToGoTo = window.location.protocol + '//' + getAlteredHost(window.location.host, hostLookup) + window.location.pathname + '#' + quasarPathForTenenat + frontendPath
  }
  if (movingFromFrontendUI) {
    // We are already at frontend URI, all we need to do is set INTERNAL return and move internally
    // this prevents stores being reset
    frontendRecordReturnAddressFn(thisQuasarPath, message, quasarPathForTenenat)
    return
  }

  var returnAddress = window.location.protocol + '//' + window.location.host + window.location.pathname + '#' + thisQuasarPath
  var newHREF = locationToGoTo
  var addedParam = false
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

  // console.log('locationToGoTo:', locationToGoTo)
  // console.log('usersystem_returnaddress:', encodeURIComponent(returnAddress))
  window.location.href = newHREF
}

function callAuthedAPI (commit, state, path, method, data, callback, curPath, headers, refreshFns, apiType, tenantName, apiPrefix, sessionInFromFrontendUI = false, frontendRecordReturnAddressFn = null) {
  var cookie = Cookies.get('usersystemUserCredentials')
  // console.log('cookie:', JSON.stringify(cookie))

  if (refreshFns.isRefreshInProgressFN()) {
    console.log('Preventing call in action.js because refresh is in progress')
    var callback2 = {
      ok: function (response) {
        callAPI(refreshFns, tenantName, apiPrefix, true, '/' + apiType + '/' + tenantName + path, method, data, callback, cookie.jwtData, cookie.refresh, false, curPath, headers, sessionInFromFrontendUI, frontendRecordReturnAddressFn)
      },
      error: callback.error
    }
    commit('RECORD_REFRESH_STORED_RESPONSE', callback2)
  } else {
    if (cookie.jwtData.JWTToken === 'INVALID') {
      // We have just logged in so need to get the token
      sendRefreshRequestToGetNewJWTAndSaveItAsACookie(
        refreshFns,
        tenantName,
        apiPrefix,
        true, // authed
        '/' + apiType + '/' + tenantName + path,
        method,
        data,
        callback,
        curPath,
        headers,
        cookie.refresh.token,
        sessionInFromFrontendUI,
        frontendRecordReturnAddressFn
      )
    } else {
      callAPI(refreshFns, tenantName, apiPrefix, true, '/' + apiType + '/' + tenantName + path, method, data, callback, cookie.jwtData, cookie.refresh, false, curPath, headers, sessionInFromFrontendUI, frontendRecordReturnAddressFn)
    }
  }
}

export default {
  TryToConnectToAPI: TryToConnectToAPI,
  getAPIPathToCall: getAPIPathToCall,
  callAPI: callAPI,
  callAuthedAPI: callAuthedAPI,
  moveToFrontendUI: moveToFrontendUI
}
