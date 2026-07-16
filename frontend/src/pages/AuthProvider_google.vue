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
      usernamePass: {
        username: '',
        password: ''
      }
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
      while (!window.google?.accounts?.oauth2) {
        await new Promise(resolve => setTimeout(resolve, 100))
      }
      this.startGoogleLogin()
    },
    startGoogleLogin () {
      const TTT = this
      const client = window.google.accounts.oauth2.initCodeClient({
        client_id: TTT.selectedAuthProvider.StaticlyLoadedData.client_id,
        scope: 'openid email profile',
        ux_mode: 'popup', // important
        callback: (response) => {
          if (response.code) {
            TTT.signInCallback({
              code: response.code
            })
          } else {
            TTT.signInError(response)
          }
        }
      })
      client.requestCode()
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
