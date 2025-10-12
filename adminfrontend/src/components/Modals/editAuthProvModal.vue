<template>
  <q-dialog v-model="editAuthProvModalDialogVisible">
    <q-card style="width: 700px; max-width: 80vw; max-height: 90vh; display: flex; flex-direction: column;">
      <!-- Header -->
      <q-toolbar class="bg-primary text-white">
        <q-toolbar-title v-if="editAuthProvModalDialogData.AddMode">
          Add Auth Provider for {{ tenantData.Name }}
        </q-toolbar-title>
        <q-toolbar-title v-if="!editAuthProvModalDialogData.AddMode">
          Edit {{ editAuthProvModalDialogData.Type }} Auth Provider for {{ tenantData.Name }}
        </q-toolbar-title>
        <q-btn flat v-close-popup round dense icon="close" />
      </q-toolbar>

      <!-- Scrollable Body -->
      <q-card-section style="flex: 1; overflow-y: auto;">
        <q-input v-model="editAuthProvModalDialogData.Type" label="Type" :label-width="3" />

        <q-toggle
          v-model="editAuthProvModalDialogData.AllowUserCreation"
          label="Allow User Creation"
          :label-width="3"
        />
        Must be on for both Tenant and Auth Provider to be effective

        <div class="q-mt-md" />

        <q-toggle
          v-model="editAuthProvModalDialogData.AllowLink"
          label="Allow Link"
          :label-width="3"
        />
        Allow a user to add this auth method

        <div class="q-mt-md" />

        <q-toggle
          v-model="editAuthProvModalDialogData.AllowUnlink"
          label="Allow Unlink"
          :label-width="3"
        />
        Allow a user to remove this auth method (as long as they have at least one other active)

        <div class="q-mt-md" />

        <q-input
          v-model="editAuthProvModalDialogData.LinkText"
          label="Link Text"
          :label-width="3"
          error-message="Must be filled in"
          :error="editAuthProvModalDialogData.LinkText.length === 0"
        />
        Text to show in security settings UI

        <q-input
          v-model="editAuthProvModalDialogData.MenuText"
          label="Menu Text"
          :label-width="3"
          error-message="Must be filled in"
          :error="editAuthProvModalDialogData.MenuText.length === 0"
        />
        Text to display in select auth dialog

        <q-input
          v-model="editAuthProvModalDialogData.IconLink"
          label="Icon Link"
          :label-width="3"
        />
        Link to icon to be used in select auth dialog

        <q-input
          v-model="editAuthProvModalDialogData.ConfigJSON"
          type="textarea"
          label="ConfigJSON"
          :label-width="3"
          :error="isConfigJSONInvalid"
        />
        <div class="editAuthProvModal-confignotesdiv" v-html="configNotes" />
      </q-card-section>

      <!-- Fixed Footer -->
      <q-separator />
      <q-card-actions
        class="bg-grey-2"
        align="right"
        style="position: sticky; bottom: 0; z-index: 1;"
      >
        <q-btn
          @click="okAuthProvTenantDialog(true)"
          v-if="!editAuthProvModalDialogData.AddMode"
          color="negative"
          round
          icon="delete"
          class="q-mr-auto"
        />
        <q-btn
          @click="okAuthProvTenantDialog(false)"
          color="primary"
          label="Ok"
          class="q-ml-xs"
        />
        <q-btn
          @click="this.editAuthProvModalDialogVisible = false"
          label="Cancel"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script>
import { Notify } from 'quasar'
import callbackHelper from '../../callbackHelper'
import saasApiClientCallBackend from '../../saasAPiClientCallBackend'
import { useUserManagementClientStoreStore } from 'stores/saasUserManagementClientStore'

export default {
  name: 'EditAuthProvModal',
  props: [
    'tenantData',
    'tenantName'
  ],
  emits: ['okAuthProvTenantDialog'],
  setup () {
    const userManagementClientStoreStore = useUserManagementClientStoreStore()
    return {
      userManagementClientStoreStore
    }
  },
  data () {
    return {
      editAuthProvModalDialogData: {
        AddMode: false,
        Type: 'internal',
        AllowUserCreation: false,
        AllowLink: false,
        AllowUnlink: false,
        LinkText: '',
        MenuText: '',
        IconLink: '',
        guid: '',
        ConfigJSON: '',
        saltForPasswordHashing: '' // Can never be updated but existing value must always be provided for updates
      },
      editAuthProvModalDialogVisible: false
    }
  },
  computed: {
    isConfigJSONInvalid () {
      try {
        JSON.parse(this.editAuthProvModalDialogData.ConfigJSON)
      } catch (e) {
        return true
      }
      return false
    },
    configNotes () {
      if (this.editAuthProvModalDialogData.Type === 'internal') {
        return '<p>Config type: internal</p><p>Example ConfigJson:</p><pre>{"userSufix": "@internalDataStore"}</pre><p>Notes: Make sure the userSufix is different if using multiple internal auth types. Better still do not use multiple internal auth types</p>'
      }
      if (this.editAuthProvModalDialogData.Type === 'google') {
        return '<p>Config type: google</p><p>Example ConfigJson:</p><pre>{"clientSecretJSONFile": "/run/secrets/saas_user_management_system_authprov_google"}</pre>'
      }
      if (this.editAuthProvModalDialogData.Type === 'facebook') {
        return '<p>Config type: facebook</p><p>Example ConfigJson:</p><pre>{"clientSecretJSONFile": "/run/secrets/saas_user_management_system_authprov_facebook"}</pre>'
      }
      return 'No notes for this config type'
    }
  },
  methods: {
    launchDialogInAddMode () {
      this.editAuthProvModalDialogData.AddMode = true
      this.editAuthProvModalDialogData.Type = 'internal'
      this.editAuthProvModalDialogData.AllowUserCreation = false
      this.editAuthProvModalDialogData.AllowLink = false
      this.editAuthProvModalDialogData.AllowUnlink = false
      this.editAuthProvModalDialogData.LinkText = 'Link'
      this.editAuthProvModalDialogData.MenuText = ''
      this.editAuthProvModalDialogData.IconLink = ''
      this.editAuthProvModalDialogData.guid = ''
      this.editAuthProvModalDialogData.ConfigJSON = ''
      this.editAuthProvModalDialogData.saltForPasswordHashing = ''

      this.editAuthProvModalDialogVisible = true
    },
    launchDialogInEditMode (editAuthProvModalDialogData) {
      this.editAuthProvModalDialogData = editAuthProvModalDialogData
      this.editAuthProvModalDialogData.AddMode = false
      this.editAuthProvModalDialogVisible = true
    },
    okAuthProvTenantDialog (isDeleting) {
      // Shared validation
      if (this.editAuthProvModalDialogData.MenuText === '') {
        Notify.create({ color: 'negative', message: 'Menu text must be filled in' })
        return
      }
      if (this.editAuthProvModalDialogData.LinkText === '') {
        Notify.create({ color: 'negative', message: 'LinkText text must be filled in' })
        return
      }
      // Check configJSON string is valid JSON
      if (this.isConfigJSONInvalid) {
        Notify.create({ color: 'negative', message: 'ConfigJSON is not valid JSON' })
        return
      }
      this.okAuthProvTenantDialogSecondStage({
        isDeleting,
        editAuthProvModalDialogData: this.editAuthProvModalDialogData
      })
    },
    okAuthProvTenantDialogSecondStage ({ isDeleting, editAuthProvModalDialogData }) {
      const TTT = this

      const newTenantJSON = JSON.parse(JSON.stringify(this.tenantData))
      const newAuthProvJSON = {
        Type: editAuthProvModalDialogData.Type,
        AllowUserCreation: editAuthProvModalDialogData.AllowUserCreation,
        AllowLink: editAuthProvModalDialogData.AllowLink,
        AllowUnlink: editAuthProvModalDialogData.AllowUnlink,
        LinkText: editAuthProvModalDialogData.LinkText,
        MenuText: editAuthProvModalDialogData.MenuText,
        IconLink: editAuthProvModalDialogData.IconLink,
        guid: editAuthProvModalDialogData.guid,
        ConfigJSON: editAuthProvModalDialogData.ConfigJSON,
        saltForPasswordHashing: editAuthProvModalDialogData.saltForPasswordHashing
      }
      if (editAuthProvModalDialogData.AddMode) {
        newTenantJSON.AuthProviders.push(newAuthProvJSON)
      } else {
        for (const cur in newTenantJSON.AuthProviders) {
          if (newTenantJSON.AuthProviders[cur].guid === editAuthProvModalDialogData.guid) {
            if (isDeleting) {
              newTenantJSON.AuthProviders.splice(cur, 1)
            } else {
              newTenantJSON.AuthProviders[cur] = newAuthProvJSON
            }
          }
        }
      }
      const callback = {
        ok: function (response) {
          TTT.editAuthProvModalDialogVisible = false
          Notify.create({ color: 'positive', message: 'Tenant Updated' })
          TTT.$emit('okAuthProvTenantDialog', {
            isDeleting,
            editAuthProvModalDialogData: this.editAuthProvModalDialogData
          })
        },
        error: function (error) {
          let verb = 'Update'
          if (editAuthProvModalDialogData.AddMode) {
            verb = 'Add'
          }
          Notify.create({ color: 'negative', message: verb + ' Auth Provider failed - ' + callbackHelper.getErrorFromResponse(error) })
        }
      }
      saasApiClientCallBackend.callApi({
        prefix: 'admin',
        router: this.$router,
        store: this.userManagementClientStoreStore,
        path: '/' + TTT.tenantName + '/tenants/' + newTenantJSON.Name,
        method: 'put',
        postdata: newTenantJSON,
        callback
      })
    }
  }
}
</script>

<style>
.editAuthProvModal-confignotesdiv {
  background-color: aqua
}
</style>
