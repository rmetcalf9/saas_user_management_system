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
  // name: 'AuthSecuritySettingsFacebook',
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

      window.FB.init({
        appId: TTT.authProvData.StaticlyLoadedData.client_id,
        autoLogAppEvents: true,
        xfbml: true,
        version: 'v3.3'
      })

      window.FB.login(function (response) {
        if (response.authResponse) {
          TTT.signInCallback(response)
        } else {
          TTT.signInError('User cancelled login or did not fully authorize.')
        }
      })
    },
    signInCallback (responseFromFacebook) {
      var TTT = this
      var credentialJSON = responseFromFacebook
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
