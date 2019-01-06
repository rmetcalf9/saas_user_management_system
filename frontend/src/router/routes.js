
/*
 * commonPreLoad called before each page load
 * We need to load the auth providers and display invalid config if it failed
 */
function commonPreLoad (to, from, next) {
//   if ((globalStore.getters.datastoreState === 'LOGGED_IN') || (globalStore.getters.datastoreState === 'LOGGED_IN_SERVERDATA_LOADED')) {
//     next()
//     return
//   }
//   next({
//     path: '/login',
//     query: { redirect: to.fullPath }
//   })
  next()
}

const routes = [
  {
    path: '/',
    component: () => import('layouts/MyLayout.vue'),
    beforeEnter: commonPreLoad,
    children: [
      { path: '', component: () => import('pages/Index.vue') }
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
