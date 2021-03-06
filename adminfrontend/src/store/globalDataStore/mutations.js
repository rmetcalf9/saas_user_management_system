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
  if (typeof (state.serverInfo.Server.APIAPP_FRONTENDURL) === 'undefined') {
    state.serverInfo.Server.APIAPP_FRONTENDURL = 'http://localhost:8081/'
  }
}

export function SET_PAGE_TITLE (state, newTitle) {
  state.pageTitle = newTitle
}

export function SET_LOGOUT_CLICK_CUR_ROUTE (state, curRoute) {
  state.logoutClickCurRoute = curRoute
}

export function START_READ_SERVER_INFO (state) {
  state.readServerInfoInProgress = true
  state.readServerInfoStoredResponses = []
}
export function END_READ_SERVER_INFO (state) {
  state.readServerInfoInProgress = false
}
export function RECORD_READ_SERVER_INFO_STORED_RESPONSE (state, callback) {
  state.readServerInfoStoredResponses.push(callback)
}
export function READ_SERVER_INFO_STORED_RESPONSE_PROCESS_COMPLETE (state) {
  state.readServerInfoStoredResponses = []
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
