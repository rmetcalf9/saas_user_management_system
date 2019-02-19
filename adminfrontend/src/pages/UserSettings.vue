<template>
  <q-page>
    <q-list >
      <q-item>
        <q-item-main >
          <q-item-tile label>User:</q-item-tile>
          <q-item-tile sublabel>{{ loggedInUserCookie.known_as }}</q-item-tile>
        </q-item-main>
      </q-item>
      <q-item>
        <q-item-main >
          <q-item-tile label>Roles:</q-item-tile>
          <q-item-tile sublabel v-for="curVal in loggedInUserCookie.ThisTenantRoles" :key=curVal>{{ curVal }}</q-item-tile>
        </q-item-main>
      </q-item>
    </q-list>

    {{ loggedInUserCookie }}
  </q-page>
</template>

<style>
</style>

<script>
import { Cookies } from 'quasar'
export default {
  name: 'PageIndex',
  computed: {
    loggedInUserCookie () {
      return Cookies.get('usersystemUserCredentials')
    }
  }
}
</script>
