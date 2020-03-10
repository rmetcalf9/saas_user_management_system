
function getURLforTicketGUID (stores, ticketGUID) {
  return stores.state.globalDataStore.serverInfo.Server.APIAPP_FRONTENDURL + '/#/usersystem/Ticket/' + ticketGUID
}

export default {
  getURLforTicketGUID: getURLforTicketGUID
}
