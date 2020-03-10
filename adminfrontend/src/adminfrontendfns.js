
function getURLforTicketGUID (stores, ticketGUID, tenantName) {
  return stores.state.globalDataStore.serverInfo.Server.APIAPP_FRONTENDURL + '/#/' + tenantName + '/Ticket/' + ticketGUID
}

export default {
  getURLforTicketGUID: getURLforTicketGUID
}
