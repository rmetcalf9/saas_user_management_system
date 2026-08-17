<template>
  <div>
    <q-btn
      :label="authProvider.MenuText"
      @click="clickSignin"
    />
    <ProcessLoginResponse ref="processLoginResponseInstance" />
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { Notify, Loading } from 'quasar'
import callbackHelper from '../../callbackHelper'
import frontendFns from '../../frontendFns.js'

export default defineComponent({
  name: 'AuthProviderButtomComponent_Apple',
  props: [
    'authProvider'
  ],
  data () {
    return {
    }
  },
  methods: {
    clickSignin () {
      const TTT = this
      console.log('ClickSignIn')
      window.AppleID.auth.signIn()
        .then(response => {
          TTT.signInCallback(response)
        })
        .catch(err => {
          TTT.signInError(err)
        })
    },
    signInCallback (responseFromApple) {
      // responseFromApple Sample
      // {
      //  "authorization": {
      //    "code": "c1234567890abcdef...",
      //    "id_token": "eyJraWQiOiJFb...eyJhbGciOiJSUzI1NiJ9...",
      //    "state": "optional-state-value"
      //  },
      //  "user": {  FIRST TIME ONLY!!!
      //    "email": "abc123@privaterelay.appleid.com",
      //    "name": {
      //      "firstName": "Robert",
      //      "lastName": "Metcalf"
      //    }
      //  }
      // }
      const TTT = this
      const callback = {
        ok: function (response) {
          console.log('usersystem sign in ok')
          Loading.hide()
        },
        error: function (response) {
          console.log('usersystem sign in error')
          Loading.hide()
          Notify.create({
            color: 'negative',
            message: 'Apple Auth failed - ' + callbackHelper.getErrorFromResponse(response)
          })
          TTT.$router.replace('/' + TTT.$route.params.tenantName + '/')
        }
      }
      console.log('Got response from Apple login')
      Loading.show()
      frontendFns.callLoginAPI({
        credentialJSON: responseFromApple,
        callback,
        processLoginResponseInstance: TTT.$refs.processLoginResponseInstance,
        registering: false,
        router: TTT.$router
      })
    },
    signInError (err) {
      Loading.hide()
      Notify.create({
        color: 'negative',
        message: 'Apple signin error - ' + JSON.stringify(err)
      })
      console.log('Apple signInError', err)
      this.$router.replace('/' + this.$route.params.tenantName + '/')
    }
  },
  mounted () {
    const TTT = this
    // console.log('apple service id=', JSON.parse(TTT.selectedAuthProvider.ConfigJSON).service_id)

    window.AppleID.auth.init({
      clientId: JSON.parse(TTT.authProvider.ConfigJSON).service_id,
      scope: 'name email',
      redirectURI: 'https://api.metcarob.com/auth/apple/callback',
      usePopup: true
    })
  }
})
</script>

<style>
</style>
