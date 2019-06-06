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
          <q-item-label caption v-for="curVal in loggedInUserCookie.ThisTenantRoles" :key=curVal>{{ curVal }}</q-item-label>
        </q-item-section>
      </q-item>
      <q-item>
        <q-item-section >
          <q-item-label>Other:</q-item-label>
          <q-item-label caption >
            <q-btn
              color="primary"
              @click="securitySettingsClick"
              label="Security Settings"
            />
          </q-item-label>
        </q-item-section>
      </q-item>
      <q-item>
        <q-item-section >
          <q-item-label>Logged in users cookie:</q-item-label>
          <q-item-label caption>{{ loggedInUserCookie }}</q-item-label>
        </q-item-section>
      </q-item>
    </q-list>
  </q-page>
</template>

<style>
</style>

<script>
import { Cookies } from 'quasar'
export default {
  name: 'PageIndex',
  methods: {
    securitySettingsClick () {
      this.$store.commit('globalDataStore/SET_LOGOUT_CLICK_CUR_ROUTE', this.$router.currentRoute.path)
      this.$router.replace('/' + this.$route.params.tenantName + '/SecuritySettings')
    }
  },
  computed: {
    loggedInUserCookie () {
      return Cookies.get('usersystemUserCredentials')
    }
  }
}
</script>
