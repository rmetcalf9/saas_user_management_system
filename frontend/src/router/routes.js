import stores from '../store/index.js'

function isValueHeld (a) {
  if (typeof (a) === 'undefined') return null
  if (a === null) return false
  return true
}

function _ensurePassedTenenatIsLoaded (to, from, next, successCallback) {
  if (isValueHeld(from.query.usersystem_returnaddress)) {
    var decoded = decodeURIComponent(from.query.usersystem_returnaddress)
    // console.log('Frontend router got return address:', decoded)
    stores().commit('globalDataStore/updateUsersystemReturnaddress', decoded)
  }
  if (isValueHeld(from.query.usersystem_message)) {
    var decoded2 = decodeURIComponent(from.query.usersystem_message)
    stores().commit('globalDataStore/setMessageToDisplay', decoded2)
  }
  if (stores().state.globalDataStore.tenantInfo !== null) {
    if (stores().state.globalDataStore.tenantInfo.Name === to.params.tenantName) {
      successCallback(to, from, next)
      return
    }
  }
  console.log('Loaded store differs from param, redirecting')
  next({
    path: '/' + to.params.tenantName,
    query: { usersystem_redirect: to.fullPath }
  })
}

function ensurePassedTenantIsLoaded (to, from, next) {
  _ensurePassedTenenatIsLoaded(to, from, next, function (to, from, next) { next() })
}

function selectAuthBeforeEnter (to, from, next) {
  _ensurePassedTenenatIsLoaded(to, from, next, function (to, from, next) {
    if (stores().state.globalDataStore.tenantInfo.AuthProviders.length === 1) {
      stores().commit('globalDataStore/updateSelectedAuthProvGUID', stores().state.globalDataStore.tenantInfo.AuthProviders[0].guid)
      next({
        path: '/' + to.params.tenantName + '/AuthProvider/' + stores().state.globalDataStore.tenantInfo.AuthProviders[0].Type
      })
    }
    next()
  })
}

const routes = [
  {
    path: '/:tenantName',
    component: () => import('pages/CheckTenant.vue')
  },
  {
    path: '/:tenantName/selectAuth',
    component: () => import('pages/SelectAuth.vue'),
    beforeEnter: selectAuthBeforeEnter
  },
  {
    path: '/:tenantName/AuthProvider/internal',
    component: () => import('pages/AuthProvider_internal.vue'),
    beforeEnter: ensurePassedTenantIsLoaded
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
