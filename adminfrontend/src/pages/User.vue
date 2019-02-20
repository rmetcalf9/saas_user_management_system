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
        <q-item-tile label>{{ userData.known_as }}</q-item-tile>
        <q-item-tile sublabel>{{ userData.UserID }}</q-item-tile>
      </q-item-main>
      <q-item-side right icon="mode_edit" />
    </q-item>
    <q-item>
      <q-item-main >
        <q-item-tile label>Tenant Roles</q-item-tile>
        <q-item-tile sublabel>{{ userData.TenantRoles }}</q-item-tile>
      </q-item-main>
    </q-item>
    <q-item>
      <q-item-main >
        <q-item-tile label>Other Data</q-item-tile>
        <q-item-tile sublabel>{{ userData.other_data }}</q-item-tile>
      </q-item-main>
    </q-item>
  </q-list>

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
          <q-field helper="Description of Tenant" label="Description" :label-width="3">
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

  </q-page>
</template>

<style>
</style>

<script>
import { Notify, Loading } from 'quasar'
import callbackHelper from '../callbackHelper'

function getEmptyUserData () {
  return {
  }
}

export default {
  name: 'PageIndex',
  data () {
    return {
      userData: getEmptyUserData(),
      editTenantModalDialogData: {
        Description: '',
        AllowUserCreation: false
      },
      editTenantModalDialogVisible: false
    }
  },
  methods: {
    okEditTenantDialog () {
      var TTT = this
      this.editTenantModalDialogVisible = false
      if (this.editTenantModalDialogData.Description === this.userData.Description) {
        if (this.editTenantModalDialogData.AllowUserCreation === this.userData.AllowUserCreation) {
          return // no change so do nothing
        }
      }
      var newUserJSON = JSON.parse(JSON.stringify(this.userData))
      newUserJSON.Description = this.editTenantModalDialogData.Description
      newUserJSON.AllowUserCreation = this.editTenantModalDialogData.AllowUserCreation

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
        path: '/users/' + newUserJSON.Name,
        method: 'put',
        postdata: newUserJSON,
        callback: callback,
        curPath: TTT.$router.history.current.path,
        headers: {'object-version-id': newUserJSON.ObjectVersion}
      })
    },
    cancelEditTenantDialog () {
      this.editTenantModalDialogVisible = false
    },
    editTenant () {
      this.editTenantModalDialogData.Description = this.userData.Description
      this.editTenantModalDialogData.AllowUserCreation = this.userData.AllowUserCreation

      this.editTenantModalDialogVisible = true

      this.$refs.descriptionInput.focus()
    },
    refreshTenantData () {
      var userIDToLoad = this.$route.params.selUserID
      var TTT = this
      var callback = {
        ok: function (response) {
          Loading.hide()
          TTT.userData = response.data
          // TTT.stores().commit('globalDataStore/SET_PAGE_TITLE', 'User ' + response.data.known_as)
        },
        error: function (error) {
          Loading.hide()
          Notify.create('User query failed - ' + callbackHelper.getErrorFromResponse(error))
          TTT.userData = getEmptyUserData()
        }
      }
      Loading.show()
      this.$store.dispatch('globalDataStore/callAdminAPI', {
        path: '/users/' + userIDToLoad,
        method: 'get',
        postdata: null,
        callback: callback,
        curPath: this.$router.history.current.path,
        headers: undefined
      })
    },
    deleteTenant () {
      var TTT = this
      var nameOfTenantToUser = TTT.userData.Name
      TTT.$q.dialog({
        title: 'Confirm',
        message: 'Are you sure you want to delete ' + nameOfTenantToUser,
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
            Notify.create({color: 'positive', detail: 'Tenant ' + nameOfTenantToUser + ' deleted'})
            TTT.$router.push('/' + TTT.$route.params.tenantName + '/tenants/')
          },
          error: function (error) {
            Notify.create('Delete Tenant failed - ' + callbackHelper.getErrorFromResponse(error))
          }
        }
        TTT.$store.dispatch('globalDataStore/callAdminAPI', {
          path: '/users/' + nameOfTenantToUser,
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
