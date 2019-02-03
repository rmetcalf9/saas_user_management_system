/*
Functions shared between frontend and adminfrontend

MUST EDIT THE ADMINFRONTEND version and use process to copy across

(This and callbackHelper)
*/
import callbackHelper from './callbackHelper'
import axios from 'axios'
import { Cookies } from 'quasar'

function getAPIPrefixPossibilities (currentURL, tenantName) {
  // TODO how do we know what vx should be?
  console.log('TODO Work out on prod vx based on current url and tenantName: ', currentURL, tenantName)
  return [
    { prefix: '/vx/', kong: true },
    { prefix: 'http://localhost:8082/', kong: false },
    { prefix: 'http://somefunnyhostname.com:8098/', kong: false },
    { prefix: 'http://somefunnyhostname.com:5098/', kong: false },
    { prefix: 'http://127.0.0.1:8098/', kong: false }
  ]
}

function getAPIPathToCall (APIprefix, authed, apiPath) {
  if (authed) {
    if (APIprefix.kong) {
      return APIprefix.prefix + 'authed/api' + apiPath
    }
    return APIprefix.prefix + 'api/authed' + apiPath
  }
  if (APIprefix.kong) {
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
  console.log('Tyring to reach API at ' + config.url)
  axios(config).then(
    (response) => {
      callback.ok({
        origResponse: response,
        sucessfulApiPrefix: apiPrefix
      })
    },
    (response) => {
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

function updateCookieWithRefreshToken (callback, apiPrefix, tenantName, jwtTokenData, refreshTokenData) {
  var config = {
    method: 'POST',
    url: getAPIPathToCall(apiPrefix, false, '/login/' + tenantName + '/refresh'),
    data: {'token': refreshTokenData.token}
  }
  console.log(config)
  console.log(refreshTokenData)

  axios(config).then(
    (response) => {
      // Save new token data to cookie (expires in 1 day)
      Cookies.set('usersystemUserCredentials', response.data, {expires: 1, path: '/'})

      // callback ok
      callback.ok(response)
    },
    (response) => {
      callback.error(response)
    }
  )
}

function callAPI (tenantName, apiPrefix, authed, path, method, data, callback, jwtTokenData, refreshTokenData, refreshAlreadyTried = false) {
  if (authed) {
    if (jwtTokenData === null) {
      callbackHelper.callbackWithSimpleError(callback, 'Missing jwtTokenData Data in callAPI')
    }
  }

  var config = {
    method: method,
    url: getAPIPathToCall(apiPrefix, authed, path),
    data: data
  }
  if (authed) {
    // Possible optiomzation - check if jwt token has expired and go direct to refresh call
    config.headers = {'jwt-auth-token': jwtTokenData.JWTToken}
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
      if (callbackHelper.getResponseStatusIfItHasOneOtherwiseNegativeOne(response) !== 401) {
        callbackHelper.webserviceError(callback, response)
        return
      }
      if (!refreshAlreadyTried) {
        var callback2 = {
          ok: function (response) {
            // callAPI with new jwtTokenData value and refresh value - ignore response
            var cookie = Cookies.get('usersystemUserCredentials')
            callAPI(tenantName, apiPrefix, authed, path, method, data, callback, cookie.jwtData, cookie.refresh, true)
          },
          error: function (response) {
            callbackHelper.callbackWithSimpleError(callback, 'TODO - refresh failed - goto login and display Session refresh failed')
          }
        }
        updateCookieWithRefreshToken(callback2, apiPrefix, tenantName, jwtTokenData, refreshTokenData)
      } else {
        callbackHelper.callbackWithSimpleError(callback, 'TODO - refresh tried - goto login and display Logged out due to inactivity')
      }
    }
  )
}

export default {
  TryToConnectToAPI: TryToConnectToAPI,
  getAPIPathToCall: getAPIPathToCall,
  callAPI: callAPI
}
