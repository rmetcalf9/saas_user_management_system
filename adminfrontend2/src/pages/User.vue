<template>
  <q-page>
    <q-page-sticky position="bottom-right" :offset="[50, 50]" class="userpage-z-max">
      <q-btn
        color="negative"
        class="fixed"
        round
        @click="deleteUser"
        icon="delete"
      ></q-btn>
    </q-page-sticky>
  <q-list >
    <q-item clickable v-ripple highlight @click="editUser">
      <q-item-section >
        <q-item-label>User ID: {{ userData.UserID }}</q-item-label>
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
        <q-item-label>Linked Person Records ({{ associatedPersonGUIDLength }})</q-item-label>
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
  <q-dialog v-model="editUserModalDialogVisible">
    <q-card style="width: 700px; max-width: 80vw; max-height: 90vh; display: flex; flex-direction: column;">
      <!-- Header -->
      <q-toolbar class="bg-primary text-white">
        <q-toolbar-title>
          Edit {{ userData.UserID }} Information
        </q-toolbar-title>
        <q-btn flat v-close-popup round dense icon="close" />
      </q-toolbar>

      <!-- Scrollable Body -->
      <q-card-section style="flex: 1; overflow-y: auto;">
        <q-input
          v-model="editUserModalDialogData.known_as"
          @keyup.enter="okEditUserDialog"
          ref="knownAsInput"
          label="Known As"
          :label-width="3"
        />
        <div class="text-caption text-grey q-mb-md">
          Displayed to user in UI
        </div>

        <q-input
          v-model="editUserModalDialogData.other_data"
          type="textarea"
          label="Other Data"
          :label-width="3"
          :error="isOtherDataInvalid"
        />
        <div class="text-caption text-grey q-mb-md">
          Other information about the user (JSON)
        </div>

        <div
          v-for="curRole in editUserModalDialogData.TenantRoles"
          :key="curRole.TenantName"
          class="q-mb-md"
        >
          <div class="text-subtitle1 q-mb-xs">
            Roles for {{ curRole.TenantName }}:
          </div>
          <q-select
            v-model="curRole.ThisTenantRoles"
            use-input
            use-chips
            multiple
            input-debounce="0"
            @new-value="dialogTenantRoleCreateValue"
          />
        </div>

        <q-btn
          @click="addTenantToEditUserDialog"
          color="positive"
          icon="add_to_queue"
          round
          class="q-ml-xs"
        />
      </q-card-section>

      <!-- Footer -->
      <q-separator />
      <q-card-actions
        align="right"
        class="bg-grey-2"
        style="position: sticky; bottom: 0; z-index: 1;"
      >
        <q-btn
          @click="okEditUserDialog"
          color="primary"
          label="Ok"
          class="q-ml-xs"
        />
        <q-btn
          @click="editUserModalDialogVisible = false"
          label="Cancel"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>

  </q-page>
</template>

<script>
import { useGlobalValsStore } from 'stores/globalValsStore'
import { Notify, Loading } from 'quasar'
import callbackHelper from '../callbackHelper'
import saasApiClientCallBackend from '../saasAPiClientCallBackend'
import { useUserManagementClientStoreStore } from 'stores/saasUserManagementClientStore'

function getEmptyUserData () {
  return {
  }
}

export default {
  name: 'PageUser',
  data () {
    const currentURL = new URL(window.location.href)
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
  components: {
  },
  setup () {
    const globalValsStore = useGlobalValsStore()
    const userManagementClientStoreStore = useUserManagementClientStoreStore()
    return {
      globalValsStore,
      userManagementClientStoreStore
    }
  },
  computed: {
    tenantName () {
      return this.$route.params.tenantName
    },
    associatedPersonGUIDLength () {
      if (typeof (this.userData.associatedPersonGUIDs) === 'undefined') {
        return 0
      }
      return this.userData.associatedPersonGUIDs.length
    },
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
    deleteUser () {
      const TTT = this
      const userID = TTT.userData.UserID
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
        const callback = {
          ok: function (response) {
            Notify.create({ color: 'positive', message: 'User ' + userID + ' deleted' })
            TTT.$router.push('/' + TTT.$route.params.tenantName + '/users/')
          },
          error: function (error) {
            Notify.create('Delete User failed - ' + callbackHelper.getErrorFromResponse(error))
          }
        }
        saasApiClientCallBackend.callApi({
          prefix: 'admin',
          router: this.$router,
          store: this.userManagementClientStoreStore,
          path: '/' + TTT.tenantName + '/users/' + userID,
          method: 'delete',
          postdata: undefined,
          callback,
          extraHeaders: { 'object-version-id': TTT.userData.ObjectVersion }
        })
      })
    },
    editUser () {
      this.editUserModalDialogData.known_as = JSON.parse(JSON.stringify(this.userData.known_as))
      this.editUserModalDialogData.other_data = JSON.stringify(this.userData.other_data)
      this.editUserModalDialogData.TenantRoles = JSON.parse(JSON.stringify(this.userData.TenantRoles))
      this.editUserModalDialogVisible = true
      const TTT = this
      setTimeout(function (x) {
        TTT.$refs.knownAsInput.focus()
      }, 5)
    },
    addTenantToEditUserDialog () {
      const TTT = this
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
        if (data.length < 3) {
          Notify.create({ color: 'negative', message: 'Must have at least 3 chars' })
          return
        }
        for (const curRole in TTT.editUserModalDialogData.TenantRoles) {
          if (TTT.editUserModalDialogData.TenantRoles[curRole].TenantName === data) {
            Notify.create({ color: 'negative', message: 'Already exists' })
            return
          }
        }
        TTT.editUserModalDialogData.TenantRoles.push({ TenantName: data, ThisTenantRoles: ['hasaccount'] })
        TTT.editUserModalDialogData.TenantRoles.sort()
      })
    },
    dialogTenantRoleCreateValue (val, done) {
      if (val.length < 3) {
        Notify.create({ color: 'negative', message: 'Must have at least 3 characters' })
        return
      }
      done(val, 'add-unique')
    },
    okEditUserDialog () {
      const TTT = this
      if (this.isOtherDataInvalid) {
        Notify.create({ color: 'negative', message: 'Other JSON must be valid JSON' })
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
      const newUserJSON = JSON.parse(JSON.stringify(this.userData))
      newUserJSON.known_as = this.editUserModalDialogData.known_as
      newUserJSON.other_data = JSON.parse(this.editUserModalDialogData.other_data)
      newUserJSON.TenantRoles = []
      for (const curRole in this.editUserModalDialogData.TenantRoles) {
        if (this.editUserModalDialogData.TenantRoles[curRole].ThisTenantRoles.length !== 0) {
          newUserJSON.TenantRoles.push(this.editUserModalDialogData.TenantRoles[curRole])
        }
      }

      const callback = {
        ok: function (response) {
          Notify.create({ color: 'positive', message: 'User Updated' })
          TTT.refreshUserData()
        },
        error: function (error) {
          Notify.create('Update User failed - ' + callbackHelper.getErrorFromResponse(error))
        }
      }
      saasApiClientCallBackend.callApi({
        prefix: 'admin',
        router: this.$router,
        store: this.userManagementClientStoreStore,
        path: '/' + TTT.tenantName + '/users/' + newUserJSON.UserID,
        method: 'put',
        postdata: newUserJSON,
        callback,
        extraHeaders: { 'object-version-id': newUserJSON.ObjectVersion }
      })
    },
    refreshUserData () {
      const userIDToLoad = this.$route.params.selUserID
      const TTT = this
      const callback = {
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
      saasApiClientCallBackend.callApi({
        prefix: 'admin',
        router: this.$router,
        store: this.userManagementClientStoreStore,
        path: '/' + TTT.tenantName + '/users/' + userIDToLoad,
        method: 'get',
        postdata: undefined,
        callback
      })
    }
  },
  mounted () {
    this.refreshUserData()
  }
}
</script>

<style>
.userpage-z-max {
  z-index: 3000;
}
</style>
