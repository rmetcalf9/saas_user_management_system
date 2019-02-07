<template>
  <div>
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
  </div>
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
        { name: 'guid', required: true, label: 'guid', align: 'left', field: 'guid', sortable: true, filter: false },
        { name: 'Type', required: true, label: 'Type', align: 'left', field: 'Type', sortable: true, filter: false },
        { name: 'AllowUserCreation', required: true, label: 'AllowUserCreation', align: 'left', field: 'AllowUserCreation', sortable: true, filter: false },
        { name: 'MenuText', required: true, label: 'MenuText', align: 'left', field: 'MenuText', sortable: true, filter: false },
        { name: 'IconLink', required: true, label: 'IconLink', align: 'left', field: 'IconLink', sortable: true, filter: false }
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
        curPath: this.$router.history.current.path
      })
    }
  },
  mounted () {
    this.refreshTenantData()
  }
}
</script>
