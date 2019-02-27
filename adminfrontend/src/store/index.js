import Vue from 'vue'
import Vuex from 'vuex'

import globalDataStore from './globalDataStore'
import tablePersistStore from './tablePersistStore'

Vue.use(Vuex)

/*
 * If not building with SSR mode, you can
 * directly export the Store instantiation
 */

export default function (/* { ssrContext } */) {
  const Store = new Vuex.Store({
    modules: {
      globalDataStore,
      tablePersistStore
    }
  })

  return Store
}
