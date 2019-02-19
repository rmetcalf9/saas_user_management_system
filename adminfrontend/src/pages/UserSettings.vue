<template>
  <q-page>
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
