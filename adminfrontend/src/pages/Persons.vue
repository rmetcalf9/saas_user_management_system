<template>
  <q-page>
  <q-table
    title='Persons'
    :rows-per-page-options="tableRowsPerPageOptions"
    :loading="tableLoading"
    :data="tableData"
    :columns="tableColumns"
    @request="request"
    row-key="guid"
    :visible-columns="tablePersistSettings.visibleColumns"
    :filter="tablePersistSettings.filter"
    :pagination.sync="tablePersistSettings.serverPagination"
    selection="multiple"
    :selected.sync="tableSelected"
  >
      <template slot="top-selection" slot-scope="props">
        <q-btn flat round negative delete icon="delete" @click="deleteSelectedPersons" />
      </template>

      <template slot="top-left" slot-scope="props">
        <q-btn
          color="primary"
          push
          @click="createPersonButtonClick"
        >Create Person</q-btn>
      </template>
      <template slot="top-right" slot-scope="props">
       <q-table-columns
        color="secondary"
        class="q-mr-sm"
        v-model="tablePersistSettings.visibleColumns"
        :columns="tableColumns"
      />
      </template>

      <q-td slot="body-cell-..." slot-scope="props" :props="props">
        <q-btn flat color="primary" icon="keyboard_arrow_right" label="" @click="$router.push('/' + $route.params.tenantName + '/persons/' + props.row.guid)" />
      </q-td>
  </q-table>

    <q-modal v-model="createPersonModalDialogVisible" :content-css="{minWidth: '40vw', minHeight: '40vh'}">
      <q-modal-layout>
        <q-toolbar slot="header">
            <q-btn
            color="primary"
            flat
            round
            dense
            icon="keyboard_arrow_left"
            @click="cancelCreatePersonDialog"
          />
          <q-toolbar-title>
            Create new person
          </q-toolbar-title>
        </q-toolbar>

        <div class="layout-padding">
          <q-field helper="No Editable Person Data" label="Unknown" :label-width="3">
            <q-input v-model="createPersonModalDialogData.guid" ref="personIDInput"/>
          </q-field>
          <div>&nbsp;</div>
          <q-btn
            @click="okCreatePersonDialog"
            color="primary"
            label="Ok"
            class = "float-right q-ml-xs"
          />
          <q-btn
            @click="cancelCreatePersonDialog"
            label="Cancel"
            class = "float-right"
          />
        </div>
      </q-modal-layout>
    </q-modal>

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
        { name: 'guid', required: true, label: 'guid', align: 'left', field: 'guid', sortable: false, filter: false },
        { name: 'creationDateTime', required: false, label: 'creationDateTime', align: 'left', field: 'creationDateTime', sortable: false, filter: false },
        { name: 'lastUpdateDateTime', required: false, label: 'lastUpdateDateTime', align: 'left', field: 'lastUpdateDateTime', sortable: false, filter: false },
        { name: '...', required: true, label: '', align: 'left', field: 'guid', sortable: false, filter: false }
      ],
      tableSelected: [],
      tablePersistSettings: {
        visibleColumns: ['guid'],
        serverPagination: {
          page: 1,
          rowsNumber: 10, // specifying this determines pagination is server-side
          rowsPerPage: 10,
          sortBy: null,
          descending: true
        },
        filter: ''
      },
      futureRefreshRequested: false,
      createPersonModalDialogVisible: false,
      createPersonModalDialogData: {
        guid: ''
      }
    }
  },
  methods: {
    deletePersonNoConfirm (TTT, usr) {
      var callback = {
        ok: function (response) {
          Notify.create({color: 'positive', detail: 'Person ' + usr.guid + ' deleted'})
          TTT.futureRefresh()
        },
        error: function (error) {
          Notify.create('Delete Person failed - ' + callbackHelper.getErrorFromResponse(error))
        }
      }
      TTT.$store.dispatch('globalDataStore/callAdminAPI', {
        path: '/persons/' + usr.guid,
        method: 'delete',
        postdata: null,
        callback: callback,
        curPath: TTT.$router.history.current.path,
        headers: {'object-version-id': usr.ObjectVersion}
      })
    },
    deleteSelectedPersons () {
      var TTT = this
      var personsToDelete = this.tableSelected.map(function (usr) {
        return usr
      })
      TTT.tableSelected = []
      TTT.$q.dialog({
        title: 'Confirm',
        message: 'Are you sure you want to delete ' + personsToDelete.length + ' Person records?',
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
      }).then(() => {
        personsToDelete.map(function (usr) {
          TTT.deletePersonNoConfirm(TTT, usr)
        })
      }).catch(() => {
        // Do nothing
      })
    },
    cancelCreatePersonDialog () {
      this.createPersonModalDialogVisible = false
    },
    okCreatePersonDialog () {
      var TTT = this
      var jsonToSend = {
        // 'guid': this.createPersonModalDialogData.guid NO data can be sent
      }
      var callback = {
        ok: function (response) {
          TTT.createPersonModalDialogVisible = false
          Notify.create({color: 'positive', detail: 'Person Created'})
          TTT.refresh()
        },
        error: function (error) {
          Notify.create('Create Person failed - ' + callbackHelper.getErrorFromResponse(error))
        }
      }
      TTT.$store.dispatch('globalDataStore/callAdminAPI', {
        path: '/persons',
        method: 'post',
        postdata: jsonToSend,
        callback: callback,
        curPath: TTT.$router.history.current.path
      })
    },
    createPersonButtonClick () {
      this.createPersonModalDialogData.guid = ''

      this.createPersonModalDialogVisible = true

      this.$refs.PersonIDInput.focus()
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
      var queryString = restcallutils.buildQueryString('/persons', queryParams)
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
  },
  mounted () {
    // once mounted, we need to trigger the initial server data fetch
    this.refresh()
  }
}
</script>
