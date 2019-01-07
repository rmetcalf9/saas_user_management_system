import stores from '../store/index.js'

function ensurePassedTenantIsLoaded (to, from, next) {
  if (stores().state.globalDataStore.tenant === to.params.tenantName) {
    next()
    return
  }
  console.log('Loaded store differs from param, redirecting')
  next({
    path: '/' + to.params.tenantName
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
