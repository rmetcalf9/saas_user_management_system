<template><div>
  <q-table
    title='Users'
    :rows-per-page-options="tableRowsPerPageOptions"
    :loading="tableLoading"
    :rows="tableData"
    :columns="tableColumns"
    @request="request"
    row-key="UserID"
    :visible-columns="tablePersistSettings.visibleColumns"
    :filter="tablePersistSettings.filter"
    :pagination="tablePersistSettings.serverPagination"
    selection="multiple"
    v-model:selected="tableSelected"
  >
    <template v-slot:top-selection>
      <q-btn flat round negative delete icon="delete" @click="deleteSelectedUsers" />
    </template>

    <template v-slot:top-left>
      <q-btn
        color="primary"
        push
        @click="createUserButtonClick"
      >Create User</q-btn>&nbsp;
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

    <template v-slot:body-cell-TenantRoles="props">
      <q-td :props="props">
        {{ props.row.TenantRoles }}
      </q-td>
    </template>

    <template v-slot:body-cell-...="props">
      <q-td :props="props">
        <q-btn flat color="primary" icon="keyboard_arrow_right" label="" @click="clickSingleUser(props)" />
      </q-td>
    </template>
  </q-table>
  <!--
  <q-dialog v-model="createUserModalDialogVisible">
    <q-layout view="Lhh lpR fff" container class="bg-white" style="height: 400px; width: 700px; max-width: 80vw;">
      <q-header class="bg-primary">
        <q-toolbar>
          <q-toolbar-title>
            Create new user
          </q-toolbar-title>
          <q-btn flat v-close-popup round dense icon="close" />
        </q-toolbar>
      </q-header>

      <q-page-container>
        <q-page padding>
          <q-input v-model="createUserModalDialogData.UserID" ref="userIDInput" label="User ID" :label-width="3"/> Normally &lt;User ID>@&lt;Auth Prov>
          <q-input v-model="createUserModalDialogData.known_as" label="Known As" :label-width="3"/> Name displayed to user
          <q-input v-model="createUserModalDialogData.mainTenant" @keyup.enter="okCreateUserDialog" label="Main Tenant" :label-width="3"/> Optional Tenant to create a hasaccount role
        <div>&nbsp;</div>
        <q-btn
          @click="okCreateUserDialog"
          color="primary"
          label="Ok"
          class = "float-right q-ml-xs"
        />
        <q-btn
          label="Cancel"
          class = "float-right"
          v-close-popup
        />
        </q-page>
      </q-page-container>
    </q-layout>
  </q-dialog>
-->
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
        { name: 'UserID', required: true, label: 'UserID', align: 'left', field: 'UserID', sortable: false, filter: false },
        { name: 'known_as', required: false, label: 'Known As', align: 'left', field: 'known_as', sortable: false, filter: false },
        { name: 'TenantRoles', required: false, label: 'Tenant Roles', align: 'left', field: 'TenantRoles', sortable: false, filter: false },
        { name: 'other_data', required: false, label: 'other_data', align: 'left', field: 'other_data', sortable: false, filter: false },
        { name: 'creationDateTime', required: false, label: 'creationDateTime', align: 'left', field: 'creationDateTime', sortable: false, filter: false },
        { name: 'lastUpdateDateTime', required: false, label: 'lastUpdateDateTime', align: 'left', field: 'lastUpdateDateTime', sortable: false, filter: false },
        { name: '...', required: true, label: '', align: 'left', field: 'guid', sortable: false, filter: false }
      ],
      tableSelected: [],
      futureRefreshRequested: false,
      createUserModalDialogVisible: false,
      createUserModalDialogData: {
        UserID: '',
        known_as: '',
        mainTenant: ''
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
    clickSingleUser (props) {
      console.log('TODO clickSingleUser', props)
    },
    createUserButtonClick () {
      console.log('TODO createUserButtonClick')
    },
    deleteSelectedUsers () {
      console.log('TODO deleteSelectedUsers')
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
      const queryString = restcallutils.buildQueryString('/' + TTT.tenantName + '/users', queryParams)
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
