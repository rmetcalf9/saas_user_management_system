<template>
  <div>
    <div class="fixed-center">
      TODO Log in with Google<BR />
      Client_ID: {{ authProvInfo.StaticlyLoadedData.client_id }}<BR />
      AuthProvInfo: {{ authProvInfo }}
    </div>
    <processLoginResponse ref="processLoginResponseInstance"></processLoginResponse>
  </div>
</template>

<style>
</style>

<script>
// Notes: https://developers.google.com/identity/sign-in/web/server-side-flow
import {
  Notify, Loading
} from 'quasar'
import processLoginResponse from '../components/processLoginResponse'

export default {
  name: 'AuthProvider_internal',
  components: {
    'processLoginResponse': processLoginResponse
  },
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
    signInCallback (responseFromGoogle) {
      var TTT = this
      var loginRequestPostData = {
        credentialJSON: responseFromGoogle,
        authProviderGUID: TTT.$store.state.globalDataStore.selectedAuthProvGUID
      }
      var callback = {
        ok: function (response) {
          Loading.hide()
          TTT.$refs.processLoginResponseInstance.processLoginOKResponse(response, loginRequestPostData)
        },
        error: function (response) {
          TTT.displayErrorToUserAndMoveToLoginSelectionScreen('Login Failed')
        }
      }
      TTT.$store.dispatch('globalDataStore/callLoginAPI', {
        method: 'POST',
        path: '/authproviders',
        callback: callback,
        postdata: loginRequestPostData
      })
    },
    signInError (err) {
      this.displayErrorToUserAndMoveToLoginSelectionScreen('TODO Process err: ' + err)
    },
    displayErrorToUserAndMoveToLoginSelectionScreen (message) {
      Loading.hide()
      Notify.create({color: 'negative', detail: message})
      this.$router.replace('/' + this.$store.state.globalDataStore.tenantInfo.Name + '/selectAuth')
    }
  },
  mounted: function () {
    var TTT = this
    Loading.show()
    if (this.$store.state.globalDataStore.messagePendingDisplay !== null) {
      Notify.create({color: 'negative', detail: this.$store.state.globalDataStore.messagePendingDisplay})
      this.$store.commit('globalDataStore/setMessageDisplayed')
    }
    this.$gapi.load('auth2', function () {
      var auth2 = TTT.$gapi.auth2.init({
        client_id: TTT.authProvInfo.StaticlyLoadedData.client_id
        // Scopes to request in addition to 'profile' and 'email'
        // scope: 'additional_scope'
      }, TTT.signInError, TTT.signInError)
      auth2.grantOfflineAccess().then(TTT.signInCallback, TTT.signInError)
    })
  }
}
</script>
