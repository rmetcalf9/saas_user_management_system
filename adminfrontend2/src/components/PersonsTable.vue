<template><div>
<q-table
  title='Persons'
  :rows-per-page-options="tableRowsPerPageOptions"
  :loading="tableLoading"
  :rows="tableData"
  :columns="tableColumns"
  @request="request"
  row-key="guid"
  :visible-columns="tablePersistSettings.visibleColumns"
  :filter="tablePersistSettings.filter"
  :pagination="tablePersistSettings.serverPagination"
  selection="multiple"
  v-model:selected="tableSelected"
>
  <template v-slot:top-selection>
    <q-btn flat round negative delete icon="delete" @click="deleteSelectedPersons" />
  </template>

  <template v-slot:top-left>
    <q-btn
      color="primary"
      push
      @click="createPersonButtonClick"
    >Create Person</q-btn>&nbsp;
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
    <q-tr :props="props" @click="$router.push('/' + $route.params.tenantName + '/persons/' + props.row.guid)">
      <q-td auto-width>
        <q-checkbox
          :model-value="props.selected"
          @update:model-value="val => toggleRowSelection(props.row, val)"
          @click.stop
        />
      </q-td>
      <q-td key="guid" :props="props">
        {{ props.row.guid }}
      </q-td>
      <q-td key="creationDateTime" :props="props">
        {{ props.row.creationDateTime }}
      </q-td>
      <q-td key="lastUpdateDateTime" :props="props">
        {{ props.row.lastUpdateDateTime }}
      </q-td>
      <q-td key="..." :props="props">
        <q-btn flat color="primary" icon="keyboard_arrow_right" label="" @click="$router.push('/' + $route.params.tenantName + '/persons/' + props.row.guid)" />
      </q-td>
    </q-tr>
  </template>
</q-table>

  <q-dialog v-model="createPersonModalDialogVisible">
    <q-layout view="Lhh lpR fff" container class="bg-white" style="height: 250px; width: 700px; max-width: 80vw;">
      <q-header class="bg-primary">
        <q-toolbar>
          <q-toolbar-title>
            Create new person
          </q-toolbar-title>
          <q-btn flat v-close-popup round dense icon="close" />
        </q-toolbar>
      </q-header>

      <q-page-container>
        <q-page padding>
          <q-input v-model="createPersonModalDialogData.guid" ref="personIDInput" label="Unknown" :label-width="3"/> No Editable Person Data
          <div>&nbsp;</div>
          <q-btn
            @click="okCreatePersonDialog"
            color="primary"
            label="Ok"
            class = "float-right q-ml-xs"
          />
          <q-btn
            @click="createPersonModalDialogVisible = false"
            label="Cancel"
            class = "float-right"
          />
        </q-page>
      </q-page-container>

    </q-layout>
  </q-dialog>
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
  name: 'UsersTable',
  props: [
    'defaultDisplayedColumns',
    'persistantSettingsSlot',
    'clickSingleUserCallback'
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
        { name: 'guid', required: true, label: 'guid', align: 'left', field: 'guid', sortable: false, filter: false },
        { name: 'creationDateTime', required: false, label: 'creationDateTime', align: 'left', field: 'creationDateTime', sortable: false, filter: false },
        { name: 'lastUpdateDateTime', required: false, label: 'lastUpdateDateTime', align: 'left', field: 'lastUpdateDateTime', sortable: false, filter: false },
        { name: '...', required: true, label: '', align: 'left', field: 'guid', sortable: false, filter: false }
      ],
      tableSelected: [],
      futureRefreshRequested: false,
      createPersonModalDialogVisible: false,
      createPersonModalDialogData: {
        guid: ''
      }
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
    toggleRowSelection (row, val) {
      if (val) {
        this.tableSelected.push(row)
        return
      }
      this.tableSelected = this.tableSelected.filter(function (x) {
        return x.guid !== row.guid
      })
    },
    deleteSelectedPersons () {
      console.log('TODO deleteSelectedPersons')
    },
    createPersonButtonClick () {
      this.createPersonModalDialogData.guid = ''
      this.createPersonModalDialogVisible = true
    },
    okCreatePersonDialog () {
      const TTT = this
      const jsonToSend = {
        // 'guid': this.createPersonModalDialogData.guid NO data can be sent
      }
      const callback = {
        ok: function (response) {
          TTT.createPersonModalDialogVisible = false
          Notify.create({ color: 'positive', message: 'Person Created' })
          // Filter for this created person
          TTT.tablePersistSettings.filter = response.data.guid
          TTT.refresh()
        },
        error: function (error) {
          Notify.create('Create Person failed - ' + callbackHelper.getErrorFromResponse(error))
        }
      }
      saasApiClientCallBackend.callApi({
        prefix: 'admin',
        router: this.$router,
        store: this.userManagementClientStoreStore,
        path: '/' + TTT.tenantName + '/persons',
        method: 'post',
        postdata: jsonToSend,
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
          TTT.tableData = response.data.result
          // console.log('response.data.result:', response.data.result)
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
      const queryString = restcallutils.buildQueryString('/' + TTT.tenantName + '/persons', queryParams)
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
    futureRefresh () {
      if (this.futureRefreshRequested) {
        return
      }
      this.futureRefreshRequested = true
      setTimeout(this.futureRefreshDo, 500)
    },
    futureRefreshDo () {
      this.futureRefreshRequested = false
      this.refresh()
    },
    refresh () {
      this.request({
        pagination: this.tablePersistSettings.serverPagination,
        filter: this.tablePersistSettings.filter
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
