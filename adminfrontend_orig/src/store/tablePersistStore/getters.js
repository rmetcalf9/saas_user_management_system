/*
export function someGetter (state) {
}
*/

export function tableStttings (state) {
  return function (tableName, defaultVisibleColumns) {
    var freeSlot = -1
    var curSlot = 0
    while (freeSlot === -1) {
      if (state.tableSettingsLink[curSlot] === tableName) {
        return state.tableSettingsValues[curSlot]
      }
      if (state.tableSettingsLink[curSlot] === '_') {
        freeSlot = curSlot
      }
      curSlot++
      // We will get an error if we try and use more than 10 slots
    }
    // no data found for this table name but slot is found
    state.tableSettingsLink[freeSlot] = tableName
    state.tableSettingsValues[freeSlot].visibleColumns = defaultVisibleColumns
    state.tableSettingsValues[freeSlot].serverPagination.page = 1
    state.tableSettingsValues[freeSlot].serverPagination.rowsNumber = 10
    state.tableSettingsValues[freeSlot].serverPagination.rowsPerPage = 10
    state.tableSettingsValues[freeSlot].serverPagination.sortBy = null
    state.tableSettingsValues[freeSlot].serverPagination.descending = true
    state.tableSettingsValues[freeSlot].filter = ''
    return state.tableSettingsValues[freeSlot]
  }
}
