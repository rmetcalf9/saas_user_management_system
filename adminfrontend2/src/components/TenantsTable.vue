<template><div>
  <q-table
    title='Tenants'
    :rows-per-page-options="tableRowsPerPageOptions"
    :loading="tableLoading"
    :rows="tableData"
    :columns="tableColumns"
    @request="request"
    row-key="Name"
    :visible-columns="tablePersistSettings.visibleColumns"
    :filter="tablePersistSettings.filter"
    :pagination="tablePersistSettings.serverPagination"
  >
      <template v-slot:top-left>
        <q-btn
          color="primary"
          push
          @click="openCreateTenantModalDialog"
        >Add Tenant</q-btn>
      </template>
      <template v-slot:top-right>
        <SelectColumns
          :selected_col_names="tablePersistSettings_visiblecols"
          @update:selected_col_names="(newVal) => tablePersistSettings_visiblecols = newVal"
          :columns="tableColumns"
        />
        &nbsp;
        <q-input
          v-model="tablePersistSettings.filter"
          debounce="500"
          clearable
          placeholder="Search" outlined
        >
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
      </template>
      <template v-slot:body="props">
        <q-tr :props="props" @click="clickSingleTenantCallbackFN(props.row)">
          <q-td key="Name" :props="props">
            {{ props.row.Name }}
          </q-td>
          <q-td key="Description" :props="props">
            {{ props.row.Description }}
          </q-td>
          <q-td key="AllowUserCreation" :props="props">
            {{ props.row.AllowUserCreation }}
          </q-td>
          <q-td key="JWTCollectionAllowedOriginList" :props="props">
            {{ props.row.JWTCollectionAllowedOriginList }}
          </q-td>
          <q-td key="..." :props="props">
            <q-btn flat color="primary" icon="keyboard_arrow_right" label="" />
          </q-td>
        </q-tr>
      </template>
  </q-table>
</div></template>

<script>
import { Notify } from 'quasar'
import restcallutils from '../restcallutils'
import callbackHelper from '../callbackHelper'
import SelectColumns from '../components/SelectColumns'
import saasApiClientCallBackend from '../saasAPiClientCallBackend'
import { useTablePersistSettingsStore } from 'stores/tablePersistSettingsStore'
import { useUserManagementClientStoreStore } from 'stores/saasUserManagementClientStore'

export default {
  // name: 'TenantsTable',
  props: [
    'defaultDisplayedColumns',
    'persistantSettingsSlot',
    'clickSingleTenantCallback'
  ],
  components: {
    SelectColumns
  },
  setup () {
    const tablePersistSettingsStore = useTablePersistSettingsStore()
    const userManagementClientStoreStore = useUserManagementClientStoreStore()
    return {
      tablePersistSettingsStore,
      userManagementClientStoreStore
    }
  },
  data () {
    return {
      tableRowsPerPageOptions: [5, 10, 25, 50, 100, 200],
      tableLoading: false,
      tableData: [],
      tableColumns: [
        { name: 'Name', required: true, label: 'Tenant Name', align: 'left', field: 'Name', sortable: false, filter: false },
        { name: 'Description', required: false, label: 'Description', align: 'left', field: 'Description', sortable: false, filter: false },
        { name: 'AllowUserCreation', required: false, label: 'AllowUserCreation', align: 'left', field: 'AllowUserCreation', sortable: false, filter: false },
        { name: 'JWTCollectionAllowedOriginList', required: false, label: 'Allowed Origin List', align: 'left', field: 'JWTCollectionAllowedOriginList', sortable: false, filter: false },
        { name: '...', required: true, label: '', align: 'left', field: 'guid', sortable: false, filter: false }
      ]
    }
  },
  methods: {
    clickSingleTenantCallbackFN (props) {
      if (typeof (this.clickSingleTenantCallback) !== 'undefined') {
        this.clickSingleTenantCallback(props)
      }
    },
    request ({ pagination, filter }) {
      const TTT = this
      TTT.tableLoading = true
      const callback = {
        ok: function (response) {
          // console.log(response.data.guid)
          TTT.tableLoading = false
          TTT.tablePersistSettings.serverPagination = pagination
          TTT.tablePersistSettings.serverPagination.rowsNumber = response.data.pagination.total
          TTT.tablePersistSettings.serverPagination.filter = filter
          TTT.tablePersistSettings.serverPagination.rowsPerPage = response.data.pagination.pagesize
          TTT.tableData = response.data.result
        },
        error: function (error) {
          TTT.tableLoading = false
          Notify.create('Job query failed - ' + callbackHelper.getErrorFromResponse(error))
        }
      }
      if (pagination.page === 0) {
        pagination.page = 1
      }
      const queryParams = []
      if (filter !== null) {
        if (filter !== '') {
          queryParams.query = filter
        }
      }
      if (pagination.rowsPerPage !== 0) {
        queryParams.pagesize = pagination.rowsPerPage.toString()
        queryParams.offset = (pagination.rowsPerPage * (pagination.page - 1)).toString()
      }
      if (pagination.sortBy !== null) {
        let postfix = ''
        if (pagination.descending) {
          postfix = ':desc'
        }
        queryParams.sort = pagination.sortBy + postfix
      }
      const queryString = restcallutils.buildQueryString('/' + TTT.tenantName + '/tenants', queryParams)
      saasApiClientCallBackend.callApi({
        prefix: 'admin',
        router: this.$router,
        store: this.userManagementClientStoreStore,
        path: queryString,
        method: 'get',
        postdata: undefined,
        callback
      })
    },
    openCreateTenantModalDialog () {
      const TTT = this
      const callback = {
        ok: function (response) {
          Notify.create({ color: 'positive', message: 'Tenant created' })
          setTimeout(function () {
            TTT.refresh()
          }, 400)
        },
        error: function (error) {
          Notify.create('Request failed - ' + callbackHelper.getErrorFromResponse(error))
        }
      }
      this.$q.dialog({
        title: 'Create new Tenant',
        message: 'Name for Tenant',
        prompt: {
          model: '',
          type: 'text' // optional
        },
        cancel: true,
        color: 'secondary'
      }).onOk(data => {
        if (!data || !data.trim()) {
          // Show an alert or error, and prevent the dialog from closing
          this.$q.notify({
            type: 'negative',
            message: 'Tenant name cannot be empty!'
          })
          // Re-open the dialog
          this.openCreateTenantModalDialog() // assuming you wrap this in a function
        } else {
          const postdata = {
            Name: data,
            Description: '',
            AllowUserCreation: false
          }
          console.log('TODO', callback, postdata)
          saasApiClientCallBackend.callApi({
            prefix: 'admin',
            router: this.$router,
            store: this.userManagementClientStoreStore,
            path: '/' + TTT.tenantName + '/tenants',
            method: 'post',
            postdata,
            callback
          })
        }
      })
    },
    refresh () {
      this.request({
        pagination: this.tablePersistSettings.serverPagination,
        filter: this.tablePersistSettings.filter
      })
    }
  },
  computed: {
    tenantName () {
      return this.$route.params.tenantName
    },
    tablePersistSettings: {
      get () {
        return this.tablePersistSettingsStore.getTableSettings(
          this.persistantSettingsSlot,
          this.defaultDisplayedColumns
        )
      }
    },
    tablePersistSettings_visiblecols: {
      get () {
        return this.tablePersistSettings.visibleColumns
      },
      set (val) {
        this.tablePersistSettings.visibleColumns = val
      }
    }
  },
  mounted () {
    // once mounted, we need to trigger the initial server data fetch
    this.refresh()
  }
}
</script>

<style>
</style>
