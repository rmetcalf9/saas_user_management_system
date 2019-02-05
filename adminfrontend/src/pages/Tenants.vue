<template>
<!-- https://github.com/rmetcalf9/dockJob/blob/master/webfrontend/src/pages/Jobs.vue -->
  <q-table
    title='Tenants'
    :rows-per-page-options="tableRowsPerPageOptions"
    :loading="tableLoading"
    :data="tableData"
    :columns="tableColumns"
    @request="request"
    row-key="name"
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
  </q-table>
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
        { name: 'Name', required: true, label: 'Tenant Name', align: 'left', field: 'Name', sortable: false, filter: false },
        { name: 'Description', required: true, label: 'Description', align: 'left', field: 'Description', sortable: false, filter: false },
        { name: 'AllowUserCreation', required: true, label: 'AllowUserCreation', align: 'left', field: 'AllowUserCreation', sortable: false, filter: false }
      ]
    }
  },
  methods: {
    request ({ pagination, filter }) {
      var TTT = this
      TTT.loading = true
      var callback = {
        ok: function (response) {
          // console.log(response.data.guid)
          TTT.loading = false
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
          TTT.loading = false
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
      var queryString = restcallutils.buildQueryString('/tenants', queryParams)
      this.$store.dispatch('globalDataStore/callAdminAPI', {
        path: queryString,
        method: 'get',
        postdata: null,
        callback: callback,
        curPath: this.$router.history.current.path
      })
    },
    openCreateTenantModalDialog () {
      var TTT = this
      var callback = {
        ok: function (response) {
          Notify.create({color: 'positive', detail: 'Tenant created'})
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
      }).then(data => {
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
          curPath: this.$router.history.current.path
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
