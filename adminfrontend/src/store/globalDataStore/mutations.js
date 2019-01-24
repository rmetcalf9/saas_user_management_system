// Adminfrontend GlobalStore
/*
export function someMutation (state) {
}
*/

export const updateApiPrefix = (state, apiPrefix) => {
  state.apiPrefix = apiPrefix
}
export const updateTenantName = (state, tenantName) => {
  state.tenantName = tenantName
}
export const updateServerInfo = (state, serverInfo) => {
  state.serverInfo = serverInfo
}

export function SET_PAGE_TITLE (state, newTitle) {
  state.pageTitle = newTitle
}

export function SET_LOGOUT_CLICK_CUR_ROUTE (state, curRoute) {
  state.logoutClickCurRoute = curRoute
}

export function START_READ_SERVER_INFO (state) {
  state.readServerInfoInProgress = true
}
export function END_READ_SERVER_INFO (state) {
  state.readServerInfoInProgress = false
}
