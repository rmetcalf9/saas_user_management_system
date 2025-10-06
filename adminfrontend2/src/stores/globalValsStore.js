import { defineStore, acceptHMRUpdate } from 'pinia'

export const useGlobalValsStore = defineStore('globalValsStore', {
  state: () => ({
    pageTitle: 'Adminfrontend Page Title'
  }),
  getters: {},
  actions: {}
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useGlobalValsStore, import.meta.hot))
}
