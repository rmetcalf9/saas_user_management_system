/*
export function someMutation (state) {
}
*/
export const updateUrlToReachPublicAPI = (state, urlToReachPublicAPI) => {
  state.urlToReachPublicAPI = urlToReachPublicAPI
}
export const updateTenantInfo = (state, tenantInfo) => {
  state.tenantInfo = tenantInfo
}
export const updateTenant = (state, tenant) => {
  state.tenant = tenant
}
export const updateSelectedAuthProvGUID = (state, selectedAuthProvGUID) => {
  state.selectedAuthProvGUID = selectedAuthProvGUID
}
