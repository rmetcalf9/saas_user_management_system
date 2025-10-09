
function getURLforTicketGUID (userManagementClientStoreStore, ticketGUID, tenantName, ticketTypeData, tenantData) {
  // saas_usersystem origionaly comes from reoutes.js
  let urlBase = userManagementClientStoreStore.getEndpointInfo('saas_usersystem').serverInfo.Server.APIAPP_FRONTENDURL + '/#/' + tenantName + '/Ticket/'
  if (typeof (tenantData.TicketOverrideURL) !== 'undefined') {
    if (tenantData.TicketOverrideURL !== '') {
      urlBase = tenantData.TicketOverrideURL
    }
  }
  return urlBase + ticketGUID
}

export default {
  getURLforTicketGUID
}
