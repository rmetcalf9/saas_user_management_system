<template>
  <q-page class="flex flex-center indexpage-main">
    <DisplayInputMessage />
    <q-btn
      round
      icon="arrow_back" color="primary" style="position: fixed; left: 16px; top: 56px"
      size="md"
      v-if="hasMutipleLoginMethods"
      @click="goBackToSelectAuthProviderScreen"
    />
    <div>
      <div rows>
        <div v-html="tenantInfo.TenantBannerHTML" />
        <div>Log in with Google</div>
        <div>{{ googleLoginState }}</div>
      </div>
    </div>
    <ProcessLoginResponse ref="processLoginResponseInstance" />
  </q-page>
</template>

<script>
import { defineComponent } from 'vue'
import { Notify, Loading } from 'quasar'
import DisplayInputMessage from '../components/displayInputMessage.vue'
import { useTenantInfoStore } from 'stores/tenantInfo'
import ProcessLoginResponse from '../components/processLoginResponse'
import callbackHelper from '../callbackHelper'
import frontendFns from '../frontendFns.js'

export default defineComponent({
  name: 'IndexPage',
  components: {
    DisplayInputMessage, ProcessLoginResponse
  },
  setup () {
    const tenantInfoStore = useTenantInfoStore()
    return { tenantInfoStore }
  },
  data () {
    return {
      googleLoginState: 'Setting up...'
    }
  },
  computed: {
    tenantInfo () {
      return this.tenantInfoStore.getInfo({
        router: this.$router,
        tenantName: this.$route.params.tenantName,
        skipcache: false
      })
    },
    selectedAuthProvider () {
      return this.tenantInfoStore.selectedAuth
    },
    hasMutipleLoginMethods () {
      return this.tenantInfo.res.AuthProviders.length !== 1
    }
  },
  methods: {
    goBackToSelectAuthProviderScreen () {
      this.tenantInfoStore.clearAuthProvider()
      this.$router.push('/' + this.$route.params.tenantName + '/')
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
        message: 'Google signin error - ' + callbackHelper.getErrorFromResponse(err)
      })
      console.log(err)
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
          const clientId = this.selectedAuthProvider?.StaticlyLoadedData?.client_id

          if (googleReady && clientId) {
            console.log('Google login prerequisites ready')
            TTT.googleLoginState = 'Google Ready...'
            TTT.startGoogleLogin()
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
          client_id: TTT.selectedAuthProvider.StaticlyLoadedData.client_id,
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
.authprovider_internal_loginbuttons {
  padding: 10px;
}
</style>
