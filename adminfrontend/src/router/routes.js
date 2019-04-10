import stores from '../store/index.js'
import { Cookies } from 'quasar'
import shared from '../sharedFns.js'

function directToLoginPage (to, from, next) {
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

  directToLoginPage(to, from, next)
}

function beforeEnterMainIndexChildPage (to, from, next, pageTitle) {
  // console.log('beforeEnterMainIndexChildPage')
  stores().commit('globalDataStore/SET_PAGE_TITLE', pageTitle)
  return checkLoginNeeded(to, from, next)
}

function logoutPageFn (to, from, next, pageTitle) {
  stores().commit('globalDataStore/SET_PAGE_TITLE', pageTitle)
  directToLoginPage(to, from, next)
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
      { path: 'tenants/:selTenantNAME', component: () => import('pages/Tenant.vue'), beforeEnter: function fn (to, from, next) { beforeEnterMainIndexChildPage(to, from, next, 'Tenant') } },
      { path: 'users/:selUserID', component: () => import('pages/User.vue'), beforeEnter: function fn (to, from, next) { beforeEnterMainIndexChildPage(to, from, next, 'User') } },
      { path: 'users', component: () => import('pages/Users.vue'), beforeEnter: function fn (to, from, next) { beforeEnterMainIndexChildPage(to, from, next, 'Users') } },
      { path: 'persons', component: () => import('pages/Persons.vue'), beforeEnter: function fn (to, from, next) { beforeEnterMainIndexChildPage(to, from, next, 'Persons') } },
      { path: 'persons/:selPerGUID', component: () => import('pages/Person.vue'), beforeEnter: function fn (to, from, next) { beforeEnterMainIndexChildPage(to, from, next, 'Person') } },
      { path: 'usersettings', component: () => import('pages/UserSettings.vue'), beforeEnter: function fn (to, from, next) { beforeEnterMainIndexChildPage(to, from, next, 'User Settings') } },
      { path: 'logout', beforeEnter: function fn (to, from, next) { logoutPageFn(to, from, next, 'Logout') } }
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
