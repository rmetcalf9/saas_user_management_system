<template>
  <div>
    <q-btn
      push
      @click="linkClick()"
    >{{ authProvData.LinkText }}</q-btn>
  </div>
</template>

<script>
import {
  Loading
} from 'quasar'

export default {
  // name: 'AuthSecuritySettingsGoogle',
  props: [
    'authProvData'
  ],
  data () {
    return {
    }
  },
  methods: {
    linkClick () {
      Loading.show()
      var TTT = this
      this.$gapi.load('auth2', function () {
        var auth2 = TTT.$gapi.auth2.init({
          client_id: TTT.authProvData.StaticlyLoadedData.client_id
          // Scopes to request in addition to 'profile' and 'email'
          // scope: 'additional_scope'
        }, TTT.signInError, TTT.signInError)
        auth2.grantOfflineAccess().then(TTT.signInCallback, TTT.signInError)
      })
    },
    signInCallback (responseFromGoogle) {
      var TTT = this
      var credentialJSON = responseFromGoogle
      Loading.hide()
      TTT.$emit('completeOK', TTT.authProvData, credentialJSON)
    },
    signInError (errMsg) {
      Loading.hide()
      this.$emit('completeError', this.authProvData, 'Sign in error - ' + errMsg)
    }
  }
}
</script>

<style>
</style>
