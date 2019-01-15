import stores from '../store/index.js'

function isValueHeld (a) {
  if (typeof (a) === 'undefined') return null
  if (a === null) return false
  return true
}

function ensurePassedTenantIsLoaded (to, from, next) {
  if (isValueHeld(from.query.usersystem_returnaddress)) {
    stores().commit('globalDataStore/updateUsersystemReturnaddress', from.query.usersystem_returnaddress)
  }
  if (stores().state.globalDataStore.tenantInfo !== null) {
    if (stores().state.globalDataStore.tenantInfo.Name === to.params.tenantName) {
      next()
      return
    }
  }
  console.log('Loaded store differs from param, redirecting')
  next({
    path: '/' + to.params.tenantName,
    query: { usersystem_redirect: to.fullPath }
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
    beforeEnter: ensurePassedTenantIsLoaded
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
