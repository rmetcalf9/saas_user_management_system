<template>
  <div>
    <div class="fixed-center">
      TODO Log in with Google<BR />
      Client_ID: {{ authProvInfo.StaticlyLoadedData.client_id }}<BR />
      AuthProvInfo: {{ authProvInfo }}
    </div>
  </div>
</template>

<style>
</style>

<script>
// Notes: https://developers.google.com/identity/sign-in/web/server-side-flow
import {
  Notify
} from 'quasar'

export default {
  name: 'AuthProvider_internal',
  data () {
    return {
    }
  },
  computed: {
    tenantInfo () {
      return this.$store.state.globalDataStore.tenantInfo
    },
    authProvInfo () {
      return this.$store.getters['globalDataStore/getAuthProvFromGUID'](this.$store.state.globalDataStore.selectedAuthProvGUID)
    }
  },
  methods: {
    signInCallback (response) {
      console.log('response:', response)
      Notify.create({color: 'negative', detail: 'TODO Process signin callback'})
    }
  },
  mounted: function () {
    var TTT = this
    if (this.$store.state.globalDataStore.messagePendingDisplay !== null) {
      Notify.create({color: 'negative', detail: this.$store.state.globalDataStore.messagePendingDisplay})
      this.$store.commit('globalDataStore/setMessageDisplayed')
    }
    this.$gapi.load('auth2', function () {
      var auth2 = this.$gapi.auth2.init({
        client_id: this.authProvInfo.StaticlyLoadedData.client_id
        // Scopes to request in addition to 'profile' and 'email'
        // scope: 'additional_scope'
      })
      auth2.grantOfflineAccess().then(TTT.signInCallback)
    })
  }
}
</script>
