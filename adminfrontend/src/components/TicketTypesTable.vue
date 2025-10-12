<template><div>
  <q-table
    title='Ticket Types'
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
        @click="createNewTicketTypeButton"
      >Create new Ticket Type</q-btn>
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
      <q-tr :props="props" @click="clickSingleCallbackFN(props.row)">
        <q-td key="Name" :props="props">
          {{ props.row.ticketTypeName }}
        </q-td>
        <q-td key="Description" :props="props">
          {{ props.row.description }}
        </q-td>
        <q-td key="Enabled" :props="props">
          {{ props.row.enabled }}
        </q-td>
        <q-td key="AllowUserCreation" :props="props">
          {{ props.row.allowUserCreation }}
        </q-td>
        <q-td key="Issue Duration" :props="props">
          {{ props.row.issueDuration }}
        </q-td>
        <q-td key="Post Use URL" :props="props">
          {{ props.row.postUseURL }}
        </q-td>
        <q-td key="Post Use Invalid URL" :props="props">
          {{ props.row.postInvalidURL }}
        </q-td>
        <q-td key="WelcomeAgree" :props="props">
          {{ props.row.welcomeMessage.agreementRequired }}
        </q-td>
        <q-td key="WelcomeTitle" :props="props">
          {{ props.row.welcomeMessage.title }}
        </q-td>
        <q-td key="WelcomeBody" :props="props">
          {{ props.row.welcomeMessage.body }}
        </q-td>
        <q-td key="WelcomeOkText" :props="props">
          {{ props.row.welcomeMessage.okButtonText }}
        </q-td>
        <q-td key="..." :props="props">
          <q-btn flat color="primary" icon="keyboard_arrow_right" label="" />
        </q-td>
      </q-tr>
    </template>
    </q-table>
  <editTicketTypeModal
    ref="editTicketTypeModal"
    @ok="clickEditTicketTypeModalModalOK"
  />
</div></template>

<script>
import { Notify, Loading } from 'quasar'
import callbackHelper from '../callbackHelper'
import restcallutils from '../restcallutils'
import saasApiClientCallBackend from '../saasAPiClientCallBackend'
import SelectColumns from '../components/SelectColumns'
import { useTablePersistSettingsStore } from 'stores/tablePersistSettingsStore'
import { useUserManagementClientStoreStore } from 'stores/saasUserManagementClientStore'
import editTicketTypeModal from './Modals/editTicketTypeModal.vue'

export default {
  name: 'TicketTypesTableComponent',
  props: [
    'defaultDisplayedColumns',
    'persistantSettingsSlot',
    'selectedTenantName'
  ],
  components: {
    SelectColumns,
    editTicketTypeModal
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
        { name: 'Name', required: true, label: 'Ticket Type Name', align: 'left', field: 'ticketTypeName', sortable: false, filter: false },
        { name: 'Description', required: false, label: 'Description', align: 'left', field: 'description', sortable: false, filter: false },
        { name: 'Enabled', required: false, label: 'Enabled', align: 'left', field: 'enabled', sortable: false, filter: false },
        { name: 'AllowUserCreation', required: false, label: 'AllowUserCreation', align: 'left', field: 'allowUserCreation', sortable: false, filter: false },
        { name: 'Issue Duration', required: false, label: 'Issue Duration', align: 'left', field: 'issueDuration', sortable: false, filter: false },
        { name: 'Post Use URL', required: false, label: 'Post Use URL', align: 'left', field: 'postUseURL', sortable: false, filter: false },
        { name: 'Post Use Invalid URL', required: false, label: 'Post Use Invalid URL', align: 'left', field: 'postInvalidURL', sortable: false, filter: false },
        { name: 'WelcomeAgree', required: false, label: 'Welcome Agreement', align: 'left', field: 'welcomeMessage.agreementRequired', sortable: false, filter: false },
        { name: 'WelcomeTitle', required: false, label: 'Welcome Title', align: 'left', field: 'welcomeMessage.title', sortable: false, filter: false },
        { name: 'WelcomeBody', required: false, label: 'Welcome Body', align: 'left', field: 'welcomeMessage.body', sortable: false, filter: false },
        { name: 'WelcomeOkText', required: false, label: 'Welcome Ok Text', align: 'left', field: 'welcomeMessage.okButtonText', sortable: false, filter: false },
        { name: '...', required: true, label: '', align: 'left', field: 'guid', sortable: false, filter: false }
      ]
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
    clickSingleCallbackFN (row) {
      this.$router.push('/' + this.tenantName + '/tenants/' + this.selectedTenantName + '/tickettypes/' + row.id)
    },
    createNewTicketTypeButton () {
      this.$refs.editTicketTypeModal.launchDialog({
        title: 'Create new ticket type for ' + this.selectedTenantName,
        callerData: { editing: false },
        editingExisting: false
      })
    },
    clickEditTicketTypeModalModalOK (callerData, objData) {
      const TTT = this
      if (callerData.editing) {
        console.log('EDITING NOT DONE')
        // objData.id = TODO
        return
      }
      // Common to edit and add - we need to call upsert
      objData.tenantName = TTT.selectedTenantName

      const callback = {
        ok: function (response) {
          Loading.hide()
          Notify.create({ color: 'positive', message: 'Ticket Type created' })
          setTimeout(function () {
            TTT.refresh()
          }, 400)
        },
        error: function (error) {
          Loading.hide()
          Notify.create({ color: 'negative', message: 'Request failed - ' + callbackHelper.getErrorFromResponse(error) })
        }
      }
      Loading.show()
      saasApiClientCallBackend.callApi({
        prefix: 'admin',
        router: this.$router,
        store: this.userManagementClientStoreStore,
        path: '/' + TTT.tenantName + '/tenants/' + TTT.selectedTenantName + '/tickettypes',
        method: 'post',
        postdata: objData,
        callback
      })
    },
    refresh () {
      this.request({
        pagination: this.tablePersistSettings.serverPagination,
        filter: this.tablePersistSettings.filter
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
      const queryString = restcallutils.buildQueryString('/' + TTT.tenantName + '/tenants/' + TTT.selectedTenantName + '/tickettypes', queryParams)
      saasApiClientCallBackend.callApi({
        prefix: 'admin',
        router: this.$router,
        store: this.userManagementClientStoreStore,
        path: queryString,
        method: 'get',
        postdata: undefined,
        callback
      })
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
