<template>
  <q-page>
    <q-page-sticky position="bottom-right" :offset="[50, 50]">
      <q-btn
        color="negative"
        class="fixed"
        round
        @click="deletePerson"
        icon="delete"
      ></q-btn>
    </q-page-sticky>

  <q-list >
    <q-item highlight @click.native="editPerson">
      <q-item-main >
        <q-item-tile label>Person Info</q-item-tile>
        <q-item-tile sublabel>Known as {{ personData.guid }}</q-item-tile>
      </q-item-main>
      <q-item-side right icon="mode_edit" />
    </q-item>
    <q-item>
      <q-item-main >
        <q-item-tile label>Linked User Records ({{ personData.associatedUsers.length }})</q-item-tile>
        <q-item-tile sublabel v-for="curUser in personData.associatedUsers" :key=curUser>
          <a :href="'/#/' + $route.params.tenantName + '/users/' + curUser.UserID">{{ curUser.UserID }}</a>&nbsp;
          <q-btn
            color="negative"
            size="xs"
            round
            @click="unassociateWithUserBtnClick(curUser)"
            icon="remove"
          >
          </q-btn>
        </q-item-tile>
      </q-item-main>
      <q-item-side right>
      <q-btn
        color="positive"
        size="xs"
        round
        @click="associateWithUserBtnClick"
        icon="add"
      ></q-btn>&nbsp;
      </q-item-side>
    </q-item>

    <q-item>
      <q-item-main >
        <q-item-tile label>Auths</q-item-tile>
        <q-item-tile sublabel v-for="curAuth in personData.personAuths" :key=curAuth.AuthUserKey>Provider: {{ curAuth.AuthProviderType }}, Key:{{ curAuth.AuthUserKey }}</q-item-tile>
      </q-item-main>
    </q-item>
    <q-item>
      <q-item-main >
        <q-item-tile label>Update Info</q-item-tile>
        <q-item-tile sublabel>Created {{ personData.creationDateTime }}</q-item-tile>
        <q-item-tile sublabel>Last Updated {{ personData.lastUpdateDateTime }}</q-item-tile>
      </q-item-main>
    </q-item>
  </q-list>

    <q-modal v-model="editPersonModalDialogVisible" :content-css="{minWidth: '40vw', minHeight: '40vh'}">
      <q-modal-layout>
        <q-toolbar slot="header">
            <q-btn
            color="primary"
            flat
            round
            dense
            icon="keyboard_arrow_left"
            @click="cancelEditPersonDialog"
          />
          <q-toolbar-title>
            Edit {{ personData.guid }} Information
          </q-toolbar-title>
        </q-toolbar>

        <div class="layout-padding">
          <q-field helper="No Editable Fields for Person" label="Unknown" :label-width="3">
            <q-input v-model="editPersonModalDialogData.someTextBoxData" @keyup.enter="okEditPersonDialog" ref="someTextBoxDataInput"/>
          </q-field>
          <div>&nbsp;</div>
          <q-btn
            @click="okEditPersonDialog"
            color="primary"
            label="Ok"
            class = "float-right q-ml-xs"
          />
          <q-btn
            @click="cancelEditPersonDialog"
            label="Cancel"
            class = "float-right"
          />
        </div>
      </q-modal-layout>
    </q-modal>

    <UserSelectionModal
      ref="UserSelectionModal"
      :title="'Select User to Associate with person ' + personData.guid"
      @ok="associateWithUserBtnClickSelectUserOK"
    />
  </q-page>

</template>

<style>
</style>

<script>
import { Notify, Loading } from 'quasar'
import callbackHelper from '../callbackHelper'
import UserSelectionModal from '../components/UserSelectionModal'

function getEmptyPersonData () {
  return {
  }
}

export default {
  name: 'PageIndex',
  components: {
    UserSelectionModal
  },
  data () {
    return {
      personData: getEmptyPersonData(),
      editPersonModalDialogData: {
        someTextBoxData: '',
        guid: '',
        ObjectVersion: ''
      },
      editPersonModalDialogVisible: false,
      futureRefreshRequested: false
    }
  },
  methods: {
    _addAuth (userData) {
      var TTT = this
      var callback = {
        ok: function (response) {
          Notify.create({color: 'positive', detail: 'Person Auth Added - ' + userData.UserID})
          TTT.futureRefresh()
        },
        error: function (error) {
          Notify.create('Add Person auth failed ( ' + userData.UserID + ' - ' + callbackHelper.getErrorFromResponse(error))
        }
      }
      TTT.$store.dispatch('globalDataStore/callAdminAPI', {
        path: '/userpersonlinks/' + userData.UserID + '/' + TTT.personData.guid,
        method: 'post',
        postdata: {
          'UserID': userData.UserID,
          'personGUID': TTT.personData.guid
        },
        callback: callback,
        curPath: TTT.$router.history.current.path
      })
    },
    associateWithUserBtnClickSelectUserOK (response) {
      var TTT = this
      for (var x in response.selectedUserList) {
        TTT._addAuth(response.selectedUserList[x])
      }
    },
    associateWithUserBtnClick () {
      this.$refs.UserSelectionModal.launchDialog()
    },
    unassociateWithUserBtnClick (userData) {
      var TTT = this
      TTT.$q.dialog({
        title: 'Confirm',
        message: 'Are you sure you want to remove user auth with ' + userData.UserID,
        ok: {
          push: true,
          label: 'Yes - remove'
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
            Notify.create({color: 'positive', detail: 'Person Auth Removed - ' + userData.UserID})
            // TTT.futureRefresh()
            TTT.refreshPersonData()
          },
          error: function (error) {
            Notify.create('Remove Person auth failed ( ' + userData.UserID + ' - ' + callbackHelper.getErrorFromResponse(error))
          }
        }
        TTT.$store.dispatch('globalDataStore/callAdminAPI', {
          path: '/userpersonlinks/' + userData.UserID + '/' + TTT.personData.guid,
          method: 'delete',
          callback: callback,
          curPath: TTT.$router.history.current.path
        })
      }).catch(() => {
        // Do nothing
      })
    },
    okEditPersonDialog () {
      var TTT = this
      this.editPersonModalDialogVisible = false
      if (this.editPersonModalDialogData.guid === this.personData.guid) {
        // return // no change so do nothing
        console.log('Overrideen no change check')
      }
      var newPersonJSON = {
        guid: this.editPersonModalDialogData.guid,
        ObjectVersion: this.editPersonModalDialogData.ObjectVersion
      }

      var callback = {
        ok: function (response) {
          Notify.create({color: 'positive', detail: 'Person Updated'})
          TTT.refreshPersonData()
        },
        error: function (error) {
          Notify.create('Update Person failed - ' + callbackHelper.getErrorFromResponse(error))
        }
      }
      TTT.$store.dispatch('globalDataStore/callAdminAPI', {
        path: '/persons/' + newPersonJSON.guid,
        method: 'put',
        postdata: newPersonJSON,
        callback: callback,
        curPath: TTT.$router.history.current.path
      })
    },
    cancelEditPersonDialog () {
      this.editPersonModalDialogVisible = false
    },
    editPerson () {
      this.editPersonModalDialogData.someTextBoxData = ''
      this.editPersonModalDialogData.guid = JSON.parse(JSON.stringify(this.personData.guid))
      this.editPersonModalDialogData.ObjectVersion = JSON.parse(JSON.stringify(this.personData.ObjectVersion))

      this.editPersonModalDialogVisible = true

      this.$refs.someTextBoxDataInput.focus()
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
      this.refreshPersonData()
    },
    refreshPersonData () {
      var personIDToLoad = this.$route.params.selPerGUID
      var TTT = this
      var callback = {
        ok: function (response) {
          Loading.hide()
          TTT.personData = response.data
          // TTT.stores().commit('globalDataStore/SET_PAGE_TITLE', 'Person ' + response.data.guid)
        },
        error: function (error) {
          Loading.hide()
          Notify.create('Person query failed - ' + callbackHelper.getErrorFromResponse(error))
          TTT.personData = getEmptyPersonData()
        }
      }
      Loading.show()
      this.$store.dispatch('globalDataStore/callAdminAPI', {
        path: '/persons/' + personIDToLoad,
        method: 'get',
        postdata: null,
        callback: callback,
        curPath: this.$router.history.current.path,
        headers: undefined
      })
    },
    deletePerson () {
      var TTT = this
      var personGUID = TTT.personData.guid
      TTT.$q.dialog({
        title: 'Confirm',
        message: 'Are you sure you want to delete ' + personGUID,
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
            Notify.create({color: 'positive', detail: 'Person ' + personGUID + ' deleted'})
            TTT.$router.push('/' + TTT.$route.params.tenantName + '/persons/')
          },
          error: function (error) {
            Notify.create('Delete Person failed - ' + callbackHelper.getErrorFromResponse(error))
          }
        }
        TTT.$store.dispatch('globalDataStore/callAdminAPI', {
          path: '/persons/' + personGUID,
          method: 'delete',
          postdata: null,
          callback: callback,
          curPath: TTT.$router.history.current.path,
          headers: {'object-version-id': TTT.personData.ObjectVersion}
        })
      }).catch(() => {
        // Do nothing
      })
    }
  },
  mounted () {
    this.refreshPersonData()
  }
}
</script>
