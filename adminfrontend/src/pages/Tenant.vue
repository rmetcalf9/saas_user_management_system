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
    <q-item>
      <q-item-main >
        <q-item-tile label>Tenant Name: {{ tenantData.Name }}</q-item-tile>
        <q-item-tile sublabel>{{ tenantData.Description }}</q-item-tile>
      </q-item-main>
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
  </q-table>

  {{ tenantData }}
  </q-page>
</template>

<style>
</style>

<script>
import { Notify } from 'quasar'
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
        { name: 'IconLink', required: true, label: 'IconLink', align: 'left', field: 'IconLink', sortable: true, filter: false }
        // guid not in table
        // ConfigJSON not in table
      ]
    }
  },
  methods: {
    refreshTenantData () {
      var jobNameToLoad = this.$route.params.selTenantNAME
      var TTT = this
      var callback = {
        ok: function (response) {
          TTT.tenantData = response.data
          // TTT.stores().commit('globalDataStore/SET_PAGE_TITLE', 'Tenant ' + response.data.Name)
        },
        error: function (error) {
          Notify.create('Tenant query failed - ' + callbackHelper.getErrorFromResponse(error))
          TTT.tenantData = getEmptyTenantData()
        }
      }
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
