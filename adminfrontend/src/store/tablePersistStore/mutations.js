// Adminfrontend GlobalStore
/*
export function someMutation (state) {
}
*/

export function resetTableSettings (state, tableName) {
  for (var slot in state.tableSettingsLink) {
    if (state.tableSettingsLink[slot] === tableName) {
      state.tableSettingsLink[slot] = '_'
      state.tableSettingsValues[slot].visibleColumns = []
      state.tableSettingsValues[slot].serverPagination.page = 1
      state.tableSettingsValues[slot].serverPagination.rowsNumber = 10
      state.tableSettingsValues[slot].serverPagination.rowsPerPage = 10
      state.tableSettingsValues[slot].serverPagination.sortBy = null
      state.tableSettingsValues[slot].serverPagination.descending = true
      state.tableSettingsValues[slot].filter = ''
      return
    }
  }
}
