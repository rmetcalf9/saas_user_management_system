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
  <q-dialog v-model="createUserModalDialogVisible">
    <q-card style="width: 700px; max-width: 80vw; max-height: 90vh; display: flex; flex-direction: column;">
      <!-- Header -->
      <q-toolbar class="bg-primary text-white">
        <q-toolbar-title>
          Create new user
        </q-toolbar-title>
        <q-btn flat v-close-popup round dense icon="close" />
      </q-toolbar>

      <!-- Scrollable Body -->
      <q-card-section style="flex: 1; overflow-y: auto;">
        <q-input
          v-model="createUserModalDialogData.UserID"
          ref="userIDInput"
          label="User ID"
          :label-width="3"
        />
        <div class="text-caption text-grey q-mb-md">
          Normally &lt;User ID&gt;@&lt;Auth Prov&gt;
        </div>

        <q-input
          v-model="createUserModalDialogData.known_as"
          label="Known As"
          :label-width="3"
        />
        <div class="text-caption text-grey q-mb-md">
          Name displayed to user
        </div>

        <q-input
          v-model="createUserModalDialogData.mainTenant"
          @keyup.enter="okCreateUserDialog"
          label="Main Tenant"
          :label-width="3"
        />
        <div class="text-caption text-grey">
          Optional Tenant to create a hasaccount role
        </div>
      </q-card-section>

      <!-- Footer -->
      <q-separator />
      <q-card-actions
        align="right"
        class="bg-grey-2"
        style="position: sticky; bottom: 0; z-index: 1;"
      >
        <q-btn
          @click="okCreateUserDialog"
          color="primary"
          label="Ok"
          class="q-ml-xs"
        />
        <q-btn
          label="Cancel"
          v-close-popup
        />
      </q-card-actions>
    </q-card>
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
      if (typeof (this.clickSingleUserCallback) !== 'undefined') {
        this.clickSingleUserCallback(props)
      }
    },
    createUserButtonClick () {
      this.createUserModalDialogData.UserID = ''
      this.createUserModalDialogData.known_as = ''
      this.createUserModalDialogData.mainTenant = ''
      this.createUserModalDialogVisible = true
      const TTT = this
      setTimeout(function () {
        // Highlight default field
        TTT.$refs.userIDInput.focus()
      }, 5)
    },
    okCreateUserDialog () {
      const TTT = this
      const jsonToSend = {
        UserID: this.createUserModalDialogData.UserID,
        known_as: this.createUserModalDialogData.known_as,
        mainTenant: this.createUserModalDialogData.mainTenant
      }
      const callback = {
        ok: function (response) {
          TTT.createUserModalDialogVisible = false
          Notify.create({ color: 'positive', message: 'User Created' })
          TTT.refresh()
        },
        error: function (error) {
          Notify.create({ color: 'negative', message: 'Create User failed - ' + callbackHelper.getErrorFromResponse(error) })
        }
      }
      saasApiClientCallBackend.callApi({
        prefix: 'admin',
        router: this.$router,
        store: this.userManagementClientStoreStore,
        path: '/' + TTT.tenantName + '/users',
        method: 'post',
        postdata: jsonToSend,
        callback
      })
    },
    deleteSelectedUsers () {
      const TTT = this
      const usersToDelete = this.tableSelected.map(function (usr) {
        return usr
      })
      TTT.$q.dialog({
        title: 'Confirm',
        message: 'Are you sure you want to delete ' + usersToDelete.length + ' users?',
        ok: {
          push: true,
          label: 'Yes - delete'
        },
        cancel: {
          push: true,
          label: 'Cancel'
        }
        // preventClose: false,
        // noBackdropDismiss: false,
        // noEscDismiss: false
      }).onOk(() => {
        // only clear slection if ok is used
        TTT.tableSelected = []
        usersToDelete.forEach(function (usr) {
          TTT.deleteUserNoConfirm(usr)
        })
      })
    },
    deleteUserNoConfirm (usr) {
      const TTT = this
      const callback = {
        ok: function (response) {
          Notify.create({ color: 'positive', message: 'User ' + usr.UserID + ' deleted' })
          TTT.futureRefresh()
        },
        error: function (error) {
          Notify.create('Delete User failed - ' + callbackHelper.getErrorFromResponse(error))
        }
      }
      saasApiClientCallBackend.callApi({
        prefix: 'admin',
        router: this.$router,
        store: this.userManagementClientStoreStore,
        path: '/' + TTT.tenantName + '/users/' + usr.UserID,
        method: 'delete',
        postdata: null,
        callback,
        extraHeaders: { 'object-version-id': usr.ObjectVersion }
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
