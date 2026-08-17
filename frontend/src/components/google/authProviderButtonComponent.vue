<template>
  <div>
    <q-btn
      :label="authProvider.MenuText"
      @click="clickSignin"
      v-if="btnVisible"
    />
    <ProcessLoginResponse ref="processLoginResponseInstance" />
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { Notify, Loading } from 'quasar'
import callbackHelper from '../../callbackHelper'
import frontendFns from '../../frontendFns.js'
import { useTenantInfoStore } from 'stores/tenantInfo'
import ProcessLoginResponse from '../../components/processLoginResponse'

export default defineComponent({
  name: 'AuthProviderButtomComponent_Google',
  props: [
    'authProvider'
  ],
  components: {
    ProcessLoginResponse
  },
  setup () {
    const tenantInfoStore = useTenantInfoStore()
    return { tenantInfoStore }
  },
  data () {
    return {
      btnVisible: false
    }
  },
  methods: {
    clickSignin () {
      const TTT = this
      TTT.tenantInfoStore.selectAuthProvider({
        selectedAuthProvider: TTT.authProvider,
        tenantName: TTT.$route.params.tenantName
      })
      TTT.startGoogleLogin()
    },
    signInCallback (responseFromGoogle) {
      const TTT = this
      TTT.googleLoginState = 'Callback Received...'
      const callback = {
        ok: function (response) {
          Loading.hide()
        },
        error: function (response) {
          Loading.hide()
          Notify.create({
            color: 'negative',
            message: 'Google Auth failed - ' + callbackHelper.getErrorFromResponse(response)
          })
          TTT.$router.replace('/' + TTT.$route.params.tenantName + '/')
        }
      }
      Loading.show()
      frontendFns.callLoginAPI({
        credentialJSON: responseFromGoogle,
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
        message: 'Google signin error - ' + JSON.stringify(err)
      })
      console.log('Google signInError', err)
      this.$router.replace('/' + this.$route.params.tenantName + '/')
    },
    async waitForGoogle () {
      const TTT = this
      try {
        TTT.googleLoginState = 'Waiting for Google...'
        const maxWait = 20000
        const start = Date.now()

        while (Date.now() - start < maxWait) {
          const googleReady = !!window.google?.accounts?.oauth2
          const clientId = this.authProvider?.StaticlyLoadedData?.client_id

          if (!googleReady) {
            if (!clientId) {
              TTT.googleLoginState = 'Waiting for Google (Google, client)...'
            } else {
              TTT.googleLoginState = 'Waiting for Google (Google)...'
            }
          } else {
            if (!clientId) {
              TTT.googleLoginState = 'Waiting for Google (client)...'
            }
          }

          if (googleReady && clientId) {
            console.log('Google login prerequisites ready')
            TTT.googleLoginState = 'Google Ready...'
            TTT.btnVisible = true
            return
          }

          await new Promise(resolve => setTimeout(resolve, 100))
        }

        TTT.googleLoginState = 'Google load timed out'
        console.error('Google login timed out')

        this.signInError({
          error: 'Google login could not be initialized'
        })
      } catch (err) {
        console.error('Google login initialisation exception', err)
        TTT.googleLoginState = 'Google load exception received'

        this.signInError({
          error: 'Google login initialisation failed: ' + err?.message
        })
      }
    },
    startGoogleLogin () {
      const TTT = this

      try {
        TTT.googleLoginState = 'Creating Google client...'

        const client = window.google.accounts.oauth2.initCodeClient({
          client_id: TTT.authProvider.StaticlyLoadedData.client_id,
          scope: 'openid email profile',
          ux_mode: 'popup',
          callback: (response) => {
            try {
              if (response.code) {
                TTT.googleLoginState = 'Launched'
                TTT.signInCallback({
                  code: response.code
                })
              } else {
                TTT.googleLoginState = 'Failed'
                TTT.signInError(response)
              }
            } catch (err) {
              TTT.googleLoginState = 'Callback exception: ' + (err?.message || String(err))
            }
          }
        })

        TTT.googleLoginState = 'Google client created...'

        try {
          TTT.googleLoginState = 'Calling requestCode...'
          client.requestCode()
          TTT.googleLoginState = 'requestCode returned...'
        } catch (err) {
          TTT.googleLoginState = 'requestCode exception: ' + (err?.message || String(err))
        }
      } catch (err) {
        TTT.googleLoginState = 'initCodeClient exception: ' + (err?.message || String(err))
        console.error('Google initCodeClient exception:', err)
      }
    }
  },
  mounted () {
    this.waitForGoogle()
  }
})
</script>

<style>
</style>
