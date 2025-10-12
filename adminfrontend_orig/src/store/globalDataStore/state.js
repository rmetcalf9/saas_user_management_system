// Adminfrontend GlobalStore State
export default {
  readServerInfoInProgress: false,
  readServerInfoStoredResponses: [],
  refeshTokenInProgress: false,
  refeshTokenInfoStoredResponses: [],
  apiPrefix: null,
  tenantName: null,
  pageTitle: 'Default Page Title',
  logoutClickCurRoute: null,
  serverInfo: {
    Server: {
      Version: 'NotRead',
      APIAPP_APIDOCSURL: '_',
      APIAPP_FRONTENDURL: 'http://localhost:8081/'
    }
  }
}
