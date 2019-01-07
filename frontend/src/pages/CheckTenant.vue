<!--
This page checks the tenant passed in and if it is valid moves the client on to the correct page
 or 404 if tenant is not found.
-->
<template>
  <div class="fixed-center">
  </div>
</template>

<style>
</style>

<script>
import {
  Loading
} from 'quasar'

export default {
  name: 'CheckTenant',
  created () {
    Loading.show()
    var TTT = this
    var callback = {
      ok: function (response) {
        Loading.hide()
        if (TTT.$store.state.globalDataStore.tenant === TTT.$route.params.tenantName) {
          TTT.$router.replace('/' + TTT.$store.state.globalDataStore.tenant + '/selectAuth')
        } else {
          console.log('Returned tenantName mismatch')
          /// go to root, this will give us a 404
          TTT.$router.replace('/')
        }
      },
      error: function (response) {
        Loading.hide()
        /// go to root, this will give us a 404
        TTT.$router.replace('/')
      }
    }
    if (this.$route.params.tenantName === '') {
      Loading.hide()
      /// go to root, this will give us a 404
      TTT.$router.replace('/')
      return
    }
    this.$store.dispatch('globalDataStore/checkAuthProviders', {
      tenantName: this.$route.params.tenantName,
      callback: callback,
      currentRoute: this.$route
    })
  }
}
</script>
