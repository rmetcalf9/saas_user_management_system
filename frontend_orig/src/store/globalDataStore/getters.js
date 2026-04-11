/*
export function someGetter (state) {
}
*/
export function getAuthProvFromGUID (state) {
  return function (authProvGUID) {
    return state.tenantInfo.AuthProviders.filter(function (prov) {
      return (prov.guid === authProvGUID)
    })[0]
  }
}
