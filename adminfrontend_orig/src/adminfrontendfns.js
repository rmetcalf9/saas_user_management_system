
function getURLforTicketGUID (stores, ticketGUID, tenantName, ticketTypeData, tenantData) {
  var urlBase = stores.state.globalDataStore.serverInfo.Server.APIAPP_FRONTENDURL + '/#/' + tenantName + '/Ticket/'
  if (typeof (tenantData.TicketOverrideURL) !== 'undefined') {
    if (tenantData.TicketOverrideURL !== '') {
      urlBase = tenantData.TicketOverrideURL
    }
  }
  console.log('tenantData', tenantData)
  return urlBase + ticketGUID
}

export default {
  getURLforTicketGUID: getURLforTicketGUID
}
