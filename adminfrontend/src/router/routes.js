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
  var authCookieSet = Cookies.has('usersystemUserCredentials')
  if (authCookieSet) {
    next()
    return
  }
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

  var thisQuasarPath = to.path
  if (thisQuasarPath.startsWith('/')) {
    thisQuasarPath = thisQuasarPath.substr(1)
  }
  thisQuasarPath = '#/' + thisQuasarPath
  console.log(thisQuasarPath)
  var locationToGoTo = ''
  if (window.location.pathname.includes('/public/web/adminfrontend/')) {
    locationToGoTo = window.location.protocol + '//' + window.location.host + window.location.pathname.replace('/public/web/adminfrontend/', '/public/web/frontend/') + thisQuasarPath
  } else {
    var hostLookup = [
      {a: 'localhost:8082', b: 'localhost:8081'},
      {a: 'cat-sdts.metcarob-home.com:8082', b: 'cat-sdts.metcarob-home.com:8081'},
      {a: 'somefunnyhostname.com:5082', b: 'somefunnyhostname.com:5081'}
    ]
    locationToGoTo = window.location.protocol + '//' + getAlteredHost(window.location.host, hostLookup) + window.location.pathname + thisQuasarPath
  }
  var returnAddress = window.location.protocol + '//' + window.location.host + window.location.pathname + thisQuasarPath

  window.location.href = locationToGoTo + '?usersystem_returnaddress=' + returnAddress
  // console.log('GOTO:' + locationToGoTo)
  // console.log('RET:' + returnAddress)
  next()
}

const routes = [
  {
    path: '/', redirect: '/usersystem/'
  },
  {
    path: '/:tenantName',
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
