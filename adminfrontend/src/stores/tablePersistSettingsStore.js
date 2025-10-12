import { defineStore, acceptHMRUpdate } from 'pinia'

export const useTablePersistSettingsStore = defineStore('tablePersistSettingsStore', {
  state: () => ({
    tableSettingsValues: {}
  }),
  getters: {},
  actions: {
    getTableSettings (tableName, defaultVisibleColumns) {
      if (!Object.hasOwn(this.tableSettingsValues, tableName)) {
        this.tableSettingsValues[tableName] = {
          visibleColumns: defaultVisibleColumns,
          serverPagination: {
            page: 1,
            rowsNumber: 10,
            rowsPerPage: 10,
            sortBy: null,
            descending: true
          },
          filter: ''
        }
      }
      return this.tableSettingsValues[tableName]
    },
    resetTableSettings (tableName) {
      if (!Object.hasOwn(this.tableSettingsValues, tableName)) {
        return
      }
      this.tableSettingsValues[tableName].visibleColumns = []
      this.tableSettingsValues[tableName].serverPagination.page = 1
      this.tableSettingsValues[tableName].serverPagination.rowsNumber = 10
      this.tableSettingsValues[tableName].serverPagination.rowsPerPage = 10
      this.tableSettingsValues[tableName].serverPagination.sortBy = null
      this.tableSettingsValues[tableName].serverPagination.descending = true
      this.tableSettingsValues[tableName].filter = ''
    }
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useTablePersistSettingsStore, import.meta.hot))
}
