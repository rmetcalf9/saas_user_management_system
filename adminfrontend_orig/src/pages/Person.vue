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
    <q-item clickable v-ripple highlight @click.native="editPerson">
      <q-item-section >
        <q-item-label>Person Info</q-item-label>
        <q-item-label caption>Known as {{ personData.guid }}</q-item-label>
      </q-item-section>
      <q-item-section avatar>
        <q-icon color="primary" name="mode_edit" />
      </q-item-section>
    </q-item>
    <q-item>
      <q-item-section >
        <q-item-label>Linked User Records ({{ numberOfAssociatedUsers }})</q-item-label>
        <q-item-label caption v-for="curUser in personData.associatedUsers" :key=curUser.UserID>
          <a :href="curPathPartBeforeHash + '#/' + $route.params.tenantName + '/users/' + curUser.UserID">{{ curUser.UserID }}</a>&nbsp;
          <q-btn
            color="negative"
            size="xs"
            round
            @click="unassociateWithUserBtnClick(curUser)"
            icon="remove"
          >
          </q-btn>
        </q-item-label>
      </q-item-section>
      <q-item-section avatar>
        <q-btn
          color="positive"
          size="xs"
          round
          @click="associateWithUserBtnClick"
          icon="add"
        ></q-btn>
      </q-item-section>
    </q-item>
    <q-item>
      <q-item-section >
        <q-item-label>Auths</q-item-label>
        <q-item v-for="curAuth in personData.personAuths" :key=curAuth.AuthUserKey>
          <q-item-section >
            <div v-if="supportedAuthType(curAuth.AuthProviderType) === 'internal'">
              <q-item-label>
                {{ curAuth.tenantName }} - {{ curAuth.AuthProviderType }}, Key:{{ curAuth.AuthUserKey }}
                <q-btn class="float-left" color="negative" round @click="deleteAuth(curAuth)" icon="remove" size="xs" />
                <AuthDisplayInternal
                  :person="personData"
                  :authData="curAuth"
                />
              </q-item-label>
            </div>
            <div v-if="supportedAuthType(curAuth.AuthProviderType) === 'default'">
              <q-item-label> {{ curAuth.tenantName }} - {{ curAuth.AuthProviderType }}, Key:{{ curAuth.AuthUserKey }}</q-item-label>
            </div>
          </q-item-section>
        </q-item>
      </q-item-section>
      <q-item-section avatar>
        <AuthAddInternal
          :person="personData"
          @updateMaster="refreshPersonData"
        />
      </q-item-section>
    </q-item>

    <q-item>
      <q-item-section >
        <q-item-label>Update Info</q-item-label>
        <q-item-label caption>Created {{ personData.creationDateTime }}</q-item-label>
        <q-item-label caption>Last Updated {{ personData.lastUpdateDateTime }}</q-item-label>
      </q-item-section>
    </q-item>
  </q-list>

  <q-dialog v-model="editPersonModalDialogVisible">
    <q-layout view="Lhh lpR fff" container class="bg-white" style="width: 700px; max-width: 80vw;">
      <q-header class="bg-primary">
        <q-toolbar>
          <q-toolbar-title>
            Edit {{ personData.guid }} Information
          </q-toolbar-title>
          <q-btn flat v-close-popup round dense icon="close" />
        </q-toolbar>
      </q-header>
      <q-page-container>
        <q-page padding>
          <q-input v-model="editPersonModalDialogData.someTextBoxData" @keyup.enter="okEditPersonDialog" ref="someTextBoxDataInput" label="Unknown" :label-width="3"/> No Editable Fields for Person
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
        </q-page>
      </q-page-container>

    </q-layout>
  </q-dialog>

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
import AuthDisplayInternal from '../components/authDisplayInternal'
import AuthAddInternal from '../components/authAddInternal'

function getEmptyPersonData () {
  return {
  }
}

export default {
  name: 'PageIndex',
  components: {
    UserSelectionModal,
    AuthDisplayInternal,
    AuthAddInternal
  },
  data () {
    var currentURL = new URL(window.location.href)
    return {
      personData: getEmptyPersonData(),
      editPersonModalDialogData: {
        someTextBoxData: '',
        guid: '',
        ObjectVersion: ''
      },
      editPersonModalDialogVisible: false,
      futureRefreshRequested: false,
      curPathPartBeforeHash: currentURL.pathname
    }
  },
  methods: {
    deleteAuth (curAuth) {
      var TTT = this
      TTT.$q.dialog({
        title: 'Confirm',
        message: 'Are you sure you want to remove auth ' + curAuth.AuthUserKey + ' (Tenant ' + curAuth.tenantName + ')',
        ok: {
          push: true,
          label: 'Yes - Delete'
        },
        cancel: {
          push: true,
          label: 'Cancel'
        }
        // preventClose: false,
        // noBackdropDismiss: false,
        // noEscDismiss: false
      }).onOk(() => {
        var base64encodedkey = btoa(curAuth.AuthUserKey)
        var callback = {
          ok: function (response) {
            Notify.create({color: 'positive', message: 'Auth Deleted'})
            TTT.refreshPersonData()
          },
          error: function (error) {
            Notify.create({color: 'negative', message: 'Delete auth failed ( ' + curAuth.AuthUserKey + ') - ' + callbackHelper.getErrorFromResponse(error)})
          }
        }
        TTT.$store.dispatch('globalDataStore/callAdminAPI', {
          path: '/auths/' + base64encodedkey,
          method: 'delete',
          callback: callback,
          curPath: TTT.$router.history.current.path
        })
      })
    },
    supportedAuthType (authType) {
      if (authType === 'internal') {
        return 'internal'
      }
      return 'default'
    },
    _addAuth (userData) {
      var TTT = this
      var callback = {
        ok: function (response) {
          Notify.create({color: 'positive', message: 'Person Auth Added - ' + userData.UserID})
          TTT.futureRefresh()
        },
        error: function (error) {
          Notify.create({color: 'negative', message: 'Add Person auth failed ( ' + userData.UserID + ' - ' + callbackHelper.getErrorFromResponse(error)})
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
        message: 'Are you sure you want to remove user link with ' + userData.UserID,
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
      }).onOk(() => {
        var callback = {
          ok: function (response) {
            Notify.create({color: 'positive', message: 'User Person Link Removed - ' + userData.UserID})
            // TTT.futureRefresh()
            TTT.refreshPersonData()
          },
          error: function (error) {
            Notify.create({color: 'negative', message: 'Remove Person auth failed ( ' + userData.UserID + ' - ' + callbackHelper.getErrorFromResponse(error)})
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
          Notify.create({color: 'positive', message: 'Person Updated'})
          TTT.refreshPersonData()
        },
        error: function (error) {
          Notify.create({color: 'negative', message: 'Update Person failed - ' + callbackHelper.getErrorFromResponse(error)})
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
      this.editPersonModalDialogVisible = true
      this.editPersonModalDialogData.someTextBoxData = ''
      this.editPersonModalDialogData.guid = JSON.parse(JSON.stringify(this.personData.guid))
      this.editPersonModalDialogData.ObjectVersion = JSON.parse(JSON.stringify(this.personData.ObjectVersion))

      if (typeof (this.$refs.someTextBoxDataInput) !== 'undefined') {
        this.$refs.someTextBoxDataInput.focus()
      }
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
      }).onOk(() => {
        var callback = {
          ok: function (response) {
            Notify.create({color: 'positive', message: 'Person ' + personGUID + ' deleted'})
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
  computed: {
    numberOfAssociatedUsers () {
      if (typeof (this.personData) === 'undefined') {
        return 0
      }
      if (typeof (this.personData.associatedUsers) === 'undefined') {
        return 0
      }
      return this.personData.associatedUsers.length
    }
  },
  mounted () {
    this.refreshPersonData()
  }
}
</script>
