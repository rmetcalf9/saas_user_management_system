import stores from '../store/index.js'
import { Cookies } from 'quasar'
import shared from '../sharedFns.js'

function checkLoginNeeded (to, from, next) {
  stores().commit('globalDataStore/updateTenantName', to.params.tenantName)

  // console.log('Checking to see if login is needed')
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
  stores().commit('globalDataStore/SET_LOGOUT_CLICK_CUR_ROUTE', null)

  shared.moveToLoginService(thisQuasarPath)
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
