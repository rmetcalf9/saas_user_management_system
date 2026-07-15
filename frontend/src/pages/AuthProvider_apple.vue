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
        <div>Log in with Apple</div>
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
          Loading.hide()
        },
        error: function (response) {
          Loading.hide()
          Notify.create({
            color: 'negative',
            message: 'Apple Auth failed - ' + callbackHelper.getErrorFromResponse(response)
          })
          TTT.$router.replace('/' + TTT.$route.params.tenantName + '/')
        }
      }
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
        message: 'Apple signin error - ' + callbackHelper.getErrorFromResponse(err)
      })
      console.log(err)
      this.$router.replace('/' + this.$route.params.tenantName + '/')
    }
  },
  mounted () {
    const TTT = this
    // console.log('apple service id=', JSON.parse(TTT.selectedAuthProvider.ConfigJSON).service_id)

    window.AppleID.auth.init({
      clientId: JSON.parse(TTT.selectedAuthProvider.ConfigJSON).service_id,
      scope: 'name email',
      redirectURI: 'https://api.metcarob.com/auth/apple/callback',
      usePopup: true
    })

    window.AppleID.auth.signIn()
      .then(response => {
        TTT.signInCallback(response)
      })
      .catch(err => {
        TTT.signInError(err)
      })
  }
})
</script>

<style>
.authprovider_internal_loginbuttons {
  padding: 10px;
}
</style>
