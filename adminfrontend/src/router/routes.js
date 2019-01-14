
function getAlteredHost (origHost, hostLookupList) {
  for (var x in hostLookupList) {
    if (origHost.includes(hostLookupList[x].a)) {
      return hostLookupList[x].b
    }
  }
  return origHost
}

function checkLoginNeeded (to, from, next) {
  var loginTokenPresent = false
  var returningFromLoginSystem = false
  if (loginTokenPresent) {
    next()
    return
  }
  if (returningFromLoginSystem) {
    console.log('Returning from login system not implemented yet')
    next()
    return
  }
  console.log('TODO work out where to forward to')
  // ##console.log(this.$route.query.page)
  // ##console.log(to.query)

  // https://xx.com:123/a/b/c/vx/public/web/frontend/#/***
  // https://xx.com:123/a/b/c/vx/public/web/adminfrontend/#/***

  //
  var returnAddress = window.location.href

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
    locationToGoTo = window.location.protocol + '//' + window.location.host + window.location.pathname.replace('/public/web/adminfrontend/', '/public/web/frontend/') + window.location.hash
  } else {
    var hostLookup = [
      {a: 'localhost:8082', b: 'localhost:8081'},
      {a: 'cat-sdts.metcarob-home.com:8082', b: 'cat-sdts.metcarob-home.com:8081'},
      {a: 'somefunnyhostname.com:8082', b: 'somefunnyhostname.com:8081'}
    ]
    locationToGoTo = window.location.protocol + '//' + getAlteredHost(window.location.host, hostLookup) + window.location.pathname + window.location.hash
  }

  console.log('GOTO:' + locationToGoTo)
  console.log('RET:' + returnAddress)
  next()
}

const routes = [
  {
    path: '/',
    component: () => import('layouts/MyLayout.vue'),
    beforeEnter: checkLoginNeeded,
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
