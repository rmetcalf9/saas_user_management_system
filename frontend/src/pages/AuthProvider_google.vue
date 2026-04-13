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
    textBoxKeyUp (e) {
      if (e.key === 'Enter') {
        this.usernamePassLogin()
      }
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
            message: 'Create Account failed - ' + callbackHelper.getErrorFromResponse(response)
          })
        }
      }
      Loading.show()
      frontendFns.callLoginAPI({
        credentialJSON: responseFromGoogle,
        callback,
        processLoginResponseInstance: TTT.$refs.processLoginResponseInstance,
        registering: false,
        router: this.$router
      })
    },
    signInError (err) {
      Loading.hide()
      Notify.create({
        color: 'negative',
        message: 'Google signin error - ' + callbackHelper.getErrorFromResponse(err)
      })
      console.log(err)
    }
  },
  mounted: function () {
    const TTT = this
    Loading.show()
    this.$gapi.load('auth2', function () {
      const auth2 = TTT.$gapi.auth2.init({
        client_id: TTT.selectedAuthProvider.StaticlyLoadedData.client_id
        // Scopes to request in addition to 'profile' and 'email'
        // scope: 'additional_scope'
      }, TTT.signInError, TTT.signInError)
      auth2.grantOfflineAccess().then(TTT.signInCallback, TTT.signInError)
    })
  }
})
</script>

<style>
.authprovider_internal_loginbuttons {
  padding: 10px;
}
</style>
