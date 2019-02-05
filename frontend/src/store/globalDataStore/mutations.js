// Frontend GlobalStore Mutations
/*
export function someMutation (state) {
}
*/
export const updateApiPrefix = (state, apiPrefix) => {
  state.apiPrefix = apiPrefix
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
export const updateUsersystemReturnaddress = (state, usersystemReturnaddress) => {
  state.usersystemReturnaddress = usersystemReturnaddress
}
export const setMessageToDisplay = (state, message) => {
  state.messagePendingDisplay = message
}
export const setMessageDisplayed = (state) => {
  state.messagePendingDisplay = null
}
