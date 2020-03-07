<template><div>
  <q-table
    title='Tickets'
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
        @click="createBatchButton"
      >Create Batch</q-btn>
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
      <q-td  slot="body-cell-creationDateTime" slot-scope="props" :props="props">
        {{ metadata.creationDateTime }}
      </q-td>
  </q-table>
  <ticketCreateBatchStartModal
    ref="ticketCreateBatchStartModal"
    @ok="clickTicketCreateBatchStartModalOK"
  />
  <ticketCreateBatchResultsModal
    ref="ticketCreateBatchResultsModal"
  />
</div></template>

<script>
import { Notify } from 'quasar'
// import { Notify, Loading } from 'quasar'
import restcallutils from '../restcallutils'
import callbackHelper from '../callbackHelper'
import selectColumns from '../components/selectColumns'

import ticketCreateBatchStartModal from './Modals/ticketCreateBatchStartModal.vue'
import ticketCreateBatchResultsModal from './Modals/ticketCreateBatchResultsModal.vue'

export default {
  name: 'TicketTypesTable',
  props: [
    'defaultDisplayedColumns',
    'persistantSettingsSlot',
    'selectedTenantName',
    'selectedTicketTypeID',
    'ticketTypeData'
  ],
  components: {
    selectColumns,
    ticketCreateBatchStartModal,
    ticketCreateBatchResultsModal
  },
  data () {
    return {
      tableRowsPerPageOptions: [5, 10, 25, 50, 100, 200],
      tableLoading: false,
      tableData: [],
      tableColumns: [
        { name: 'foreignKey', required: false, label: 'Foreign Key', align: 'left', field: 'foreignKey', sortable: false, filter: false },
        { name: 'id', required: true, label: 'ID', align: 'left', field: 'id', sortable: false, filter: false },
        { name: 'usableState', required: true, label: 'Usable State', align: 'left', field: 'usableState', sortable: false, filter: false },
        { name: 'expiry', required: false, label: 'expiry', align: 'left', field: 'expiry', sortable: false, filter: false },
        { name: 'usedDate', required: false, label: 'usedDate', align: 'left', field: 'usedDate', sortable: false, filter: false },
        { name: 'useWithUserID', required: false, label: 'useWithUserID', align: 'left', field: 'useWithUserID', sortable: false, filter: false },
        { name: 'reissueRequestedDate', required: false, label: 'reissueRequestedDate', align: 'left', field: 'reissueRequestedDate', sortable: false, filter: false },
        { name: 'reissuedTicketID', required: false, label: 'reissuedTicketID', align: 'left', field: 'reissuedTicketID', sortable: false, filter: false },
        { name: 'disabled', required: false, label: 'disabled', align: 'left', field: 'disabled', sortable: false, filter: false },
        { name: 'creationDateTime', required: false, label: 'Creation Date', align: 'left', field: 'metadata.creationDateTime', sortable: false, filter: false }
      ]
    }
  },
  methods: {
    createBatchButton () {
      this.$refs.ticketCreateBatchStartModal.launchDialog({
        ticketTypeData: this.ticketTypeData,
        callerData: { }
      })
    },
    clickTicketCreateBatchStartModalOK ({ callerData, keymap, foreignKeyDupAction }) {
      var TTT = this
      var callback = {
        ok: function (response) {
          TTT.$refs.ticketCreateBatchResultsModal.launchDialog({
            ticketTypeData: TTT.ticketTypeData,
            callerData: { },
            createBatchResult: response
          })
          TTT.refresh()
        },
        error: function (error) {
          Notify.create({color: 'negative', message: 'Delete Ticket Type failed - ' + callbackHelper.getErrorFromResponse(error)})
        }
      }
      var postData = {
        'foreignKeyDupAction': foreignKeyDupAction,
        'foreignKeyList': keymap
      }
      TTT.$store.dispatch('globalDataStore/callAdminAPI', {
        path: '/tenants/' + this.selectedTenantName + '/tickettypes/' + this.ticketTypeData.id + '/createbatch',
        method: 'post',
        postdata: postData,
        callback: callback,
        curPath: TTT.$router.history.current.path,
        headers: {}
      })
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
      var queryString = restcallutils.buildQueryString('/tenants/' + TTT.selectedTenantName + '/tickettypes/' + TTT.selectedTicketTypeID + '/tickets', queryParams)
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
