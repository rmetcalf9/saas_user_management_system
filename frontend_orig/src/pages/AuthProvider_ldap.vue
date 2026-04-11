<template>
  <div class="q-md">
    <q-layout>
      <q-page-container>
        <q-page flex class="full-width column justify-center items-center">
          <q-btn
            round
            icon="arrow_back" color="primary" style="position: fixed; left: 16px; top: 16px"
            size="md"
            v-if="hasMutipleLoginMethods"
            @click="goBackToSelectAuthProviderScreen"
          />
          <div>
            <div rows>
              <div v-html="tenantInfo.TenantBannerHTML" />
              <q-input v-model="usernamePass.username" placeholder="Username" ref="userNameInput" @keyup.enter="usernamePassLogin" />
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
          </div>
        </q-page>
      </q-page-container>
    </q-layout>
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
  methods: {
    goBackToSelectAuthProviderScreen () {
      this.$router.replace('/' + this.$store.state.globalDataStore.tenantInfo.Name + '/selectAuth')
    },
    usernamePassLogin () {
      var TTT = this
      if (this.$store.state.globalDataStore.selectedAuthProvGUID === null) {
        Notify.create({color: 'negative', message: 'No AuthProvGUID selected - you should not navigate here directly'})
        return
      }
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
        credentialJSON: ldapShared.getCredentialDict(
          TTT.authProvInfo.saltForPasswordHashing,
          this.usernamePass.username,
          this.usernamePass.password
        ),
        callback: callback,
        processLoginResponseInstance: TTT.$refs.processLoginResponseInstance
      })
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
    },
    hasMutipleLoginMethods () {
      return this.$store.state.globalDataStore.tenantInfo.AuthProviders.length !== 0
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
