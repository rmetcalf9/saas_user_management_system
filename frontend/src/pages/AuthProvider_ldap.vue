<template>
  <div>
    <div class="fixed-center">
      <q-input v-model="usernamePass.username" placeholder="Username" ref="userNameInput" @keyup.enter="usernamePassLogin" />
      <br>
      <q-input type="password" v-model="usernamePass.password" placeholder="Password" @keyup.enter="usernamePassLogin" />
      <p class="text-center group">
        <q-btn
          color="primary"
          push
          @click="usernamePassLogin"
        >
          Login
        </q-btn>
      </p>
    </div>
    <processLoginResponse ref="processLoginResponseInstance"></processLoginResponse>
  </div>
</template>

<style>
</style>

<script>
import {
  Notify,
  Loading
} from 'quasar'
import frontendFns from '../frontendFns.js'
import processLoginResponse from '../components/processLoginResponse'
import ldapShared from '../ldap_shared.js'

export default {
  name: 'AuthProvider_internal',
  components: {
    'processLoginResponse': processLoginResponse
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
      return this.$store.state.globalDataStore.tenantInfo
    },
    authProvInfo () {
      return this.$store.getters['globalDataStore/getAuthProvFromGUID'](this.$store.state.globalDataStore.selectedAuthProvGUID)
    },
    passwordERROR () {
      return (this.passwordERRORMessage !== 'Password')
    },
    passwordERRORMessage () {
      return frontendFns.passwordERRORMessage(this.createAccountDialogModel.password, this.createAccountDialogModel.password2)
    }
  },
  methods: {
    processLoginOKResponse (response, loginRequestPostData) {
      Loading.hide()
      this.$refs.processLoginResponseInstance.processLoginOKResponse(response, loginRequestPostData)
    },
    usernamePassLogin () {
      var TTT = this
      if (this.$store.state.globalDataStore.selectedAuthProvGUID === null) {
        Notify.create({color: 'negative', message: 'No AuthProvGUID selected - you shouldn\'t navigate here directly'})
        return
      }
      var loginRequestPostData = {
        credentialJSON: ldapShared.getCredentialDict(
          TTT.authProvInfo.saltForPasswordHashing,
          this.usernamePass.username,
          this.usernamePass.password
        ),
        authProviderGUID: this.$store.state.globalDataStore.selectedAuthProvGUID
      }
      var callback = {
        ok: function (response) {
          TTT.processLoginOKResponse(response, loginRequestPostData)
        },
        error: function (response) {
          Loading.hide()
          Notify.create({color: 'negative', message: 'Login Failed'})
        }
      }
      Loading.show()
      this.$store.dispatch('globalDataStore/callLoginAPI', {
        method: 'POST',
        path: '/authproviders',
        callback: callback,
        postdata: loginRequestPostData
      })
    }
  },
  mounted: function () {
    if (this.$store.state.globalDataStore.messagePendingDisplay !== null) {
      Notify.create({color: 'negative', message: this.$store.state.globalDataStore.messagePendingDisplay})
      this.$store.commit('globalDataStore/setMessageDisplayed')
    }
    var TTT = this
    this.$nextTick(function () {
      TTT.$refs.userNameInput.focus()
    })
  }
}
</script>
