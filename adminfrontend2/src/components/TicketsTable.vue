<template><div>
  <q-table
    title='Tickets'
    :rows-per-page-options="tableRowsPerPageOptions"
    :loading="tableLoading"
    :rows="tableData"
    :columns="tableColumns"
    @request="request"
    row-key="id"
    :visible-columns="tablePersistSettings.visibleColumns"
    :filter="tablePersistSettings.filter"
    :pagination="tablePersistSettings.serverPagination"
    selection="multiple"
    v-model:selected="tableSelected"
  >
    <template v-slot:top-selection>
      <q-btn color="negative" @click="disableSelectedTickets">Disable Selected Tickets</q-btn>
    </template>

    <template v-slot:top-left>
      <q-btn
        color="primary"
        push
        @click="createBatchButton"
      >Create Batch of Tickets</q-btn>
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

    <template v-slot:body-cell-url="props">
      <a :href="getURLforTicketGUID(props.row.id)">{{ getURLforTicketGUID(props.row.id) }}</a>
    </template>
    <!--
      <q-td  slot="body-cell-creationDateTime" slot-scope="props" :props="props">
        {{ metadata.creationDateTime }}
      </q-td>
      <q-td  slot="body-cell-url" slot-scope="props" :props="props">
        <a :href="getURLforTicketGUID(props.row.id)">{{ getURLforTicketGUID(props.row.id) }}</a>
      </q-td>
      -->
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
import restcallutils from '../restcallutils'
import callbackHelper from '../callbackHelper'
import adminfrontendfns from '../adminfrontendfns.js'
import saasApiClientCallBackend from '../saasAPiClientCallBackend'

import SelectColumns from '../components/SelectColumns'
import { useTablePersistSettingsStore } from 'stores/tablePersistSettingsStore'
import { useUserManagementClientStoreStore } from 'stores/saasUserManagementClientStore'
import ticketCreateBatchStartModal from './Modals/ticketCreateBatchStartModal.vue'
import ticketCreateBatchResultsModal from './Modals/ticketCreateBatchResultsModal.vue'

export default {
  name: 'TicketsTable',
  props: [
    'defaultDisplayedColumns',
    'persistantSettingsSlot',
    'selectedTenantName',
    'selectedTicketTypeID',
    'ticketTypeData',
    'tenantData'
  ],
  components: {
    SelectColumns,
    ticketCreateBatchStartModal,
    ticketCreateBatchResultsModal
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
        { name: 'foreignKey', required: false, label: 'Foreign Key', align: 'left', field: 'foreignKey', sortable: false, filter: false },
        { name: 'id', required: true, label: 'ID', align: 'left', field: 'id', sortable: false, filter: false },
        { name: 'usableState', required: true, label: 'Usable State', align: 'left', field: 'usableState', sortable: false, filter: false },
        { name: 'expiry', required: false, label: 'expiry', align: 'left', field: 'expiry', sortable: false, filter: false },
        { name: 'usedDate', required: false, label: 'usedDate', align: 'left', field: 'usedDate', sortable: false, filter: false },
        { name: 'useWithUserID', required: false, label: 'useWithUserID', align: 'left', field: 'useWithUserID', sortable: false, filter: false },
        { name: 'reissueRequestedDate', required: false, label: 'reissueRequestedDate', align: 'left', field: 'reissueRequestedDate', sortable: false, filter: false },
        { name: 'reissuedTicketID', required: false, label: 'reissuedTicketID', align: 'left', field: 'reissuedTicketID', sortable: false, filter: false },
        { name: 'disabled', required: false, label: 'disabled', align: 'left', field: 'disabled', sortable: false, filter: false },
        { name: 'creationDateTime', required: false, label: 'Creation Date', align: 'left', field: 'metadata.creationDateTime', sortable: false, filter: false },
        { name: 'url', required: false, label: 'URL', align: 'left', field: 'id', sortable: false, filter: false }
      ],
      tableSelected: []
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
  methods: {
    disableSelectedTickets () {
      const TTT = this
      const callback = {
        ok: function (response) {
          Notify.create({ color: 'positive', message: 'Disable Ticket Sucessful' })
          TTT.refresh()
        },
        error: function (error) {
          Notify.create({ color: 'negative', message: 'Disable Ticket(s) failed - ' + callbackHelper.getErrorFromResponse(error) })
        }
      }
      const arr = this.tableSelected.map(function (ite) {
        return {
          ticketGUID: ite.id,
          objectVersion: ite.metadata.objectVersion
        }
      })
      const postData = {
        tickets: arr
      }
      saasApiClientCallBackend.callApi({
        prefix: 'admin',
        router: this.$router,
        store: this.userManagementClientStoreStore,
        path: '/' + TTT.tenantName + '/tenants/' + this.selectedTenantName + '/tickettypes/' + this.ticketTypeData.id + '/tickets/disablebatch',
        method: 'post',
        postdata: postData,
        callback
      })
    },
    getURLforTicketGUID (ticketGUID) {
      return adminfrontendfns.getURLforTicketGUID(this.userManagementClientStoreStore, ticketGUID, this.selectedTenantName, this.ticketTypeData, this.tenantData)
    },
    createBatchButton () {
      this.$refs.ticketCreateBatchStartModal.launchDialog({
        ticketTypeData: this.ticketTypeData,
        callerData: { }
      })
    },
    clickTicketCreateBatchStartModalOK ({ callerData, keymap, foreignKeyDupAction }) {
      const TTT = this
      const callback = {
        ok: function (response) {
          TTT.$refs.ticketCreateBatchResultsModal.launchDialog({
            ticketTypeData: TTT.ticketTypeData,
            callerData: { },
            createBatchResult: response,
            tenantData: TTT.tenantData
          })
          TTT.refresh()
        },
        error: function (error) {
          Notify.create({ color: 'negative', message: 'Delete Ticket Type failed - ' + callbackHelper.getErrorFromResponse(error) })
        }
      }
      const postData = {
        foreignKeyDupAction,
        foreignKeyList: keymap
      }
      saasApiClientCallBackend.callApi({
        prefix: 'admin',
        router: this.$router,
        store: this.userManagementClientStoreStore,
        path: '/' + TTT.tenantName + '/tenants/' + this.selectedTenantName + '/tickettypes/' + this.ticketTypeData.id + '/createbatch',
        method: 'post',
        postdata: postData,
        callback
      })
    },
    request ({ pagination, filter }) {
      const TTT = this
      TTT.tableLoading = true
      const callback = {
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
      const queryString = restcallutils.buildQueryString('/' + TTT.tenantName + '/tenants/' + TTT.selectedTenantName + '/tickettypes/' + TTT.selectedTicketTypeID + '/tickets', queryParams)
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
    refresh () {
      this.request({
        pagination: this.tablePersistSettings.serverPagination,
        filter: this.tablePersistSettings.filter
      })
    }
  },
  mounted () {
    this.refresh()
  }
}
</script>

<style>
</style>
