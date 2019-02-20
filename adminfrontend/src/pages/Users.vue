<template>
  <q-page>
  <q-table
    title='Users'
    :rows-per-page-options="tableRowsPerPageOptions"
    :loading="tableLoading"
    :data="tableData"
    :columns="tableColumns"
    @request="request"
    row-key="UserID"
    :visible-columns="tablePersistSettings.visibleColumns"
    :filter="tablePersistSettings.filter"
    :pagination.sync="tablePersistSettings.serverPagination"
  >
      <template slot="top-left" slot-scope="props">
        <q-btn
          color="primary"
          push
          @click="createUserButtonClick"
        >Create User</q-btn>
      </template>

      <q-td  slot="body-cell-Name" slot-scope="props" :props="props">
        <q-btn flat no-caps dense :label="props.value" @click="$router.push('/' + $route.params.tenantName + '/users/' + props.row.Name)" width="100%"/>
      </q-td>

      <q-td slot="body-cell-..." slot-scope="props" :props="props">
        <q-btn flat color="primary" icon="keyboard_arrow_right" label="" @click="$router.push('/' + $route.params.tenantName + '/users/' + props.row.Name)" />
      </q-td>
  </q-table>{{ tableData }}
  </q-page>
</template>

<style>
</style>

<script>
import { Notify } from 'quasar'
import restcallutils from '../restcallutils'
import callbackHelper from '../callbackHelper'

export default {
  name: 'PageIndex',
  data () {
    return {
      tableRowsPerPageOptions: [5, 10, 25, 50, 100, 200],
      tableLoading: false,
      tableData: [],
      tableColumns: [
        { name: 'known_as', required: true, label: 'Known As', align: 'left', field: 'known_as', sortable: false, filter: false },
        { name: 'TenantRoles', required: true, label: 'TenantRoles', align: 'left', field: 'TenantRoles', sortable: false, filter: false },
        { name: 'Other Data', required: true, label: 'other_data', align: 'left', field: 'other_data', sortable: false, filter: false },
        { name: '...', required: true, label: '', align: 'left', field: 'guid', sortable: false, filter: false }
      ]
    }
  },
  methods: {
    createUserButtonClick () {
      console.log('TODO')
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
      if (filter !== '') {
        queryParams['query'] = filter
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
      var queryString = restcallutils.buildQueryString('/users', queryParams)
      this.$store.dispatch('globalDataStore/callAdminAPI', {
        path: queryString,
        method: 'get',
        postdata: null,
        callback: callback,
        curPath: this.$router.history.current.path,
        headers: undefined
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
    tablePersistSettings () {
      // TODO Arrange this to go into a Store somewhere
      return {
        visibleColumns: ['Name', 'Description'],
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
  },
  mounted () {
    // once mounted, we need to trigger the initial server data fetch
    this.refresh()
  }
}
</script>
