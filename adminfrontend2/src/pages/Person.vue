<template>
<q-page>
  <q-page-sticky position="bottom-right" :offset="[50, 50]" class="personpage-z-max">
    <q-btn
      color="negative"
      class="fixed"
      round
      @click="deletePerson"
      icon="delete"
    ></q-btn>
  </q-page-sticky>
<q-list >
  <q-item clickable v-ripple highlight @click="editPerson">
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
  <q-card style="width: 700px; max-width: 80vw; max-height: 90vh; display: flex; flex-direction: column;">
    <!-- Header -->
    <q-toolbar class="bg-primary text-white">
      <q-toolbar-title>
        Edit {{ personData.guid }} Information
      </q-toolbar-title>
      <q-btn flat v-close-popup round dense icon="close" />
    </q-toolbar>

    <!-- Scrollable Body -->
    <q-card-section style="flex: 1; overflow-y: auto;">
      <q-input
        v-model="editPersonModalDialogData.someTextBoxData"
        @keyup.enter="okEditPersonDialog"
        ref="someTextBoxDataInput"
        label="Unknown"
        :label-width="3"
      />
      <div class="text-caption text-grey q-mt-sm">
        No Editable Fields for Person
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
        @click="okEditPersonDialog"
        color="primary"
        label="Ok"
        class="q-ml-xs"
      />
      <q-btn
        @click="editPersonModalDialogVisible = false"
        label="Cancel"
      />
    </q-card-actions>
  </q-card>
</q-dialog>
  <UserSelectionModal
    ref="UserSelectionModal"
    :title="'Select User to Associate with person ' + personData.guid"
    @ok="associateWithUserBtnClickSelectUserOK"
  />
</q-page>
</template>

<script>
import { Notify, Loading } from 'quasar'
import callbackHelper from '../callbackHelper'
import saasApiClientCallBackend from '../saasAPiClientCallBackend'
import { useUserManagementClientStoreStore } from 'stores/saasUserManagementClientStore'
import UserSelectionModal from '../components/UserSelectionModal'
import AuthDisplayInternal from '../components/PersonDisplay/authDisplayInternal'
import AuthAddInternal from '../components/PersonDisplay/authAddInternal'

function getEmptyPersonData () {
  return {
  }
}

export default {
  name: 'PagePerson',
  components: {
    AuthDisplayInternal,
    AuthAddInternal,
    UserSelectionModal
  },
  setup () {
    const userManagementClientStoreStore = useUserManagementClientStoreStore()
    return {
      userManagementClientStoreStore
    }
  },
  data () {
    const currentURL = new URL(window.location.href)
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
  computed: {
    tenantName () {
      return this.$route.params.tenantName
    },
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
  methods: {
    deletePerson () {
      const TTT = this
      const personGUID = TTT.personData.guid
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
        const callback = {
          ok: function (response) {
            Notify.create({ color: 'positive', message: 'Person ' + personGUID + ' deleted' })
            TTT.$router.push('/' + TTT.$route.params.tenantName + '/persons/')
          },
          error: function (error) {
            Notify.create('Delete Person failed - ' + callbackHelper.getErrorFromResponse(error))
          }
        }
        saasApiClientCallBackend.callApi({
          prefix: 'admin',
          router: this.$router,
          store: this.userManagementClientStoreStore,
          path: '/' + TTT.tenantName + '/persons/' + personGUID,
          method: 'delete',
          postdata: null,
          callback,
          extraHeaders: { 'object-version-id': TTT.personData.ObjectVersion }
        })
      })
    },
    editPerson () {
      this.editPersonModalDialogVisible = true
      this.editPersonModalDialogData.someTextBoxData = ''
      this.editPersonModalDialogData.guid = JSON.parse(JSON.stringify(this.personData.guid))
      this.editPersonModalDialogData.ObjectVersion = JSON.parse(JSON.stringify(this.personData.ObjectVersion))
      const TTT = this
      setTimeout(function () {
        TTT.$refs.someTextBoxDataInput.focus()
      }, 5)
    },
    okEditPersonDialog () {
      const TTT = this
      this.editPersonModalDialogVisible = false
      if (this.editPersonModalDialogData.guid === this.personData.guid) {
        // return // no change so do nothing
        console.log('Overridden no change check')
      }
      const newPersonJSON = {
        guid: this.editPersonModalDialogData.guid,
        ObjectVersion: this.editPersonModalDialogData.ObjectVersion
      }

      const callback = {
        ok: function (response) {
          Notify.create({ color: 'positive', message: 'Person Updated' })
          TTT.refreshPersonData()
        },
        error: function (error) {
          Notify.create({ color: 'negative', message: 'Update Person failed - ' + callbackHelper.getErrorFromResponse(error) })
        }
      }
      saasApiClientCallBackend.callApi({
        prefix: 'admin',
        router: this.$router,
        store: this.userManagementClientStoreStore,
        path: '/' + TTT.tenantName + '/persons/' + newPersonJSON.guid,
        method: 'put',
        postdata: newPersonJSON,
        callback
      })
    },
    associateWithUserBtnClick () {
      this.$refs.UserSelectionModal.launchDialog()
    },
    associateWithUserBtnClickSelectUserOK (response) {
      const TTT = this
      for (const x in response.selectedUserList) {
        TTT._addAuth(response.selectedUserList[x])
      }
    },
    _addAuth (userData) {
      const TTT = this
      const callback = {
        ok: function (response) {
          Notify.create({ color: 'positive', message: 'Person Auth Added - ' + userData.UserID })
          TTT.futureRefresh()
        },
        error: function (error) {
          Notify.create({ color: 'negative', message: 'Add Person auth failed ( ' + userData.UserID + ' - ' + callbackHelper.getErrorFromResponse(error) })
        }
      }
      saasApiClientCallBackend.callApi({
        prefix: 'admin',
        router: this.$router,
        store: this.userManagementClientStoreStore,
        path: '/' + TTT.tenantName + '/userpersonlinks/' + userData.UserID + '/' + TTT.personData.guid,
        method: 'post',
        postdata: {
          UserID: userData.UserID,
          personGUID: TTT.personData.guid
        },
        callback
      })
    },
    unassociateWithUserBtnClick (userData) {
      const TTT = this
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
        const callback = {
          ok: function (response) {
            Notify.create({ color: 'positive', message: 'User Person Link Removed - ' + userData.UserID })
            // TTT.futureRefresh()
            TTT.refreshPersonData()
          },
          error: function (error) {
            Notify.create({ color: 'negative', message: 'Remove Person auth failed ( ' + userData.UserID + ' - ' + callbackHelper.getErrorFromResponse(error) })
          }
        }
        saasApiClientCallBackend.callApi({
          prefix: 'admin',
          router: this.$router,
          store: this.userManagementClientStoreStore,
          path: '/' + TTT.tenantName + '/userpersonlinks/' + userData.UserID + '/' + TTT.personData.guid,
          method: 'delete',
          postdata: null,
          callback
        })
      })
    },
    deleteAuth (curAuth) {
      const TTT = this
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
        const base64encodedkey = btoa(curAuth.AuthUserKey)
        const callback = {
          ok: function (response) {
            Notify.create({ color: 'positive', message: 'Auth Deleted' })
            TTT.refreshPersonData()
          },
          error: function (error) {
            Notify.create({ color: 'negative', message: 'Delete auth failed ( ' + curAuth.AuthUserKey + ') - ' + callbackHelper.getErrorFromResponse(error) })
          }
        }
        saasApiClientCallBackend.callApi({
          prefix: 'admin',
          router: this.$router,
          store: this.userManagementClientStoreStore,
          path: '/' + TTT.tenantName + '/auths/' + base64encodedkey,
          method: 'delete',
          postdata: null,
          callback
        })
      })
    },
    supportedAuthType (authType) {
      if (authType === 'internal') {
        return 'internal'
      }
      return 'default'
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
      const personIDToLoad = this.$route.params.selPerGUID
      const TTT = this
      const callback = {
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
      saasApiClientCallBackend.callApi({
        prefix: 'admin',
        router: this.$router,
        store: this.userManagementClientStoreStore,
        path: '/' + TTT.tenantName + '/persons/' + personIDToLoad,
        method: 'get',
        postdata: null,
        callback
      })
    }
  },
  mounted () {
    this.refreshPersonData()
  }
}
</script>

<style>
.personpage-z-max {
  z-index: 3000;
}
</style>
