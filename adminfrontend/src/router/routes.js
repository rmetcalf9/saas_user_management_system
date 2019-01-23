import stores from '../store/index.js'
import { Cookies } from 'quasar'

function getAlteredHost (origHost, hostLookupList) {
  for (var x in hostLookupList) {
    if (origHost.includes(hostLookupList[x].a)) {
      return hostLookupList[x].b
    }
  }
  console.log('Failed to lookup ' + origHost + ' - don\'t know how to login')
  return 'UNKNOWN'
}

function checkLoginNeeded (to, from, next) {
  console.log('Checking to see if login is needed')
  var authCookieSet = Cookies.has('usersystemUserCredentials')
  if (authCookieSet) {
    // console.log('Already logged in')
    // var cookie = Cookies.get('usersystemUserCredentials')
    // var jwtTokenData = cookie.jwtData
    // var refreshTokenData = cookie.refresh
    // console.log('Cookie Val:', cookie)
    // console.log('JWT Val:', jwtTokenData)
    // console.log('refresh Val:', refreshTokenData)
    next()
    return
  }
  var thisQuasarPath = to.path
  var logoutClickCurRoute = stores().state.globalDataStore.logoutClickCurRoute
  if (typeof (logoutClickCurRoute) !== 'undefined') {
    if (logoutClickCurRoute !== null) {
      thisQuasarPath = logoutClickCurRoute
    }
  }
  if (thisQuasarPath.startsWith('/')) {
    thisQuasarPath = thisQuasarPath.substr(1)
  }
  var quasarPathForTenenat = '#/' + thisQuasarPath.substr(0, thisQuasarPath.indexOf('/'))
  thisQuasarPath = '#/' + thisQuasarPath

  stores().commit('globalDataStore/SET_LOGOUT_CLICK_CUR_ROUTE', null)
  // ##console.log(this.$route.query.page)
  // ##console.log(to.query)

  // https://xx.com:123/a/b/c/vx/public/web/frontend/#/***
  // https://xx.com:123/a/b/c/vx/public/web/adminfrontend/#/***

  // window.location.href contains old path if we are redirecting

  // http:
  // console.log(window.location.protocol)

  // localhost:8002
  // console.log(window.location.host)

  // Path name is the bit before the hash
  // /
  // /a/b/c/vx/public/web/adminfrontend/
  // console.log(window.location.pathname)

  // #/
  // #/usersystem/selectAuth
  // console.log(window.location.hash)

  var locationToGoTo = ''
  if (window.location.pathname.includes('/public/web/adminfrontend/')) {
    locationToGoTo = window.location.protocol + '//' + window.location.host + window.location.pathname.replace('/public/web/adminfrontend/', '/public/web/frontend/') + quasarPathForTenenat
  } else {
    var hostLookup = [
      {a: 'localhost:8082', b: 'localhost:8081'},
      {a: 'cat-sdts.metcarob-home.com:8082', b: 'cat-sdts.metcarob-home.com:8081'},
      {a: 'somefunnyhostname.com:5082', b: 'somefunnyhostname.com:5081'}
    ]
    locationToGoTo = window.location.protocol + '//' + getAlteredHost(window.location.host, hostLookup) + window.location.pathname + quasarPathForTenenat
  }
  var returnAddress = window.location.protocol + '//' + window.location.host + window.location.pathname + thisQuasarPath

  window.location.href = locationToGoTo + '?usersystem_returnaddress=' + encodeURIComponent(returnAddress)
  // console.log('GOTO:' + locationToGoTo)
  // console.log('RET:' + returnAddress)
  next()
}

function beforeEnterMainIndexChildPage (to, from, next, pageTitle) {
  // console.log('beforeEnterMainIndexChildPage')
  stores().commit('globalDataStore/SET_PAGE_TITLE', pageTitle)
  return checkLoginNeeded(to, from, next)
}

const routes = [
  {
    path: '/', redirect: '/usersystem/'
  },
  {
    path: '/:tenantName/',
    component: () => import('layouts/MyLayout.vue'),
    beforeEnter: checkLoginNeeded,
    children: [
      { path: '', component: () => import('pages/Index.vue') },
      { path: 'tenants', component: () => import('pages/Tenants.vue'), beforeEnter: function fn (to, from, next) { beforeEnterMainIndexChildPage(to, from, next, 'Tenants') } },
      { path: 'users', component: () => import('pages/Users.vue'), beforeEnter: function fn (to, from, next) { beforeEnterMainIndexChildPage(to, from, next, 'Users') } },
      { path: 'logout', beforeEnter: function fn (to, from, next) { beforeEnterMainIndexChildPage(to, from, next, 'Logout') } }
    ]
  }
]

// Always leave this as last one
if (process.env.MODE !== 'ssr') {
  routes.push({
    path: '*',
    component: () => import('pages/Error404.vue')
  })
}

export default routes
