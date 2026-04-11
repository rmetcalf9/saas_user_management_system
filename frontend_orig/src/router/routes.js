import stores from '../store/index.js'

function isValueHeld (a) {
  if (typeof (a) === 'undefined') return null
  if (a === null) return false
  return true
}

function _getDecodedValueFromQuery (to, from, valueName) {
  if (isValueHeld(from.query[valueName])) {
    return decodeURIComponent(from.query[valueName])
  } else if (isValueHeld(to.query[valueName])) {
    return decodeURIComponent(to.query[valueName])
  }
  return undefined
}

function _ensurePassedTenenatIsLoaded (to, from, next, successCallback) {
  // console.log('_ensurePassedTenenatIsLoaded FROM', from)
  // console.log('_ensurePassedTenenatIsLoaded TO', to)
  // console.log('_ensurePassedTenenatIsLoaded internal ra:', stores().state.globalDataStore.usersystemReturnaddressInternal)
  var a = _getDecodedValueFromQuery(to, from, 'usersystem_returnaddress')
  if (typeof (a) !== 'undefined') {
    stores().commit('globalDataStore/updateUsersystemReturnaddress', a)
  }
  var b = _getDecodedValueFromQuery(to, from, 'usersystem_message')
  if (typeof (b) !== 'undefined') {
    stores().commit('globalDataStore/setMessageToDisplay', b)
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
    query: {
      usersystem_redirect: to.fullPath
    }
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
  },
  {
    path: '/:tenantName/AuthProvider/google',
    component: () => import('pages/AuthProvider_google.vue'),
    beforeEnter: ensurePassedTenantIsLoaded
  },
  {
    path: '/:tenantName/AuthProvider/facebook',
    component: () => import('pages/AuthProvider_facebook.vue'),
    beforeEnter: ensurePassedTenantIsLoaded
  },
  {
    path: '/:tenantName/AuthProvider/ldap',
    component: () => import('pages/AuthProvider_ldap.vue'),
    beforeEnter: ensurePassedTenantIsLoaded
  },
  {
    path: '/:tenantName/SecuritySettings',
    component: () => import('pages/SecuritySettings.vue'),
    beforeEnter: ensurePassedTenantIsLoaded
  },
  {
    path: '/:tenantName/Ticket/:ticketGUID',
    component: () => import('pages/Ticket.vue'),
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
