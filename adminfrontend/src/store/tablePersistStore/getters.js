/*
export function someGetter (state) {
}
*/
/*
function getDefaultTableSettings (defaultVisibleColumns) {
  return {
    visibleColumns: defaultVisibleColumns,
    serverPagination: {
      page: 1,
      rowsNumber: 10, // specifying this determines pagination is server-side
      rowsPerPage: 10,
      sortBy: null,
      descending: true
    },
    filter: ''
  }
}
*/
export function tableStttings (state) {
  return function (tableName, defaultVisibleColumns) {
    return state.ttt
    // console.log('Calling Getter', tableName)
    // if (typeof (state.tableSettingsValues[tableName]) === 'undefined') {
    //   state.tableSettingsValues[tableName] = getDefaultTableSettings(defaultVisibleColumns)
    // }
    // return getDefaultTableSettings(defaultVisibleColumns)
  }
}
