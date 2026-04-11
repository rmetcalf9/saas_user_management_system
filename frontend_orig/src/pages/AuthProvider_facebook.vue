<template>
  <div>
    <div class="fixed-center">
      Log in with Facebook<BR />
    </div>
    <processLoginResponse ref="processLoginResponseInstance"></processLoginResponse>
  </div>
</template>

<style>
</style>

<script>
// Notes: https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow
import {
  Notify, Loading
} from 'quasar'
import processLoginResponse from '../components/processLoginResponse'
import frontendFns from '../frontendFns.js'

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
    signInCallback (responseFromFacebook) {
      var TTT = this
      var callback = {
        ok: function (response) {
          Loading.hide()
        },
        error: function (response) {
          Loading.hide()
        }
      }
      Loading.show()
      frontendFns.callLoginAPI({
        store: this.$store,
        credentialJSON: responseFromFacebook,
        callback: callback,
        processLoginResponseInstance: TTT.$refs.processLoginResponseInstance
      })
    },
    displayErrorToUserAndMoveToLoginSelectionScreen (message) {
      Loading.hide()
      Notify.create({color: 'negative', message: message})
      this.$router.replace('/' + this.$store.state.globalDataStore.tenantInfo.Name + '/selectAuth')
    }
  },
  mounted: function () {
    var TTT = this
    Loading.show()

    // var returnURI = window.location.href + '2?usersystem_returnaddress=' + encodeURIComponent(this.$store.state.globalDataStore.usersystemReturnaddress)

    window.FB.init({
      appId: TTT.authProvInfo.StaticlyLoadedData.client_id,
      autoLogAppEvents: true,
      xfbml: true,
      version: 'v3.3'
    })

    window.FB.login(function (response) {
      if (response.authResponse) {
        TTT.signInCallback(response)
      } else {
        TTT.displayErrorToUserAndMoveToLoginSelectionScreen('User cancelled login or did not fully authorize.')
      }
    })
  }
}
</script>
