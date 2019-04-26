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
export function START_REFRESH (state) {
  state.refeshTokenInProgress = true
  state.refeshTokenInfoStoredResponses = []
}
export function END_REFRESH (state) {
  state.refeshTokenInProgress = false
}
export function RECORD_REFRESH_STORED_RESPONSE (state, callback) {
  state.refeshTokenInfoStoredResponses.push(callback)
}
export function REFRESH_STORED_RESPONSE_PROCESS_COMPLETE (state) {
  state.refeshTokenInfoStoredResponses = []
}
