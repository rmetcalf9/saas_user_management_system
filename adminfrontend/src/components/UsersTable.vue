<template><div>
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
    selection="multiple"
    :selected.sync="tableSelected"
  >
      <template slot="top-selection" slot-scope="props">
        <q-btn flat round negative delete icon="delete" @click="deleteSelectedUsers" />
      </template>

      <template slot="top-left" slot-scope="props">
        <q-btn
          color="primary"
          push
          @click="createUserButtonClick"
        >Create User</q-btn>&nbsp;
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

      <q-td  slot="body-cell-TenantRoles" slot-scope="props" :props="props">
        {{ props.row.TenantRoles }}
      </q-td>

      <q-td  slot="body-cell-other_data" slot-scope="props" :props="props">
        {{ props.row.other_data }}
      </q-td>

      <q-td slot="body-cell-..." slot-scope="props" :props="props">
        <q-btn flat color="primary" icon="keyboard_arrow_right" label="" @click="clickSingleUser(props)" />
      </q-td>
  </q-table>

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

  </div>
</template>

<script>
import { Notify } from 'quasar'
import restcallutils from '../restcallutils'
import callbackHelper from '../callbackHelper'
import selectColumns from '../components/selectColumns'

export default {
  // name: 'UsersTable',
  props: [
    'defaultDisplayedColumns',
    'persistantSettingsSlot',
    'clickSingleUserCallback'
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
        { name: 'UserID', required: true, label: 'UserID', align: 'left', field: 'UserID', sortable: false, filter: false },
        { name: 'Known As', required: false, label: 'Known As', align: 'left', field: 'known_as', sortable: false, filter: false },
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
  methods: {
    clickSingleUser (props) {
      if (typeof (this.clickSingleUserCallback) !== 'undefined') {
        this.clickSingleUserCallback(props)
      }
    },
    deleteUserNoConfirm (TTT, usr) {
      var callback = {
        ok: function (response) {
          Notify.create({color: 'positive', message: 'User ' + usr.UserID + ' deleted'})
          TTT.futureRefresh()
        },
        error: function (error) {
          Notify.create('Delete User failed - ' + callbackHelper.getErrorFromResponse(error))
        }
      }
      TTT.$store.dispatch('globalDataStore/callAdminAPI', {
        path: '/users/' + usr.UserID,
        method: 'delete',
        postdata: null,
        callback: callback,
        curPath: TTT.$router.history.current.path,
        headers: {'object-version-id': usr.ObjectVersion}
      })
    },
    deleteSelectedUsers () {
      var TTT = this
      var usersToDelete = this.tableSelected.map(function (usr) {
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
        usersToDelete.map(function (usr) {
          TTT.deleteUserNoConfirm(TTT, usr)
        })
      }).catch(() => {
        // Do nothing
      })
    },
    cancelCreateUserDialog () {
      this.createUserModalDialogVisible = false
    },
    okCreateUserDialog () {
      var TTT = this
      var jsonToSend = {
        'UserID': this.createUserModalDialogData.UserID,
        'known_as': this.createUserModalDialogData.known_as,
        'mainTenant': this.createUserModalDialogData.mainTenant
      }
      var callback = {
        ok: function (response) {
          TTT.createUserModalDialogVisible = false
          Notify.create({color: 'positive', message: 'User Created'})
          TTT.refresh()
        },
        error: function (error) {
          Notify.create({color: 'negative', message: 'Create User failed - ' + callbackHelper.getErrorFromResponse(error)})
        }
      }
      TTT.$store.dispatch('globalDataStore/callAdminAPI', {
        path: '/users',
        method: 'post',
        postdata: jsonToSend,
        callback: callback,
        curPath: TTT.$router.history.current.path
      })
    },
    createUserButtonClick () {
      this.createUserModalDialogData.UserID = ''
      this.createUserModalDialogData.known_as = ''
      this.createUserModalDialogData.mainTenant = ''

      this.createUserModalDialogVisible = true

      this.$refs.userIDInput.focus()
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
