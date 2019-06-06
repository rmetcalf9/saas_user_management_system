<template>
  <q-page>
    <q-page-sticky position="bottom-right" :offset="[50, 50]">
      <q-btn
        color="negative"
        class="fixed"
        round
        @click="deleteUser"
        icon="delete"
      ></q-btn>
    </q-page-sticky>

  <q-list >
    <q-item clickable v-ripple highlight @click.native="editUser">
      <q-item-section >
        <q-item-label>Job {{ userData.UserID }}</q-item-label>
        <q-item-label caption>Known as {{ userData.known_as }}</q-item-label>
      </q-item-section>
      <q-item-section avatar>
        <q-icon color="primary" name="mode_edit" />
      </q-item-section>
    </q-item>
    <q-item>
      <q-item-section >
        <q-item-label>Other Data</q-item-label>
        <q-item-label caption>{{ userData.other_data }}</q-item-label>
      </q-item-section>
    </q-item>
    <q-item v-for="curRole in userData.TenantRoles" :key=curRole.TenantName>
      <q-item-section >
        <q-item-label>Tenant Roles - {{ curRole.TenantName }}</q-item-label>
        <q-item-label>
          <q-chip size="10px" v-for="curVal in curRole.ThisTenantRoles" :key=curVal>{{ curVal }}</q-chip>
        </q-item-label>
      </q-item-section>
    </q-item>
    <q-item>
      <q-item-section >
        <q-item-label>Linked Person Records ({{ userData['associatedPersonGUIDs'].length }})</q-item-label>
        <q-item-label caption v-for="curPersonGUID in userData.associatedPersonGUIDs" :key=curPersonGUID><a :href="curPathPartBeforeHash + '#/' + $route.params.tenantName + '/persons/' + curPersonGUID">{{ curPersonGUID }}</a></q-item-label>
      </q-item-section>
    </q-item>
    <q-item>
      <q-item-section >
        <q-item-label>Update Info</q-item-label>
        <q-item-label caption>Created {{ userData.creationDateTime }}</q-item-label>
        <q-item-label caption>Last Updated {{ userData.lastUpdateDateTime }}</q-item-label>
      </q-item-section>
    </q-item>
  </q-list>

    <q-modal v-model="editUserModalDialogVisible" :content-css="{minWidth: '40vw', minHeight: '40vh'}">
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
            Edit {{ userData.UserID }} Information
          </q-toolbar-title>
        </q-toolbar>

        <div class="layout-padding">
          <q-field helper="Displayed to user in UI" label="Known As" :label-width="3">
            <q-input v-model="editUserModalDialogData.known_as" @keyup.enter="okEditUserDialog" ref="knownAsInput"/>
          </q-field>
          <q-field helper="Other information about the user (JSON)" label="Other Data" :label-width="3" :error="isOtherDataInvalid">
            <q-input v-model="editUserModalDialogData.other_data" type="textarea" />
          </q-field>
          <q-field :helper="'Roles for ' + curRole.TenantName" :label="curRole.TenantName + ' Roles'" :label-width="3" v-for="curRole in editUserModalDialogData.TenantRoles" :key=curRole.TenantName>
             <q-chips-input v-model="curRole.ThisTenantRoles" />
          </q-field>
          <q-field>
            <q-btn
              @click="addTenantToEditUserDialog"
              color="positive"
              icon="add_to_queue"
              round
              class = "q-ml-xs"
            />          </q-field>
          <div>&nbsp;</div>
          <q-btn
            @click="okEditUserDialog"
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
    var currentURL = new URL(window.location.href)
    return {
      userData: getEmptyUserData(),
      editUserModalDialogData: {
        known_as: '',
        other_data: '',
        TenantRoles: ''
      },
      editUserModalDialogVisible: false,
      curPathPartBeforeHash: currentURL.pathname
    }
  },
  computed: {
    isOtherDataInvalid () {
      try {
        JSON.parse(this.editUserModalDialogData.other_data)
      } catch (e) {
        return true
      }
      return false
    }
  },
  methods: {
    addTenantToEditUserDialog () {
      var TTT = this
      this.$q.dialog({
        title: 'Prompt',
        message: 'Name of Tenant to Add',
        prompt: {
          model: '',
          type: 'text' // optional
        },
        cancel: true,
        color: 'secondary'
      }).onOk(data => {
        for (var curRole in TTT.editUserModalDialogData.TenantRoles) {
          if (TTT.editUserModalDialogData.TenantRoles[curRole].TenantName === data) {
            Notify.create({color: 'negative', detail: 'Already exists'})
            return
          }
        }
        TTT.editUserModalDialogData.TenantRoles.push({TenantName: data, ThisTenantRoles: ['hasaccount']})
        TTT.editUserModalDialogData.TenantRoles.sort()
      }).catch(() => {
        // Do nothing
      })
    },
    okEditUserDialog () {
      var TTT = this
      if (this.isOtherDataInvalid) {
        Notify.create({color: 'negative', detail: 'Other JSON must be valid JSON'})
        return
      }
      this.editUserModalDialogVisible = false
      if (this.editUserModalDialogData.known_as === this.userData.known_as) {
        if (JSON.stringify(JSON.parse(this.editUserModalDialogData.other_data)) === JSON.stringify(this.userData.other_data)) {
          if (JSON.stringify(this.editUserModalDialogData.TenantRoles) === JSON.stringify(this.userData.TenantRoles)) {
            return // no change so do nothing
          }
        }
      }
      var newUserJSON = JSON.parse(JSON.stringify(this.userData))
      newUserJSON.known_as = this.editUserModalDialogData.known_as
      newUserJSON.other_data = JSON.parse(this.editUserModalDialogData.other_data)
      newUserJSON.TenantRoles = []
      for (var curRole in this.editUserModalDialogData.TenantRoles) {
        if (this.editUserModalDialogData.TenantRoles[curRole].ThisTenantRoles.length !== 0) {
          newUserJSON.TenantRoles.push(this.editUserModalDialogData.TenantRoles[curRole])
        }
      }

      var callback = {
        ok: function (response) {
          Notify.create({color: 'positive', detail: 'User Updated'})
          TTT.refreshUserData()
        },
        error: function (error) {
          Notify.create('Update User failed - ' + callbackHelper.getErrorFromResponse(error))
        }
      }
      TTT.$store.dispatch('globalDataStore/callAdminAPI', {
        path: '/users/' + newUserJSON.UserID,
        method: 'put',
        postdata: newUserJSON,
        callback: callback,
        curPath: TTT.$router.history.current.path,
        headers: {'object-version-id': newUserJSON.ObjectVersion}
      })
    },
    cancelEditTenantDialog () {
      this.editUserModalDialogVisible = false
    },
    editUser () {
      this.editUserModalDialogData.known_as = JSON.parse(JSON.stringify(this.userData.known_as))
      this.editUserModalDialogData.other_data = JSON.stringify(this.userData.other_data)
      this.editUserModalDialogData.TenantRoles = JSON.parse(JSON.stringify(this.userData.TenantRoles))

      this.editUserModalDialogVisible = true

      this.$refs.knownAsInput.focus()
    },
    refreshUserData () {
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
    deleteUser () {
      var TTT = this
      var userID = TTT.userData.UserID
      TTT.$q.dialog({
        title: 'Confirm',
        message: 'Are you sure you want to delete ' + userID,
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
        var callback = {
          ok: function (response) {
            Notify.create({color: 'positive', detail: 'User ' + userID + ' deleted'})
            TTT.$router.push('/' + TTT.$route.params.tenantName + '/users/')
          },
          error: function (error) {
            Notify.create('Delete User failed - ' + callbackHelper.getErrorFromResponse(error))
          }
        }
        TTT.$store.dispatch('globalDataStore/callAdminAPI', {
          path: '/users/' + userID,
          method: 'delete',
          postdata: null,
          callback: callback,
          curPath: TTT.$router.history.current.path,
          headers: {'object-version-id': TTT.userData.ObjectVersion}
        })
      }).catch(() => {
        // Do nothing
      })
    }
  },
  mounted () {
    this.refreshUserData()
  }
}
</script>
