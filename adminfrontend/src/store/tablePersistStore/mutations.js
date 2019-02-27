// Adminfrontend GlobalStore
/*
export function someMutation (state) {
}
*/

export function updateTableSettings (state, val) {
  console.log('Calling mutation updateTableSettings ', val)
  state.tableSettingsValues[val.tableName] = val.val
}
