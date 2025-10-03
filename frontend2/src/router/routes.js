import saasApiClient from '../saasAplClient'
import { getRjmStateChangeObj } from '../stores/saasUserManagementClientStore'
import { Cookies } from 'quasar'
import saasApiClientServerRequestQueue from '../saasApiClientServerRequestQueue'

const prodDomain = 'platform.challengeswipe.com'
const preferredTenantName = 'defaulttenant'
export const saasServiceName = 'saas_' + preferredTenantName
const preferredFullLocation = 'https://' + prodDomain + '/#/' + preferredTenantName + '/'

function allowNotLoggedInForPath (tenantName, path) {
  // All pages require login accept profile which may be public
  if (path === '/' + tenantName + '/') {
    return true
  }
  if (path === '/' + tenantName + '/debug') {
    return true
  }
  const pathArr = path.split('/')
  if (pathArr.length === 4 && path.startsWith('/' + tenantName + '/promo/')) {
    return true
  }
  // if (path.startsWith('/' + tenantName + '/login/')) {
  //   return true
  // }
  return false
}

function retrieveLoginFromCookieAndSaveToStateIfFound (rjmStateChange) {
  if (!Cookies.has('saasUserManagementClientStoreCredentials')) {
    return // no cookie so do nothing
  }
  const cookieData = Cookies.get('saasUserManagementClientStoreCredentials')
  if (typeof (cookieData) === 'undefined') {
    return // blanked cookie so do nothing (cookies are blanked when refresh fails)
  }
  if (typeof (cookieData.loginTenantName) === 'undefined') {
    // require cookie to have the loginTenantName
    return
  }
  if (cookieData.loginTenantName !== rjmStateChange.getFromState('loginService').tenantName) {
    // do not accept a cookie without a loginTenantName that matches this one
    return
  }
  rjmStateChange.executeAction('setLoginFromCookie', { cookieData })
}

function actionsForLoggedInUser ({ to, rjmStateChange }) {
  // Empty function. Good place for loading logged in users details
}

function notLoggedInBeforeEnter (to, from, next, rjmStateChange) {
  redirectionlogger('notLoggedInBeforeEnter')

  const notLoggedInPath = '/' + to.params.tenantName + '/notloggedin'
  const afterLoginPath = '/' + to.params.tenantName

  const sendUserToNotLoggedInPage = function () {
    sendUserToPage(to, next, notLoggedInPath, to.path)
    sendUserToLogin(to, rjmStateChange)
  }
  const sendUserToDefaultAfterLoginPage = function () {
    sendUserToPage(to, next, afterLoginPath)
  }

  const callback = {
    ok: function (response) {
      // At this point the retervial token and cookie has been read to see if user is logged in

      // console.log('sendUserToNotLoggedInPage callback OK')
      // Rather than check if user is logged in check they have the role hasaccount

      const hasAccount = rjmStateChange.getFromState('hasRole')('hasaccount')
      if (hasAccount) {
        if (to.path === notLoggedInPath) {
          console.log('about to sendUserToDefaultAfterLoginPage', to.path)
          sendUserToDefaultAfterLoginPage()
          return
        } else {
          actionsForLoggedInUser({ to, rjmStateChange })
          next()
          return
        }
      }

      // At this point we know the user has no login credentials
      if (allowNotLoggedInForPath(to.params.tenantName, to.path)) {
        redirectionlogger('notLoggedInBeforeEnter - page is allowed for not logged in user')
        next()
        return
      }
      sendUserToNotLoggedInPage()
      console.log('sendUserToNotLoggedInPage callback OK END')
    },
    error: function (response) {
      console.log('ERROR router.js fds43 ERR', response)
      sendUserToNotLoggedInPage()
    }
  }

  if (typeof (to.query.jwtretervialtoken) === 'undefined') {
    // console.log('Checking for logon cookie')
    if (rjmStateChange.getFromState('loginService').processState !== 0) return
    retrieveLoginFromCookieAndSaveToStateIfFound(rjmStateChange)
    callback.ok('')
  } else {
    redirectionlogger('Detected return from login')
    // gtm not deployed yet
    // gtm.logEvent('login', 'LoginComplete', 'Done', 0)
    rjmStateChange.executeAction('processRecievedJWTretervialtoken', {
      jwtretervialtoken: to.query.jwtretervialtoken,
      callback,
      curpath: to.path,
      startAllBackendCallQueuesFn: saasApiClientServerRequestQueue.getStartAllBackendCallQueuesFn({ curpath: to.path })
    })
  }
}

function globalBeforeEnter (to, from, next, callSrc) {
  redirectionlogger('globalBeforeEnter topath=' + to.path + ' source of globalBeforeEnter=' + callSrc)

  const x = redirectToProperDomain()
  if (x.wasRedirected) return
  if (redirectToURLWithExpandedCampaignParams()) return

  const rjmStateChange = getRjmStateChangeObj()

  saasApiClient.registerEndpointsWithStore({
    saasServiceName,
    getRjmStateChangeFn: getRjmStateChangeObj,
    prodDomain,
    runtype: x.runtype,
    tenantName: to.params.tenantName,
    doneFn: function () {
      saasApiClient.startEndpointIdentificationProcess({
        endpointName: saasServiceName,
        getRjmStateChangeFn: getRjmStateChangeObj
      })
    }
  })
  const rjmStateChange2 = getRjmStateChangeObj()
  if (rjmStateChange2.getFromState('isLoggedIn')) {
    actionsForLoggedInUser({ to, rjmStateChange })
    next()
  } else {
    notLoggedInBeforeEnter(to, from, next, rjmStateChange)
  }
}

function redirectToURLWithExpandedCampaignParams () {
  const redirectUTMSource = 'defaulttenant'
  const urlParams = new URLSearchParams(window.location.search)
  if (urlParams.has('l')) {
    // Auto tag an internal campaign
    const newLocation = 'https://' + prodDomain + '/?utm_source=' + redirectUTMSource + '&utm_medium=' + urlParams.get('l') + '&utm_campaign=Internal%20app%20Share'
    redirectionlogger('redirectToURLWithExpandedCampaignParams->HREF(' + newLocation + ')')
    window.location.href = newLocation
    return true
  }
  return false
}

function sendUserToPage (to, next, targetPage, requestedPage) {
  if (to.path === targetPage) {
    // console.log('a')
    redirectionlogger('sendUserToPage->next()')
    next()
    return
  }
  if (typeof (requestedPage) !== 'undefined') {
    targetPage = targetPage + '?requestedPage=' + requestedPage
  }
  // console.log('AAA:', targetPage)
  redirectionlogger('sendUserToPage->next(' + targetPage + ')')
  next({
    path: targetPage
  })
}

function sendUserToLogin (to, rjmStateChange) {
  const returnAddress = window.location.protocol + '//' + window.location.host + window.location.pathname + '#' + to.path
  window.location.href = rjmStateChange.getFromState('getLoginUIURLFn')(undefined, '/', returnAddress)
}

function redirectToProperDomain () {
  // return
  // {
  //   wasRedirected: true if redirection is required, false otherwise
  //   runtype: 'proddomain' - if running in prodDomain, 'prodapi' if running in api.metcarob.com, 'dev' otherwise
  // }
  // host api.metcarob.com can never be http - kong will block
  // host www.thumbsum.co must be moved non-www and https if not already
  // host thumbsum.co must be moved to https if not
  // console.log('location.protocol:', location.protocol)
  // console.log('location.hostname:', location.hostname)
  const subDomainsToRedirectFrom = ['www']
  let runtype = 'dev'
  const arrayLength = subDomainsToRedirectFrom.length
  for (let i = 0; i < arrayLength; i++) {
    if (location.hostname === subDomainsToRedirectFrom[i] + '.' + prodDomain) {
      redirectionlogger('redirectToProperDomain 1->HREF(' + preferredFullLocation + ')')
      window.location.href = preferredFullLocation
      return { wasRedirected: true }
    }
  }

  if (location.hostname === prodDomain) {
    if (location.protocol === 'http:') {
      redirectionlogger('redirectToProperDomain 2->HREF(' + preferredFullLocation + ')')
      window.location.href = preferredFullLocation
      return { wasRedirected: true }
    }
    runtype = 'proddomain'
  } else { // not prod domain
    if (location.hostname === 'api.metcarob.com') {
      runtype = 'prodapi'
    } else {
      if (location.hostname !== 'localhost') {
        if (location.hostname !== 'localhost:8080') {
          if (location.hostname !== '127.0.0.1') {
            if (location.hostname !== '127.0.0.1:8080') {
              // May be someone else hosting this code
              redirectionlogger('redirectToProperDomain 3->HREF(' + preferredFullLocation + ')')
              window.location.href = preferredFullLocation
              return { wasRedirected: true }
            }
          }
        }
      }
    }
  }
  return { wasRedirected: false, runtype }
}

const logger = function (msg, messagetype) {
  let log = true
  if (messagetype === 'redirect') {
    log = true
  }
  if (log) {
    console.log(messagetype, ':', msg)
  }
}
const redirectionlogger = function (msg) {
  logger(msg, 'redirect')
}

function redirectToDefaultTenant (to, from, next) {
  redirectionlogger('redirectToDefaultTenant')
  const x = redirectToProperDomain()
  if (x.wasRedirected) return
  if (redirectToURLWithExpandedCampaignParams()) return
  // window.location.href = window.location.href + preferredTenantName + '/'
  redirectionlogger('redirectToDefaultTenant - about to call sendUserToPage')
  sendUserToPage(to, next, '/' + preferredTenantName + '/')
}

function getGlobalBeforeEnterFn (callSrc) {
  return function (to, from, next) {
    redirectionlogger('S-Start of GlobalBeforeEnterFn:' + callSrc)
    globalBeforeEnter(to, from, next, callSrc)
    redirectionlogger('X-End of GlobalBeforeEnterFn:' + callSrc)
  }
}

const routes = [
  {
    path: '/',
    beforeEnter: redirectToDefaultTenant
  },
  {
    path: '/:tenantName/',
    component: () => import('layouts/MainLayout.vue'),
    beforeEnter: getGlobalBeforeEnterFn('main'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue'), beforeEnter: getGlobalBeforeEnterFn('Index') },
      { path: 'debug', name: 'Debug', component: () => import('pages/DebugPage.vue'), beforeEnter: getGlobalBeforeEnterFn('debug') }
    ]
  },

  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]

export default routes
