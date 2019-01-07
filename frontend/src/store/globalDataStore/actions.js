/*
export function someAction (context) {
}
*/

import callbackHelper from '../../callbackHelper'

export const checkAuthProviders = ({ dispatch }, callback) => {
  callbackHelper.callbackWithSimpleError(callback.callback, 'Bad Tenant')
  // state.drawerState = opened
}
