const routes = [
  {
    path: '/:tenantName',
    component: () => import('pages/CheckTenant.vue')
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
