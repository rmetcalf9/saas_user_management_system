/*
  My API Client to help the frontend talk to the back end.
   - Handles finding the right endpoint (uses store)
*/
import rjmversion from './rjmversion.js'
import saasApiClientEndpointIdentificationProcess from './saasApiClientEndpointIdentificationProcess'

// Change this variable to use different major bersions of login service
const prodLoginServiceBaseURL = 'https://api.metcarob.com/saas_user_management/v0/'

function finishEndPointIdentificationHook (rjmStateChange, { serverInfo, apiPrefix }) {
  // Do nothing
}

function requestUserRelogin (message, curpath, rjmStateChange) {
  if (typeof (curpath) === 'undefined') {
    console.log('requestUserRelogin recieved undefined curpath - stopping as this is a BUG')
    console.log('requestUserRelogin', message, curpath, rjmStateChange)
    return
  }
  const thisQuasarPath = curpath
  const returnAddress = window.location.protocol + '//' + window.location.host + window.location.pathname + '#' + thisQuasarPath
  if (returnAddress.includes('saas_user_management')) {
    console.log('requestUserRelogin: error, found that returnAddress includes saas_user_management')
    console.log('window.location.protocol', window.location.protocol)
    console.log('window.location.host', window.location.host)
    console.log('window.location.pathname', window.location.pathname)
    console.log('thisQuasarPath', thisQuasarPath)
    // TODO replace line with new store
    // console.log('Did not preform redirect to:', stores.getters['saasUserManagementClientStore/getLoginUIURLFn'](message, '/', returnAddress))
  } else {
    window.location.href = rjmStateChange.getFromState('getLoginUIURLFn')(message, '/', returnAddress)
  }
}

function getProdVer (currentURL, endpointName) {
  let searchStr = '/' + endpointName + '/test/v'
  let testPos = currentURL.indexOf(searchStr)
  const searchStr2 = '/public/web/'
  if (testPos !== -1) {
    const midArg = currentURL.substring(currentURL.indexOf(searchStr) + searchStr.length)
    const secondPos = midArg.indexOf(searchStr2)
    if (secondPos === -1) {
      return {
        prod: false
      }
    }
    return {
      prod: true,
      ver: parseInt(midArg.substring(0, secondPos)),
      test: true,
      prefix: currentURL.substring(0, currentURL.indexOf(searchStr)) + searchStr + parseInt(midArg.substring(0, secondPos))
    }
  } else {
    searchStr = '/' + endpointName + '/v'
    testPos = currentURL.indexOf(searchStr)
    if (testPos !== -1) {
      const midArg = currentURL.substring(currentURL.indexOf(searchStr) + searchStr.length)
      const secondPos = midArg.indexOf(searchStr2)
      if (secondPos === -1) {
        return {
          prod: false
        }
      }
      return {
        prod: true,
        ver: parseInt(midArg.substring(0, secondPos)),
        test: false,
        prefix: currentURL.substring(0, currentURL.indexOf(searchStr)) + searchStr + parseInt(midArg.substring(0, secondPos))
      }
    }
  }
  return {
    prod: false
  }
}

export function registerEndpointsWithStore (params) {
  const rjmStateChange = params.getRjmStateChangeFn()
  const isEndpointsRegistered = rjmStateChange.getFromState('getIsEndpointsRegistered')
  if (isEndpointsRegistered) return
  rjmStateChange.executeAction('endpointsAreRegistered')
  const finishEndPointIdentificationHookFN = function (params) {
    finishEndPointIdentificationHook(rjmStateChange, params)
  }

  if (params.runtype === 'proddomain') {
    const majorCodeVersion = rjmversion.codebasever.split('.')[0]
    console.log('PROD taking api version from code', params.runtype, majorCodeVersion)
    rjmStateChange.executeAction('registerLoginEndpoint', {
      baseUrl: prodLoginServiceBaseURL,
      tenantName: params.tenantName
    })

    // https://api.metcarob.com/saas_linkvis/v0
    const possibleApiPrefixes = [{ prefix: 'https://api.metcarob.com/' + params.saasServiceName + '/v' + majorCodeVersion, connectingthroughnginx: true, apitype: 'public' }]
    rjmStateChange.executeAction('registerEndpoint', {
      endpointName: params.saasServiceName,
      apiPrefixIdentificationProcessConfig: {
        possibleApiPrefixes
      },
      finishEndPointIdentificationHook: finishEndPointIdentificationHookFN
    })
  } else {
    const prodVer = getProdVer(window.location.href, params.saasServiceName)
    if (prodVer.prod) {
      console.log('PROD taking api version from url ', params.runtype)
      rjmStateChange.executeAction('registerLoginEndpoint', {
        baseUrl: prodLoginServiceBaseURL,
        tenantName: params.tenantName
      })
      const possibleApiPrefixes2 = [{ prefix: prodVer.prefix, connectingthroughnginx: true, apitype: 'public' }]
      rjmStateChange.executeAction('registerEndpoint', {
        endpointName: params.saasServiceName,
        apiPrefixIdentificationProcessConfig: {
          possibleApiPrefixes: possibleApiPrefixes2
        },
        finishEndPointIdentificationHook: finishEndPointIdentificationHookFN
      })
    } else { // Not prod ver
      console.log('NON PROD no api version needed using same basepath', params.runtype)
      rjmStateChange.executeAction('registerLoginEndpoint', {
        baseUrl: 'http://127.0.0.1:8099/',
        tenantName: params.tenantName
      })
      if (!rjmStateChange.getFromState('getIsParticularEndpointsRegistered')(params.saasServiceName)) {
        const newEndpoint = {
          endpointName: params.saasServiceName,
          apiPrefixIdentificationProcessConfig: {
            // these lines appear in the order they are attempted
            // first we are trying ./run_app_developer.sh which will be on different ports
            // then we are trying running via a container where the frontend and
            // python app are on the same port
            // usermanagement ADMIN only - also search 8099 as this is the containerised backend
            possibleApiPrefixes: [
              { prefix: 'http://127.0.0.1:8099', connectingthroughnginx: true, apitype: 'public' },
              { prefix: 'http://localhost:8098', connectingthroughnginx: false, apitype: 'public' },
              { prefix: window.location.protocol + '//' + window.location.host, connectingthroughnginx: true, apitype: 'public' }
            ]
          },
          finishEndPointIdentificationHook: finishEndPointIdentificationHookFN
        }
        rjmStateChange.executeAction('registerEndpoint', newEndpoint)
      }
    }
    if (typeof (params.doneFn) === 'undefined') {
      return
    }
    params.doneFn()
  }

  const requestUserReloginINT = function ({ message, curpath }) {
    const rjmStateChange = params.getRjmStateChangeFn()
    requestUserRelogin(message, curpath, rjmStateChange)
  }
  rjmStateChange.executeAction('registerRequestUserReloginFn', { requestUserReloginFn: requestUserReloginINT })
}

function startEndpointIdentificationProcess ({ getRjmStateChangeFn, endpointName }) {
  const rjmStateChange = getRjmStateChangeFn()
  const callback = {
    ok: function ({ serverinfoResponse, endpoint, sucessfulapiprefix }) {
    },
    error: function (response) {
    }
  }
  saasApiClientEndpointIdentificationProcess.startEndpointIdentificationProcess({
    endpointName,
    callback,
    rjmStateChange
  })
}

export default {
  registerEndpointsWithStore,
  startEndpointIdentificationProcess
}
