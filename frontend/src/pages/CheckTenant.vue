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
        if (TTT.$store.state.globalDataStore.tenantInfo.Name === TTT.$route.params.tenantName) {
          if (typeof (TTT.$route.query.usersystem_redirect) !== 'undefined' && TTT.$route.query.usersystem_redirect !== null) {
            TTT.$router.replace(TTT.$route.query.usersystem_redirect)
          } else {
            TTT.$router.replace('/' + TTT.$store.state.globalDataStore.tenantInfo.Name + '/selectAuth')
          }
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
    // console.log('CheckTenant.vue ra:', TTT.$store.state.globalDataStore.usersystemReturnaddressInternal)
    this.$store.dispatch('globalDataStore/checkAuthProviders', {
      tenantName: this.$route.params.tenantName,
      callback: callback,
      currentHREF: window.location.href
    })
  }
}
</script>
