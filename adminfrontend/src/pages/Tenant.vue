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
    <q-item clickable v-ripple highlight @click.native="editTenant">
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
        <q-item-label caption v-if="tenantData.AllowUserCreation">New users can sign up</q-item-label>
        <q-item-label caption v-if="!tenantData.AllowUserCreation">Users must be created by admins</q-item-label>
      </q-item-section>
    </q-item>
    <q-item>
      <q-item-section >
        <q-item-label>Origins which client apps will be allowed to collect JWT tokens from:</q-item-label>
        <q-item-label caption><q-chip size="10px" v-for="curVal in tenantData.JWTCollectionAllowedOriginList" :key=curVal>{{ curVal }}</q-chip></q-item-label>
      </q-item-section>
    </q-item>
    <q-item clickable v-ripple highlight @click.native="viewTicketTypes">
      <q-item-section>
        <q-item-label>Auth Ticket Types</q-item-label>
        <q-item-label caption>
          <q-chip size="10px" v-for="curVal in ticketTypeList" :key=curVal.id  @click.native="viewTicketType(curVal)">{{ curVal.text }}</q-chip>
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

<q-dialog v-model="editTenantModalDialogVisible">
  <q-layout view="Lhh lpR fff" container class="bg-white" style="height: 450px; width: 700px; max-width: 80vw;">
    <q-header class="bg-primary">
      <q-toolbar>
        <q-toolbar-title>
          Edit Tenant Information
        </q-toolbar-title>
        <q-btn flat v-close-popup round dense icon="close" />
      </q-toolbar>
    </q-header>
    <q-page-container>
      <q-page padding>
        <q-input v-model="editTenantModalDialogData.Description" @keyup.enter="okEditTenantDialog" ref="descriptionInput" label="Description" :label-width="3"/> Description of Tenant
        <q-field helper="Must be on for both Tenant and Auth Provider to be effective" label="Allow User Creation" :label-width="3">
          <q-toggle v-model="editTenantModalDialogData.AllowUserCreation" />
        </q-field> Must be on for both Tenant and Auth Provider to be effective
        <q-select
          label="JWT Collection Allowed Origin List"
          v-model="editTenantModalDialogData.JWTCollectionAllowedOriginList"
          use-input
          use-chips
          multiple
          input-debounce="0"
          @new-value="dialogEditJWTCollectionAllowedOriginListCreateValue"
        /> Origins which client apps will be allowed to collect JWT tokens from
        <q-input v-model="editTenantModalDialogData.TicketOverrideURL" ref="TicketOverrideURLInput" label="Tenant spercific ticket endpoint" :label-width="3" clearable />Ticket Override URL
        <q-input v-model="editTenantModalDialogData.TenantBannerHTML" ref="TenantBannerHTMLInput" label="Tenant banner displayed at login" :label-width="3" clearable />Tenant Banner HTML
        <q-input v-model="editTenantModalDialogData.SelectAuthMessage" ref="SelectAuthMessageInput" label="Select Auth message to use" :label-width="3" clearable />Select Auth Message

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
      </q-page>
    </q-page-container>
  </q-layout>
</q-dialog>

<q-dialog v-model="editAuthProvModalDialogVisible">
  <q-layout view="Lhh lpR fff" container class="bg-white" style="width: 700px; max-width: 80vw;">
    <q-header class="bg-primary">
      <q-toolbar>
        <q-toolbar-title v-if="editAuthProvModalDialogData.AddMode">
          Add Auth Provider for {{ tenantData.Name }}
        </q-toolbar-title>
        <q-toolbar-title v-if="!editAuthProvModalDialogData.AddMode">
          Edit {{ editAuthProvModalDialogData.Type }} Auth Provider for {{ tenantData.Name }}
        </q-toolbar-title>
        <q-btn flat v-close-popup round dense icon="close" />
      </q-toolbar>
    </q-header>
    <q-page-container>
      <q-page padding>
        <q-input v-model="editAuthProvModalDialogData.Type" label="Type" :label-width="3"/>
        <q-toggle v-model="editAuthProvModalDialogData.AllowUserCreation" label="Allow User Creation" :label-width="3"/> Must be on for both Tenant and Auth Provider to be effective
        <div>&nbsp;</div>
        <q-toggle v-model="editAuthProvModalDialogData.AllowLink" label="Allow Link" :label-width="3"/> Allow a user to add this auth method
        <div>&nbsp;</div>
        <q-toggle v-model="editAuthProvModalDialogData.AllowUnlink" label="Allow Unlink" :label-width="3"/> Allow a user to remove this auth method (As long as they have at least one other active)
        <div>&nbsp;</div>
        <q-input
          v-model="editAuthProvModalDialogData.LinkText"
          label="Link Text"
          :label-width="3"
          error-message="Must be filled in"
          :error="editAuthProvModalDialogData.LinkText.length === 0"
        /> Text to show in security settings UI
        <q-input
          v-model="editAuthProvModalDialogData.MenuText"
          label="Menu Text"
          :label-width="3"
          error-message="Must be filled in"
          :error="editAuthProvModalDialogData.MenuText.length === 0"
        /> Text to display in select auth dialog
        <q-input
          v-model="editAuthProvModalDialogData.IconLink"
          label="Icon Link"
          :label-width="3"
        /> Link to icon to be used in select auth dialog
        <q-input
          v-model="editAuthProvModalDialogData.ConfigJSON"
          type="textarea"
          label="ConfigJSON"
          :label-width="3"
          :error="isConfigJSONInvalid"
        /> Auth Prov Spercific Config
        <div>&nbsp;</div>
        <q-btn
          @click="deleteAuthProvTenantDialog"
          color="negative"
          round
          icon="delete"
          class = "float-left q-ml-xs"
        />
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
      </q-page>
    </q-page-container>
  </q-layout>
</q-dialog>
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
function getEmptyTicketTypeData () {
  return {
    pagination: {
      total: 999
    },
    result: []
  }
}

export default {
  name: 'PageIndex',
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
        DeleteMode: false,
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
    ticketTypeList () {
      var ret = []
      this.ticketTypeData.result.map(function (resItem) {
        ret.push({ id: resItem.id, text: resItem.ticketTypeName })
      })
      if (this.ticketTypeData.pagination.total > this.ticketTypeData.result.length) {
        ret.push({ id: undefined, text: '...' })
      }
      return ret
    }
  },
  methods: {
    viewTicketTypes () {
      this.$router.push('/' + this.$route.params.tenantName + '/tenants/' + this.$route.params.selTenantNAME + '/tickettypes')
    },
    viewTicketType (val) {
      this.$router.push('/' + this.$route.params.tenantName + '/tenants/' + this.$route.params.selTenantNAME + '/tickettypes/' + val.id)
      event.preventDefault()
      event.stopPropagation()
    },
    addAuthProv () {
      this.editAuthProvModalDialogData.AddMode = true
      this.editAuthProvModalDialogData.DeleteMode = false
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
    editAuthProv (item) {
      this.editAuthProvModalDialogData.AddMode = false
      this.editAuthProvModalDialogData.DeleteMode = false
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
    deleteAuthProvTenantDialog () {
      var TTT = this
      TTT.$q.dialog({
        title: 'Confirm',
        message: 'Are you sure you want to delete this Auth Provider?',
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
        TTT.editAuthProvModalDialogData.DeleteMode = true
        TTT.okAuthProvTenantDialog()
      })
    },
    okAuthProvTenantDialog () {
      var TTT = this
      var isDeleting = TTT.editAuthProvModalDialogData.DeleteMode
      TTT.editAuthProvModalDialogData.DeleteMode = true

      // Shared validation
      if (this.editAuthProvModalDialogData.MenuText === '') {
        Notify.create({color: 'negative', message: 'Menu text must be filled in'})
        return
      }
      if (this.editAuthProvModalDialogData.LinkText === '') {
        Notify.create({color: 'negative', message: 'LinkText text must be filled in'})
        return
      }
      // Check configJSON string is valid JSON
      if (this.isConfigJSONInvalid) {
        Notify.create({color: 'negative', message: 'ConfigJSON is not valid JSON'})
        return
      }
      var newTenantJSON = JSON.parse(JSON.stringify(this.tenantData))
      var newAuthProvJSON = {
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
        for (var cur in newTenantJSON.AuthProviders) {
          if (newTenantJSON.AuthProviders[cur].guid === TTT.editAuthProvModalDialogData.guid) {
            if (isDeleting) {
              newTenantJSON.AuthProviders.splice(cur, 1)
            } else {
              newTenantJSON.AuthProviders[cur] = newAuthProvJSON
            }
          }
        }
      }
      var callback = {
        ok: function (response) {
          TTT.editAuthProvModalDialogVisible = false
          Notify.create({color: 'positive', message: 'Tenant Updated'})
          TTT.refreshTenantData()
        },
        error: function (error) {
          var verb = 'Update'
          if (TTT.editAuthProvModalDialogData.AddMode) {
            verb = 'Add'
          }
          Notify.create({color: 'negative', message: verb + ' Auth Provider failed - ' + callbackHelper.getErrorFromResponse(error)})
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
    cancelAuthProvTenantDialog () {
      this.editAuthProvModalDialogVisible = false
    },
    dialogEditJWTCollectionAllowedOriginListCreateValue (val, done) {
      if (val.length < 3) {
        Notify.create({color: 'negative', message: 'Must have at least 3 characters'})
        return
      }
      done(val, 'add-unique')
    },
    okEditTenantDialog () {
      var TTT = this
      this.editTenantModalDialogVisible = false
      if (this.editTenantModalDialogData.Description === this.tenantData.Description) {
        if (this.editTenantModalDialogData.AllowUserCreation === this.tenantData.AllowUserCreation) {
          if (this.editTenantModalDialogData.JWTCollectionAllowedOriginList === this.tenantData.JWTCollectionAllowedOriginList) {
            if (this.editTenantModalDialogData.TicketOverrideURL === this.tenantData.TicketOverrideURL) {
              if (this.editTenantModalDialogData.TenantBannerHTML === this.tenantData.TenantBannerHTML) {
                if (this.editTenantModalDialogData.SelectAuthMessage === this.tenantData.SelectAuthMessage) {
                  Notify.create({color: 'positive', message: 'No changes made'})
                  return // no change so do nothing
                }
              }
            }
          }
        }
      }
      var newTenantJSON = JSON.parse(JSON.stringify(this.tenantData))
      newTenantJSON.Description = this.editTenantModalDialogData.Description
      newTenantJSON.AllowUserCreation = this.editTenantModalDialogData.AllowUserCreation
      newTenantJSON.JWTCollectionAllowedOriginList = this.editTenantModalDialogData.JWTCollectionAllowedOriginList
      newTenantJSON.TicketOverrideURL = this.editTenantModalDialogData.TicketOverrideURL
      newTenantJSON.TenantBannerHTML = this.editTenantModalDialogData.TenantBannerHTML
      newTenantJSON.SelectAuthMessage = this.editTenantModalDialogData.SelectAuthMessage

      var callback = {
        ok: function (response) {
          Notify.create({color: 'positive', message: 'Tenant Updated'})
          TTT.refreshTenantData()
        },
        error: function (error) {
          Notify.create({color: 'negative', message: 'Update Tenant failed - ' + callbackHelper.getErrorFromResponse(error)})
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
      this.editTenantModalDialogData.JWTCollectionAllowedOriginList = this.tenantData.JWTCollectionAllowedOriginList
      this.editTenantModalDialogData.TicketOverrideURL = this.tenantData.TicketOverrideURL
      this.editTenantModalDialogData.TenantBannerHTML = this.tenantData.TenantBannerHTML
      this.editTenantModalDialogData.SelectAuthMessage = this.tenantData.SelectAuthMessage

      this.editTenantModalDialogVisible = true
      var TTT = this
      setTimeout(function () {
        TTT.$refs.descriptionInput.focus()
      }, 5)
    },
    refreshTicketTypeData () {
      var TTT = this
      var callback = {
        ok: function (response) {
          Loading.hide()
          TTT.ticketTypeData = response.data
        },
        error: function (error) {
          Loading.hide()
          Notify.create({color: 'negative', message: 'Ticket Type query failed - ' + callbackHelper.getErrorFromResponse(error)})
          TTT.ticketTypeData = getEmptyTicketTypeData()
        }
      }
      Loading.show()
      this.$store.dispatch('globalDataStore/callAdminAPI', {
        path: '/tenants/' + this.$route.params.selTenantNAME + '/tickettypes?pagesize=5',
        method: 'get',
        postdata: null,
        callback: callback,
        curPath: this.$router.history.current.path,
        headers: undefined
      })
    },
    refreshTenantData () {
      var jobNameToLoad = this.$route.params.selTenantNAME
      var TTT = this
      var callback = {
        ok: function (response) {
          TTT.tenantData = response.data
          TTT.refreshTicketTypeData()
        },
        error: function (error) {
          Loading.hide()
          Notify.create({color: 'negative', message: 'Tenant query failed - ' + callbackHelper.getErrorFromResponse(error)})
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
      }).onOk(() => {
        var callback = {
          ok: function (response) {
            Notify.create({color: 'positive', message: 'Tenant ' + nameOfTenantToDelete + ' deleted'})
            TTT.$router.push('/' + TTT.$route.params.tenantName + '/tenants/')
          },
          error: function (error) {
            Notify.create({color: 'negative', message: 'Delete Tenant failed - ' + callbackHelper.getErrorFromResponse(error)})
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
