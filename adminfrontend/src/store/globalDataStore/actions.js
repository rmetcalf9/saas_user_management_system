// Adminfrontend GlobalStore Actions
/*
export function someAction (context) {
}
*/

/*
Called only once
*/
export const readServerInfo = ({ dispatch, commit, state }, params) => {
  if (state.urlToReachAPI === null) {
    console.log('WARNING - trying to read server info when it is already read')
    return
  }
  console.log('TODO')
}
