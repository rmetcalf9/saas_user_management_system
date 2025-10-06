/*
This file contains functions to call the api client backends.
*/
import { saasServiceName } from './router/routes.js'

const authedStoreFn = 'callAuthedAPI'
const authedOrAnonStoreFn = 'callAuthedOrAnonAPI'

/*
One entry here for ecery prefix ins the python backend app
 matches prefixes foudn in /services/src/APIs/__init__.py
*/
const apiPrefixes = {
  info: { // baseapp provided endpoint
    endpoint: saasServiceName,
    path: '/info',
    storeFn: authedOrAnonStoreFn, // authedStoreFn or authedOrAnonStoreFn
    orveridePublicPrivatePart: 'public' // public or private
  },
  admin: {
    endpoint: saasServiceName,
    path: '/admin',
    storeFn: authedStoreFn,
    orveridePublicPrivatePart: 'authed'
  }
}

function callApi ({
  prefix, // must match prefix from apiPRefixes array
  router,
  store,
  path, // : queryString,
  method, // : 'get',
  postdata, // : null,
  callback // : callback,
}) {
  if (typeof (apiPrefixes[prefix]) === 'undefined') {
    console.log('ERROR invalid prefix provided to callAPI - ', prefix, apiPrefixes)
    return
  }
  let curPath // = undefined
  if (typeof (router) !== 'undefined') {
    curPath = router.currentRoute.value.fullPath
  }
  store[apiPrefixes[prefix].storeFn]({
    endpoint: apiPrefixes[prefix].endpoint,
    path: apiPrefixes[prefix].path + path,
    method,
    postdata,
    callback,
    curpath: curPath,
    orveridePublicPrivatePart: apiPrefixes[prefix].orveridePublicPrivatePart
  })
}

export default {
  callApi
}
