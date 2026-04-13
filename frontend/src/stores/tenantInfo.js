import { defineStore, acceptHMRUpdate } from 'pinia'
import saasAPiClientCallBackend from '../saasAPiClientCallBackend.js'
// import callbackHelper from '../callbackHelper'

export const useTenantInfoStore = defineStore('tenantInfoStore', {
  state: () => ({
    tenants: {},
    selectedAuth: {}
  }),
  getters: {
  },
  actions: {
    selectAuthProvider ({ selectedAuthProvider }) {
      this.selectedAuth = selectedAuthProvider
    },
    clearAuthProvider () {
      this.selectedAuth = {}
    },
    isAuthProviderSelected () {
      return Object.keys(this.selectedAuth).length > 0
    },
    getInfo ({ router, tenantName, skipcache }) {
      if (!skipcache) {
        if (typeof (this.tenants[tenantName]) !== 'undefined') {
          return this.tenants[tenantName]
        }
      }
      const TTT = this
      const callback = {
        ok: function (response) {
          TTT.tenants[tenantName] = {
            loading: false,
            errored: false,
            error: {},
            res: response.data
          }
        },
        error: function (response) {
          TTT.tenants[tenantName] = {
            loading: false,
            errored: true,
            error: response,
            res: {}
          }
          console.log('ERROR - failed to get tenant info')
        }
      }
      if (typeof (this.tenants[tenantName]) === 'undefined') {
        this.tenants[tenantName] = {
          loading: true,
          errored: false,
          error: {},
          res: {}
        }
      }
      saasAPiClientCallBackend.callApi({
        prefix: 'login',
        router,
        path: '/' + tenantName + '/authproviders',
        method: 'get',
        postdata: {},
        callback
      })

      return this.tenants[tenantName]
    }
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useTenantInfoStore, import.meta.hot))
}
