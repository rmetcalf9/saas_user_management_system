<template><div>
  <q-table
    title='Tenants'
    :rows-per-page-options="tableRowsPerPageOptions"
    :loading="tableLoading"
    :data="tableData"
    :columns="tableColumns"
    @request="request"
    row-key="Name"
    :visible-columns="tablePersistSettings.visibleColumns"
    :filter="tablePersistSettings.filter"
    :pagination.sync="tablePersistSettings.serverPagination"
  >
      <template slot="top-left" slot-scope="props">
        <q-btn
          color="primary"
          push
          @click="openCreateTenantModalDialog"
        >Add Tenant</q-btn>
      </template>
      <template slot="top-right" slot-scope="props">
        <selectColumns
          v-model="tablePersistSettings.visibleColumns"
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

      <q-td  slot="body-cell-Name" slot-scope="props" :props="props">
        <q-btn flat no-caps dense :label="props.value" @click="clickSingleTenantCallbackFN(props)" width="100%"/>
      </q-td>

      <q-td  slot="body-cell-JWTCollectionAllowedOriginList" slot-scope="props" :props="props">
        {{ props.value }}
      </q-td>

      <q-td slot="body-cell-..." slot-scope="props" :props="props">
        <q-btn flat color="primary" icon="keyboard_arrow_right" label="" @click="clickSingleTenantCallbackFN(props)" />
      </q-td>
  </q-table>
</div></template>

<script>
import { Notify } from 'quasar'
import restcallutils from '../restcallutils'
import callbackHelper from '../callbackHelper'
import selectColumns from '../components/selectColumns'

export default {
  // name: 'TenantsTable',
  props: [
    'defaultDisplayedColumns',
    'persistantSettingsSlot',
    'clickSingleTenantCallback'
  ],
  components: {
    selectColumns
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
      var TTT = this
      TTT.tableLoading = true
      var callback = {
        ok: function (response) {
          // console.log(response.data.guid)
          TTT.tableLoading = false
          // updating pagination to reflect in the UI
          TTT.tablePersistSettings.serverPagination = pagination
          // we also set (or update) rowsNumber
          TTT.tablePersistSettings.serverPagination.rowsNumber = response.data.pagination.total
          TTT.tablePersistSettings.serverPagination.filter = filter
          TTT.tablePersistSettings.serverPagination.rowsPerPage = response.data.pagination.pagesize
          // TODO ??? change when we have a store dataTableSettings.commit('JOBS', TTT.tablePersistSettings)
          // then we update the rows with the fetched ones
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
      var queryParams = []
      if (filter !== null) {
        if (filter !== '') {
          queryParams['query'] = filter
        }
      }
      if (pagination.rowsPerPage !== 0) {
        queryParams['pagesize'] = pagination.rowsPerPage.toString()
        queryParams['offset'] = (pagination.rowsPerPage * (pagination.page - 1)).toString()
      }
      if (pagination.sortBy !== null) {
        var postfix = ''
        if (pagination.descending) {
          postfix = ':desc'
        }
        queryParams['sort'] = pagination.sortBy + postfix
      }
      var queryString = restcallutils.buildQueryString('/tenants', queryParams)
      this.$store.dispatch('globalDataStore/callAdminAPI', {
        path: queryString,
        method: 'get',
        postdata: null,
        callback: callback,
        curPath: this.$router.history.current.path,
        headers: undefined
      })
    },
    openCreateTenantModalDialog () {
      var TTT = this
      var callback = {
        ok: function (response) {
          Notify.create({color: 'positive', message: 'Tenant created'})
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
        var postdata = {
          'Name': data,
          'Description': '',
          'AllowUserCreation': false
        }
        this.$store.dispatch('globalDataStore/callAdminAPI', {
          path: '/tenants',
          method: 'post',
          postdata: postdata,
          callback: callback,
          curPath: this.$router.history.current.path,
          headers: undefined
        })
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
    tablePersistSettings: {
      get () {
        return this.$store.getters['tablePersistStore/tableStttings'](this.persistantSettingsSlot, this.defaultDisplayedColumns)
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
