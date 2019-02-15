<template>
  <q-page>
    <q-page-sticky position="bottom-right" :offset="[50, 50]">
      <q-btn
        color="negative"
        class="fixed"
        round
        @click="deleteTenant"
        icon="delete"
      ></q-btn>
    </q-page-sticky>

  <q-list >
    <q-item highlight @click.native="editTenant">
      <q-item-main >
        <q-item-tile label>Tenant Name: {{ tenantData.Name }}</q-item-tile>
        <q-item-tile sublabel>{{ tenantData.Description }}</q-item-tile>
      </q-item-main>
      <q-item-side right icon="mode_edit" />
    </q-item>
    <q-item>
      <q-item-main >
        <q-item-tile label>Allow User Creation:</q-item-tile>
        <q-item-tile sublabel v-if="tenantData.AllowUserCreation">New users can sign up</q-item-tile>
        <q-item-tile sublabel v-if="!tenantData.AllowUserCreation">Users must be created by admins</q-item-tile>
      </q-item-main>
    </q-item>
  </q-list>

  <q-table
    title='Auth Providers'
    :data="tenantData.AuthProviders"
    :columns="tableColumns"
    row-key="name"
  >
    <q-td slot="body-cell-..." slot-scope="props" :props="props">
      <q-btn flat color="primary" icon="mode_edit" label="" @click="editAuthProv(props.row)" />
    </q-td>
  </q-table>
  <q-btn
    @click="addAuthProv"
    color="primary"
    label="Add Auth Provider"
    class = "float-left q-ma-xs"
  />

    <q-modal v-model="editTenantModalDialogVisible" :content-css="{minWidth: '40vw', minHeight: '40vh'}">
      <q-modal-layout>
        <q-toolbar slot="header">
            <q-btn
            color="primary"
            flat
            round
            dense
            icon="keyboard_arrow_left"
            @click="cancelEditTenantDialog"
          />
          <q-toolbar-title>
            Edit Tenant Information
          </q-toolbar-title>
        </q-toolbar>

        <div class="layout-padding">
          <q-field helper="Description of Tenant" label="Descrption" :label-width="3">
            <q-input v-model="editTenantModalDialogData.Description" @keyup.enter="okEditTenantDialog" ref="descriptionInput"/>
          </q-field>
          <q-field helper="Must be on for both Tenant and Auth Provider to be effective" label="Allow User Creation" :label-width="3">
            <q-toggle v-model="editTenantModalDialogData.AllowUserCreation" />
          </q-field>
          <div>&nbsp;</div>
          <q-btn
            @click="okEditTenantDialog"
            color="primary"
            label="Ok"
            class = "float-right q-ml-xs"
          />
          <q-btn
            @click="cancelEditTenantDialog"
            label="Cancel"
            class = "float-right"
          />
        </div>
      </q-modal-layout>
    </q-modal>

    <q-modal v-model="editAuthProvModalDialogVisible" :content-css="{minWidth: '40vw', minHeight: '40vh'}">
      <q-modal-layout>
        <q-toolbar slot="header">
            <q-btn
            color="primary"
            flat
            round
            dense
            icon="keyboard_arrow_left"
            @click="cancelAuthProvTenantDialog"
          />
          <q-toolbar-title v-if="editAuthProvModalDialogData.AddMode">
            Add Auth Provider for {{ tenantData.Name }}
          </q-toolbar-title>
          <q-toolbar-title v-if="!editAuthProvModalDialogData.AddMode">
            Edit {{ editAuthProvModalDialogData.Type }} Auth Provider for {{ tenantData.Name }}
          </q-toolbar-title>
        </q-toolbar>

        <div class="layout-padding">
          <q-field helper="Type" label="Type" :label-width="3">
            <q-input v-model="editAuthProvModalDialogData.Type" />
          </q-field>
          <q-field helper="Must be on for both Tenant and Auth Provider to be effective" label="Allow User Creation" :label-width="3">
            <q-toggle v-model="editAuthProvModalDialogData.AllowUserCreation" />
          </q-field>
          <q-field helper="Text to display in select auth dialog" label="Menu Text" :label-width="3">
            <q-input v-model="editAuthProvModalDialogData.MenuText" />
          </q-field>
          <q-field helper="Link to icon to be used in select auth dialog" label="Icon Link" :label-width="3">
            <q-input v-model="editAuthProvModalDialogData.IconLink" />
          </q-field>
          <div>&nbsp;</div>
          <q-btn
            @click="okAuthProvTenantDialog"
            color="primary"
            label="Ok"
            class = "float-right q-ml-xs"
          />
          <q-btn
            @click="cancelAuthProvTenantDialog"
            label="Cancel"
            class = "float-right"
          />
        </div>
      </q-modal-layout>
    </q-modal>
  {{ tenantData }}
  </q-page>
</template>

<style>
</style>

<script>
import { Notify, Loading } from 'quasar'
import callbackHelper from '../callbackHelper'

function getEmptyTenantData () {
  return {
    AuthProviders: []
  }
}

export default {
  name: 'PageIndex',
  data () {
    return {
      tenantData: getEmptyTenantData(),
      tableColumns: [
        { name: 'Type', required: true, label: 'Type', align: 'left', field: 'Type', sortable: true, filter: false },
        { name: 'AllowUserCreation', required: true, label: 'AllowUserCreation', align: 'left', field: 'AllowUserCreation', sortable: true, filter: false },
        { name: 'MenuText', required: true, label: 'MenuText', align: 'left', field: 'MenuText', sortable: true, filter: false },
        { name: 'IconLink', required: true, label: 'IconLink', align: 'left', field: 'IconLink', sortable: true, filter: false },
        { name: '...', required: true, label: '', align: 'left', field: 'guid', sortable: false, filter: false }
        // guid not in table
        // ConfigJSON not in table
      ],
      editTenantModalDialogData: {
        Description: '',
        AllowUserCreation: false
      },
      editTenantModalDialogVisible: false,
      editAuthProvModalDialogData: {
        AddMode: false,
        Type: 'internal',
        AllowUserCreation: false,
        MenuText: '',
        IconLink: '',
        guid: ''
      },
      editAuthProvModalDialogVisible: false
    }
  },
  methods: {
    addAuthProv () {
      this.editAuthProvModalDialogData.AddMode = true
      this.editAuthProvModalDialogData.Type = 'internal'
      this.editAuthProvModalDialogData.AllowUserCreation = false
      this.editAuthProvModalDialogData.MenuText = ''
      this.editAuthProvModalDialogData.IconLink = ''
      this.editAuthProvModalDialogData.guid = ''

      this.editAuthProvModalDialogVisible = true
    },
    editAuthProv (item) {
      this.editAuthProvModalDialogData.AddMode = false
      this.editAuthProvModalDialogData.Type = item.Type
      this.editAuthProvModalDialogData.AllowUserCreation = item.AllowUserCreation
      this.editAuthProvModalDialogData.MenuText = item.MenuText
      this.editAuthProvModalDialogData.IconLink = item.IconLink
      this.editAuthProvModalDialogData.guid = item.guid

      this.editAuthProvModalDialogVisible = true
    },
    okAuthProvTenantDialog () {
      var TTT = this

      // Shared validation
      if (this.editAuthProvModalDialogData.MenuText === '') {
        Notify.create({color: 'negative', detail: 'Menu text must be filled in'})
        return
      }

      var newTenantJSON = JSON.parse(JSON.stringify(this.tenantData))
      var newAuthProvJSON = {
        Type: TTT.editAuthProvModalDialogData.Type,
        AllowUserCreation: TTT.editAuthProvModalDialogData.AllowUserCreation,
        MenuText: TTT.editAuthProvModalDialogData.MenuText,
        IconLink: TTT.editAuthProvModalDialogData.IconLink,
        guid: TTT.editAuthProvModalDialogData.guid
      }
      if (this.editAuthProvModalDialogData.AddMode) {
        newTenantJSON.AuthProviders.push(newAuthProvJSON)
      } else {
        Notify.create('TODO Edit mode')
      }
      console.log('newTenantJSON:', newTenantJSON)
      var callback = {
        ok: function (response) {
          Notify.create({color: 'positive', detail: 'Tenant Updated'})
          TTT.refreshTenantData()
        },
        error: function (error) {
          Notify.create('Update Tenant failed - ' + callbackHelper.getErrorFromResponse(error))
        }
      }
      TTT.$store.dispatch('globalDataStore/callAdminAPI', {
        path: '/tenants/' + newTenantJSON.Name,
        method: 'put',
        postdata: newTenantJSON,
        callback: callback,
        curPath: TTT.$router.history.current.path,
        headers: {'object-version-id': newTenantJSON.ObjectVersion}
      })

      this.editAuthProvModalDialogVisible = false
    },
    cancelAuthProvTenantDialog () {
      this.editAuthProvModalDialogVisible = false
    },
    okEditTenantDialog () {
      var TTT = this
      this.editTenantModalDialogVisible = false
      if (this.editTenantModalDialogData.Description === this.tenantData.Description) {
        if (this.editTenantModalDialogData.AllowUserCreation === this.tenantData.AllowUserCreation) {
          return // no change so do nothing
        }
      }
      var newTenantJSON = JSON.parse(JSON.stringify(this.tenantData))
      newTenantJSON.Description = this.editTenantModalDialogData.Description
      newTenantJSON.AllowUserCreation = this.editTenantModalDialogData.AllowUserCreation

      var callback = {
        ok: function (response) {
          Notify.create({color: 'positive', detail: 'Tenant Updated'})
          TTT.refreshTenantData()
        },
        error: function (error) {
          Notify.create('Update Tenant failed - ' + callbackHelper.getErrorFromResponse(error))
        }
      }
      TTT.$store.dispatch('globalDataStore/callAdminAPI', {
        path: '/tenants/' + newTenantJSON.Name,
        method: 'put',
        postdata: newTenantJSON,
        callback: callback,
        curPath: TTT.$router.history.current.path,
        headers: {'object-version-id': newTenantJSON.ObjectVersion}
      })
    },
    cancelEditTenantDialog () {
      this.editTenantModalDialogVisible = false
    },
    editTenant () {
      this.editTenantModalDialogData.Description = this.tenantData.Description
      this.editTenantModalDialogData.AllowUserCreation = this.tenantData.AllowUserCreation

      this.editTenantModalDialogVisible = true

      this.$refs.descriptionInput.focus()
    },
    refreshTenantData () {
      var jobNameToLoad = this.$route.params.selTenantNAME
      var TTT = this
      var callback = {
        ok: function (response) {
          Loading.hide()
          TTT.tenantData = response.data
          // TTT.stores().commit('globalDataStore/SET_PAGE_TITLE', 'Tenant ' + response.data.Name)
        },
        error: function (error) {
          Loading.hide()
          Notify.create('Tenant query failed - ' + callbackHelper.getErrorFromResponse(error))
          TTT.tenantData = getEmptyTenantData()
        }
      }
      Loading.show()
      this.$store.dispatch('globalDataStore/callAdminAPI', {
        path: '/tenants/' + jobNameToLoad,
        method: 'get',
        postdata: null,
        callback: callback,
        curPath: this.$router.history.current.path,
        headers: undefined
      })
    },
    deleteTenant () {
      var TTT = this
      var nameOfTenantToDelete = TTT.tenantData.Name
      TTT.$q.dialog({
        title: 'Confirm',
        message: 'Are you sure you want to delete ' + nameOfTenantToDelete,
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
        var callback = {
          ok: function (response) {
            Notify.create({color: 'positive', detail: 'Tenant ' + nameOfTenantToDelete + ' deleted'})
            TTT.$router.push('/' + TTT.$route.params.tenantName + '/tenants/')
          },
          error: function (error) {
            Notify.create('Delete Tenant failed - ' + callbackHelper.getErrorFromResponse(error))
          }
        }
        TTT.$store.dispatch('globalDataStore/callAdminAPI', {
          path: '/tenants/' + nameOfTenantToDelete,
          method: 'delete',
          postdata: null,
          callback: callback,
          curPath: TTT.$router.history.current.path,
          headers: {'object-version-id': TTT.tenantData.ObjectVersion}
        })
      }).catch(() => {
        // Do nothing
      })
    }
  },
  mounted () {
    this.refreshTenantData()
  }
}
</script>
