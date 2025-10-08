<template>
  <q-page>
    <q-page-sticky position="bottom-right" :offset="[50, 50]" class="tenantpage-z-max">
      <q-btn
        color="negative"
        class="fixed"
        round
        @click="deleteTenant"
        icon="delete"
      ></q-btn>
    </q-page-sticky>

  <q-list >
    <q-item clickable v-ripple highlight @click="editTenant">
      <q-item-section >
        <q-item-label>Tenant Name: {{ tenantData.Name }}</q-item-label>
        <q-item-label caption>{{ tenantData.Description }}</q-item-label>
      </q-item-section>
      <q-item-section avatar>
        <q-icon color="primary" name="mode_edit" />
      </q-item-section>
    </q-item>
    <q-item>
      <q-item-section >
        <q-item-label>Allow User Creation:</q-item-label>
        <q-item-label caption v-if="tenantData.AllowUserCreation">✅ New users can sign up</q-item-label>
        <q-item-label caption v-if="!tenantData.AllowUserCreation">❌ Users must be created by admins</q-item-label>
      </q-item-section>
    </q-item>
    <q-item>
      <q-item-section >
        <q-item-label>Origins which client apps will be allowed to collect JWT tokens from:</q-item-label>
        <q-item-label caption><q-chip size="10px" v-for="curVal in tenantData.JWTCollectionAllowedOriginList" :key=curVal>{{ curVal }}</q-chip></q-item-label>
      </q-item-section>
    </q-item>
    <q-item clickable v-ripple highlight @click="viewTicketTypes">
      <q-item-section>
        <q-item-label>Auth Ticket Types</q-item-label>
        <q-item-label caption>
          <q-chip size="10px" v-for="curVal in ticketTypeList" :key=curVal.id  @click="viewTicketType(curVal)">{{ curVal.text }}</q-chip>
        </q-item-label>
      </q-item-section>
      <q-item-section avatar>
        <q-icon color="primary" name="mode_edit" />
      </q-item-section>
    </q-item>
    <q-item>
      <q-item-section >
        <q-item-label>Ticket Override URL:</q-item-label>
        <q-item-label caption v-if="tenantData.TicketOverrideURL === ''">None Set</q-item-label>
        <q-item-label caption v-if="tenantData.TicketOverrideURL !== ''">
          <a :href="tenantData.TicketOverrideURL">{{ tenantData.TicketOverrideURL }}</a>
        </q-item-label>
      </q-item-section>
    </q-item>
    <q-item>
      <q-item-section >
        <q-item-label>Tennant Banner HTML:</q-item-label>
        <q-item-label>
          <div v-html="tenantData.TenantBannerHTML" />
        </q-item-label>
      </q-item-section>
    </q-item>
    <q-item>
      <q-item-section >
        <q-item-label>Select Auth Message:</q-item-label>
        <q-item-label>
          {{ tenantData.SelectAuthMessage }}
        </q-item-label>
      </q-item-section>
    </q-item>
  </q-list>

  <q-table
    title='Auth Providers'
    :rows="tenantData.AuthProviders"
    :columns="tableColumns"
    row-key="name"
  >
    <template v-slot:body-cell-...="props">
      <q-td :props="props">
          <q-btn flat color="primary" icon="mode_edit" label="" @click="editAuthProv(props.row)" />
      </q-td>
    </template>
  </q-table>
  <q-btn
    @click="addAuthProv"
    color="primary"
    label="Add Auth Provider"
    class = "float-left q-ma-xs"
  />
  <q-dialog v-model="editTenantModalDialogVisible">
    <q-card style="width: 700px; max-width: 80vw; max-height: 90vh; display: flex; flex-direction: column;">
      <!-- Header -->
      <q-toolbar class="bg-primary text-white">
        <q-toolbar-title>
          Edit Tenant Information
        </q-toolbar-title>
        <q-btn flat v-close-popup round dense icon="close" />
      </q-toolbar>

      <!-- Scrollable body -->
      <q-card-section style="flex: 1; overflow-y: auto;">
        <q-input
          v-model="editTenantModalDialogData.Description"
          @keyup.enter="okEditTenantDialog"
          ref="descriptionInput"
          label="Description"
          :label-width="3"
        />
        Description of Tenant

        <q-field
          helper="Must be on for both Tenant and Auth Provider to be effective"
          label="Allow User Creation"
          :label-width="3"
        >
          <q-toggle v-model="editTenantModalDialogData.AllowUserCreation" />
        </q-field>

        <q-select
          label="JWT Collection Allowed Origin List"
          v-model="editTenantModalDialogData.JWTCollectionAllowedOriginList"
          use-input
          use-chips
          multiple
          input-debounce="0"
          @new-value="dialogEditJWTCollectionAllowedOriginListCreateValue"
        />
        Origins which client apps will be allowed to collect JWT tokens from

        <q-input
          v-model="editTenantModalDialogData.TicketOverrideURL"
          ref="TicketOverrideURLInput"
          label="Tenant specific ticket endpoint"
          :label-width="3"
          clearable
        />
        Ticket Override URL

        <q-input
          v-model="editTenantModalDialogData.TenantBannerHTML"
          ref="TenantBannerHTMLInput"
          label="Tenant banner displayed at login"
          :label-width="3"
          clearable
        />
        Tenant Banner HTML

        <q-input
          v-model="editTenantModalDialogData.SelectAuthMessage"
          ref="SelectAuthMessageInput"
          label="Select Auth message to use"
          :label-width="3"
          clearable
        />
        Select Auth Message
      </q-card-section>

      <!-- Fixed footer -->
      <q-separator />
      <q-card-actions
        align="right"
        class="bg-grey-2"
        style="position: sticky; bottom: 0; z-index: 1;"
      >
        <q-btn
          @click="okEditTenantDialog"
          color="primary"
          label="Ok"
          class="q-ml-xs"
        />
        <q-btn
          @click="editTenantModalDialogVisible = false"
          label="Cancel"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
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
        Auth Provider Specific Config
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

  </q-page>
</template>

<script>
import { useGlobalValsStore } from 'stores/globalValsStore'
import { Notify, Loading } from 'quasar'
import callbackHelper from '../callbackHelper'
import saasApiClientCallBackend from '../saasAPiClientCallBackend'
import { useUserManagementClientStoreStore } from 'stores/saasUserManagementClientStore'

function getEmptyTenantData () {
  return {
    AuthProviders: []
  }
}
function getEmptyTicketTypeData () {
  return {
    pagination: {
      total: 999
    },
    result: []
  }
}

export default {
  name: 'PageTenant',
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
  data () {
    return {
      tenantData: getEmptyTenantData(),
      ticketTypeData: getEmptyTicketTypeData(),
      tableColumns: [
        { name: 'Type', required: true, label: 'Type', align: 'left', field: 'Type', sortable: true, filter: false },
        { name: 'AllowUserCreation', required: true, label: 'AllowUserCreation', align: 'left', field: 'AllowUserCreation', sortable: true, filter: false },
        { name: 'AllowLink', required: true, label: 'AllowLink', align: 'left', field: 'AllowLink', sortable: true, filter: false },
        { name: 'AllowUnlink', required: true, label: 'AllowUnlink', align: 'left', field: 'AllowUnlink', sortable: true, filter: false },
        { name: 'LinkText', required: true, label: 'LinkText', align: 'left', field: 'LinkText', sortable: true, filter: false },
        { name: 'MenuText', required: true, label: 'MenuText', align: 'left', field: 'MenuText', sortable: true, filter: false },
        { name: 'IconLink', required: true, label: 'IconLink', align: 'left', field: 'IconLink', sortable: true, filter: false },
        { name: '...', required: true, label: '', align: 'left', field: 'guid', sortable: false, filter: false }
        // guid not in table
        // ConfigJSON not in table
      ],
      editTenantModalDialogData: {
        Description: '',
        AllowUserCreation: false,
        JWTCollectionAllowedOriginList: [],
        TicketOverrideURL: ''
      },
      editTenantModalDialogVisible: false,
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
  methods: {
    dialogEditJWTCollectionAllowedOriginListCreateValue (val, done) {
      if (val.length < 3) {
        Notify.create({ color: 'negative', message: 'Must have at least 3 characters' })
        return
      }
      done(val, 'add-unique')
    },
    addAuthProv () {
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
    deleteTenant () {
      const TTT = this
      const nameOfTenantToDelete = TTT.tenantData.Name
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
      }).onOk(() => {
        const callback = {
          ok: function (response) {
            Notify.create({ color: 'positive', message: 'Tenant ' + nameOfTenantToDelete + ' deleted' })
            TTT.$router.push('/' + TTT.$route.params.tenantName + '/tenants/')
          },
          error: function (error) {
            Notify.create({ color: 'negative', message: 'Delete Tenant failed - ' + callbackHelper.getErrorFromResponse(error) })
          }
        }
        saasApiClientCallBackend.callApi({
          prefix: 'admin',
          router: this.$router,
          store: this.userManagementClientStoreStore,
          path: '/' + TTT.tenantName + '/tenants/' + nameOfTenantToDelete,
          method: 'delete',
          postdata: null,
          callback,
          extraHeaders: { 'object-version-id': TTT.tenantData.ObjectVersion }
        })
      })
    },
    editTenant () {
      this.editTenantModalDialogData.Description = this.tenantData.Description
      this.editTenantModalDialogData.AllowUserCreation = this.tenantData.AllowUserCreation
      this.editTenantModalDialogData.JWTCollectionAllowedOriginList = this.tenantData.JWTCollectionAllowedOriginList
      this.editTenantModalDialogData.TicketOverrideURL = this.tenantData.TicketOverrideURL
      this.editTenantModalDialogData.TenantBannerHTML = this.tenantData.TenantBannerHTML
      this.editTenantModalDialogData.SelectAuthMessage = this.tenantData.SelectAuthMessage

      this.editTenantModalDialogVisible = true
      const TTT = this
      setTimeout(function () {
        TTT.$refs.descriptionInput.focus()
      }, 5)
    },
    okEditTenantDialog () {
      const TTT = this
      this.editTenantModalDialogVisible = false
      if (this.editTenantModalDialogData.Description === this.tenantData.Description) {
        if (this.editTenantModalDialogData.AllowUserCreation === this.tenantData.AllowUserCreation) {
          if (this.editTenantModalDialogData.JWTCollectionAllowedOriginList === this.tenantData.JWTCollectionAllowedOriginList) {
            if (this.editTenantModalDialogData.TicketOverrideURL === this.tenantData.TicketOverrideURL) {
              if (this.editTenantModalDialogData.TenantBannerHTML === this.tenantData.TenantBannerHTML) {
                if (this.editTenantModalDialogData.SelectAuthMessage === this.tenantData.SelectAuthMessage) {
                  Notify.create({ color: 'positive', message: 'No changes made' })
                  return // no change so do nothing
                }
              }
            }
          }
        }
      }
      const newTenantJSON = JSON.parse(JSON.stringify(this.tenantData))
      newTenantJSON.Description = this.editTenantModalDialogData.Description
      newTenantJSON.AllowUserCreation = this.editTenantModalDialogData.AllowUserCreation
      newTenantJSON.JWTCollectionAllowedOriginList = this.editTenantModalDialogData.JWTCollectionAllowedOriginList
      newTenantJSON.TicketOverrideURL = this.editTenantModalDialogData.TicketOverrideURL
      newTenantJSON.TenantBannerHTML = this.editTenantModalDialogData.TenantBannerHTML
      newTenantJSON.SelectAuthMessage = this.editTenantModalDialogData.SelectAuthMessage

      const callback = {
        ok: function (response) {
          Notify.create({ color: 'positive', message: 'Tenant Updated' })
          TTT.refreshTenantData()
        },
        error: function (error) {
          Notify.create({ color: 'negative', message: 'Update Tenant failed - ' + callbackHelper.getErrorFromResponse(error) })
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
    },
    okAuthProvTenantDialog (isDeleting) {
      const TTT = this

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
      const newTenantJSON = JSON.parse(JSON.stringify(this.tenantData))
      const newAuthProvJSON = {
        Type: TTT.editAuthProvModalDialogData.Type,
        AllowUserCreation: TTT.editAuthProvModalDialogData.AllowUserCreation,
        AllowLink: TTT.editAuthProvModalDialogData.AllowLink,
        AllowUnlink: TTT.editAuthProvModalDialogData.AllowUnlink,
        LinkText: TTT.editAuthProvModalDialogData.LinkText,
        MenuText: TTT.editAuthProvModalDialogData.MenuText,
        IconLink: TTT.editAuthProvModalDialogData.IconLink,
        guid: TTT.editAuthProvModalDialogData.guid,
        ConfigJSON: TTT.editAuthProvModalDialogData.ConfigJSON,
        saltForPasswordHashing: TTT.editAuthProvModalDialogData.saltForPasswordHashing
      }
      if (this.editAuthProvModalDialogData.AddMode) {
        newTenantJSON.AuthProviders.push(newAuthProvJSON)
      } else {
        for (const cur in newTenantJSON.AuthProviders) {
          if (newTenantJSON.AuthProviders[cur].guid === TTT.editAuthProvModalDialogData.guid) {
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
          TTT.refreshTenantData()
        },
        error: function (error) {
          let verb = 'Update'
          if (TTT.editAuthProvModalDialogData.AddMode) {
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
    },
    viewTicketTypes () {
      this.$router.push('/' + this.$route.params.tenantName + '/tenants/' + this.$route.params.selTenantNAME + '/tickettypes')
    },
    editAuthProv (item) {
      this.editAuthProvModalDialogData.AddMode = false
      this.editAuthProvModalDialogData.Type = item.Type
      this.editAuthProvModalDialogData.AllowUserCreation = item.AllowUserCreation
      this.editAuthProvModalDialogData.AllowLink = item.AllowLink
      this.editAuthProvModalDialogData.AllowUnlink = item.AllowUnlink
      this.editAuthProvModalDialogData.LinkText = item.LinkText
      this.editAuthProvModalDialogData.MenuText = item.MenuText
      this.editAuthProvModalDialogData.IconLink = item.IconLink
      this.editAuthProvModalDialogData.guid = item.guid
      this.editAuthProvModalDialogData.ConfigJSON = item.ConfigJSON
      this.editAuthProvModalDialogData.saltForPasswordHashing = item.saltForPasswordHashing

      this.editAuthProvModalDialogVisible = true
    },
    refreshTenantData () {
      const jobNameToLoad = this.$route.params.selTenantNAME
      const TTT = this
      const callback = {
        ok: function (response) {
          TTT.tenantData = response.data
          TTT.refreshTicketTypeData()
        },
        error: function (error) {
          TTT.globalValsStore.pageTitle = 'Tenant ERROR'
          Loading.hide()
          Notify.create({ color: 'negative', message: 'Tenant query failed - ' + callbackHelper.getErrorFromResponse(error) })
          TTT.tenantData = getEmptyTenantData()
        }
      }
      TTT.globalValsStore.pageTitle = 'Tenant Loading'
      Loading.show()
      saasApiClientCallBackend.callApi({
        prefix: 'admin',
        router: this.$router,
        store: this.userManagementClientStoreStore,
        path: '/' + TTT.tenantName + '/tenants/' + jobNameToLoad,
        method: 'get',
        postdata: undefined,
        callback
      })
    },
    refreshTicketTypeData () {
      const TTT = this
      const callback = {
        ok: function (response) {
          TTT.ticketTypeData = response.data
          TTT.globalValsStore.pageTitle = 'Tenant ' + TTT.tenantData.Name
          Loading.hide()
        },
        error: function (error) {
          TTT.globalValsStore.pageTitle = 'Tenant ERROR'
          Loading.hide()
          Notify.create({ color: 'negative', message: 'Ticket Type query failed - ' + callbackHelper.getErrorFromResponse(error) })
          TTT.ticketTypeData = getEmptyTicketTypeData()
        }
      }
      TTT.globalValsStore.pageTitle = 'Tenant Loading'
      Loading.show()
      saasApiClientCallBackend.callApi({
        prefix: 'admin',
        router: this.$router,
        store: this.userManagementClientStoreStore,
        path: '/' + TTT.tenantName + '/tenants/' + this.$route.params.selTenantNAME + '/tickettypes?pagesize=5',
        method: 'get',
        postdata: undefined,
        callback
      })
    }
  },
  computed: {
    tenantName () {
      return this.$route.params.tenantName
    },
    isConfigJSONInvalid () {
      try {
        JSON.parse(this.editAuthProvModalDialogData.ConfigJSON)
      } catch (e) {
        return true
      }
      return false
    },
    ticketTypeList () {
      const ret = []
      this.ticketTypeData.result.forEach(function (resItem) {
        ret.push({ id: resItem.id, text: resItem.ticketTypeName })
      })
      if (this.ticketTypeData.pagination.total > this.ticketTypeData.result.length) {
        ret.push({ id: undefined, text: '...' })
      }
      return ret
    }
  },
  mounted () {
    this.refreshTenantData()
  }
}
</script>

<style>
.tenantpage-z-max {
  z-index: 3000; /* higher than q-table's content */
}
</style>
