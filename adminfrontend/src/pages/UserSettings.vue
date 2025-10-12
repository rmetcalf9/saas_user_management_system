<template>
  <q-page>
    <q-list >
      <q-item>
        <q-item-section >
          <q-item-label>User:</q-item-label>
          <q-item-label caption>{{ loggedInUserCookie.known_as }}</q-item-label>
        </q-item-section>
      </q-item>
      <q-item>
        <q-item-section >
          <q-item-label>Roles:</q-item-label>
          <div v-for="curRole in loggedInUserCookie.ThisTenantRoles" :key=curRole>
            <q-item-label caption>{{ curRole }}</q-item-label>
          </div>
        </q-item-section>
      </q-item>
      <q-item>
        <q-item-section >
          <q-item-label>Other:</q-item-label>
          <q-item-label caption >
            <saasUsermanagementLoginItem
              viewstyle="securitysettingsbutton"
            />
            <div>Note: doesn't work when running locally since relies on cookie and won't read across different domain.</div>
          </q-item-label>
        </q-item-section>
      </q-item>
      <q-item>
        <q-item-section >
          <q-item-label>Logged in users cookie:</q-item-label>
          <q-item-label caption>{{ loggedInUserCookie }}</q-item-label>
        </q-item-section>
      </q-item>
      <q-item>
        <q-item-section >
          <q-item-label>adminfrontend codebase version:</q-item-label>
          <q-item-label caption>{{ codebasever }}</q-item-label>
        </q-item-section>
      </q-item>
    </q-list>
  </q-page>
</template>

<script>
import { Cookies } from 'quasar'
import rjmversion from '../rjmversion'
import saasUsermanagementLoginItem from '../components/saasUsermanagementLoginItem.vue'

export default {
  name: 'PageUserSettings',
  components: {
    saasUsermanagementLoginItem
  },
  computed: {
    loggedInUserCookie () {
      // saasUserManagementClientStoreCredentials
      return Cookies.get('saasUserManagementClientStoreCredentials')
    },
    codebasever () {
      return rjmversion.codebasever
    },
    securitySettingsUrl () {
      return 'AAA'
    }
  },
  methods: {
    securitySettingsClick () {
      this.$router.replace('/' + this.$route.params.tenantName + '/SecuritySettings')
    }
  }
}
</script>

<style>
</style>
