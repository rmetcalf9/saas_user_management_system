<template>
  <q-page>
    <div>TENANT TODO {{ tenantData }}</div>
    <div>xx {{ ticketTypeData }}</div>
  </q-page>
</template>

<script>
import { useGlobalValsStore } from 'stores/globalValsStore'
import { Notify, Loading } from 'quasar'
import callbackHelper from '../callbackHelper'
import saasApiClientCallBackend from '../saasAPiClientCallBackend'
import { useUserManagementClientStoreStore } from 'stores/saasUserManagementClientStore'

function getEmptyTenantData () {
  return {
    AuthProviders: []
  }
}
function getEmptyTicketTypeData () {
  return {
    pagination: {
      total: 999
    },
    result: []
  }
}

export default {
  name: 'PageTenant',
  components: {
  },
  setup () {
    const globalValsStore = useGlobalValsStore()
    const userManagementClientStoreStore = useUserManagementClientStoreStore()
    return {
      globalValsStore,
      userManagementClientStoreStore
    }
  },
  data () {
    return {
      tenantData: getEmptyTenantData(),
      ticketTypeData: getEmptyTicketTypeData(),
      tableColumns: [
        { name: 'Type', required: true, label: 'Type', align: 'left', field: 'Type', sortable: true, filter: false },
        { name: 'AllowUserCreation', required: true, label: 'AllowUserCreation', align: 'left', field: 'AllowUserCreation', sortable: true, filter: false },
        { name: 'AllowLink', required: true, label: 'AllowLink', align: 'left', field: 'AllowLink', sortable: true, filter: false },
        { name: 'AllowUnlink', required: true, label: 'AllowUnlink', align: 'left', field: 'AllowUnlink', sortable: true, filter: false },
        { name: 'LinkText', required: true, label: 'LinkText', align: 'left', field: 'LinkText', sortable: true, filter: false },
        { name: 'MenuText', required: true, label: 'MenuText', align: 'left', field: 'MenuText', sortable: true, filter: false },
        { name: 'IconLink', required: true, label: 'IconLink', align: 'left', field: 'IconLink', sortable: true, filter: false },
        { name: '...', required: true, label: '', align: 'left', field: 'guid', sortable: false, filter: false }
        // guid not in table
        // ConfigJSON not in table
      ],
      editTenantModalDialogData: {
        Description: '',
        AllowUserCreation: false,
        JWTCollectionAllowedOriginList: [],
        TicketOverrideURL: ''
      },
      editTenantModalDialogVisible: false,
      editAuthProvModalDialogData: {
        AddMode: false,
        DeleteMode: false,
        Type: 'internal',
        AllowUserCreation: false,
        AllowLink: false,
        AllowUnlink: false,
        LinkText: '',
        MenuText: '',
        IconLink: '',
        guid: '',
        ConfigJSON: '',
        saltForPasswordHashing: '' // Can never be updated but existing value must always be provided for updates
      },
      editAuthProvModalDialogVisible: false
    }
  },
  methods: {
    refreshTenantData () {
      const jobNameToLoad = this.$route.params.selTenantNAME
      const TTT = this
      const callback = {
        ok: function (response) {
          TTT.tenantData = response.data
          TTT.refreshTicketTypeData()
        },
        error: function (error) {
          TTT.globalValsStore.pageTitle = 'Tenant ERROR'
          Loading.hide()
          Notify.create({ color: 'negative', message: 'Tenant query failed - ' + callbackHelper.getErrorFromResponse(error) })
          TTT.tenantData = getEmptyTenantData()
        }
      }
      TTT.globalValsStore.pageTitle = 'Tenant Loading'
      Loading.show()
      saasApiClientCallBackend.callApi({
        prefix: 'admin',
        router: this.$router,
        store: this.userManagementClientStoreStore,
        path: '/' + TTT.tenantName + '/tenants/' + jobNameToLoad,
        method: 'get',
        postdata: undefined,
        callback
      })
    },
    refreshTicketTypeData () {
      const TTT = this
      const callback = {
        ok: function (response) {
          TTT.globalValsStore.pageTitle = 'Tenant TODO'
          Loading.hide()
          TTT.ticketTypeData = response.data
        },
        error: function (error) {
          TTT.globalValsStore.pageTitle = 'Tenant ERROR'
          Loading.hide()
          Notify.create({ color: 'negative', message: 'Ticket Type query failed - ' + callbackHelper.getErrorFromResponse(error) })
          TTT.ticketTypeData = getEmptyTicketTypeData()
        }
      }
      TTT.globalValsStore.pageTitle = 'Tenant Loading'
      Loading.show()
      saasApiClientCallBackend.callApi({
        prefix: 'admin',
        router: this.$router,
        store: this.userManagementClientStoreStore,
        path: '/' + TTT.tenantName + '/tenants/' + this.$route.params.selTenantNAME + '/tickettypes?pagesize=5',
        method: 'get',
        postdata: undefined,
        callback
      })
    }
  },
  computed: {
    tenantName () {
      return this.$route.params.tenantName
    }
  },
  mounted () {
    this.refreshTenantData()
  }
}
</script>

<style>
</style>
