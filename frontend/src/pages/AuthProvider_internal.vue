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
                <q-btn
                  v-if='authProvInfo.AllowUserCreation && tenantInfo.AllowUserCreation'
                  color="secondary"
                  push
                  @click="createAccountClick"
                >
                  Create Account
                </q-btn>
              </p>
            </div>
          </div>
        </q-page>
      </q-page-container>

      <q-dialog v-model="createAccountDialogModel.visible">
        <q-layout view="Lhh lpR fff" container class="bg-white" style="height: 400px; width: 700px; max-width: 80vw;">
          <q-header class="bg-primary">
            <q-toolbar>
              <q-toolbar-title>
                Create Account
              </q-toolbar-title>
              <q-btn flat v-close-popup round dense icon="close" />
            </q-toolbar>
          </q-header>

          <q-page-container>
            <q-page padding>
              <q-input
                v-model="createAccountDialogModel.username"
                ref="usernameDialogInput"
                helper="Username"
                label="Username"
                :label-width="3"
               />
              <q-input
                type="password"
                v-model="createAccountDialogModel.password"
                label="Password"
                :label-width="3"
                :error-message="passwordERRORMessage"
                :error="passwordERROR"
               />
              <q-input
                type="password"
                v-model="createAccountDialogModel.password2"
                @keyup.enter="okCreateAccountDialog"
                label="Retype Password"
                :label-width="3"
                :error-message="passwordERRORMessage"
                :error="passwordERROR"
              />
              <q-btn
                @click="okCreateAccountDialog"
                color="primary"
                label="Ok"
                class = "float-right q-ml-xs"
              />
              <q-btn
                @click="cancelCreateAccountDialog"
                label="Cancel"
                class = "float-right"
              />
            </q-page>
          </q-page-container>

        </q-layout>
      </q-dialog>

      <processLoginResponse ref="processLoginResponseInstance"></processLoginResponse>
    </q-layout>
  </div>
</template>

<style>
</style>

<script>
import {
  Notify,
  Loading
} from 'quasar'
import bcrypt from 'bcryptjs'
import frontendFns from '../frontendFns.js'
import processLoginResponse from '../components/processLoginResponse'

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
      },
      createAccountDialogModel: {
        visible: false,
        username: '',
        password: '',
        password2: ''
      }
    }
  },
  methods: {
    goBackToSelectAuthProviderScreen () {
      this.$router.replace('/' + this.$store.state.globalDataStore.tenantInfo.Name + '/selectAuth')
    },
    createAccountClick () {
      this.createAccountDialogModel = {
        visible: true,
        username: '',
        password: '',
        password2: ''
      }
      this.$refs.usernameDialogInput.focus()
    },
    okCreateAccountDialog () {
      var TTT = this
      if (this.passwordERROR) {
        Notify.create({color: 'negative', message: this.passwordERRORMessage})
        return
      }
      var callback = {
        ok: function (response) {
          Loading.hide()
          TTT.createAccountDialogModel.visible = false
          Notify.create({color: 'positive', message: 'Account created'})
        },
        error: function (response) {
          Loading.hide()
          var msg = 'unknown'
          if (typeof (response) !== 'undefined') {
            if (typeof (response.orig) !== 'undefined') {
              if (typeof (response.orig.response) !== 'undefined') {
                if (typeof (response.orig.response.data) !== 'undefined') {
                  if (typeof (response.orig.response.data.message) !== 'undefined') {
                    msg = response.orig.response.data.message
                  }
                }
              }
            }
          }
          Notify.create({color: 'negative', message: 'Login Failed - ' + msg})
        }
      }
      Loading.show()
      var passwordhash = bcrypt.hashSync(this.createAccountDialogModel.username + ':' + this.createAccountDialogModel.password + ':AG44', atob(this.authProvInfo.saltForPasswordHashing))
      frontendFns.callLoginAPI({
        store: this.$store,
        credentialJSON: {
          username: this.createAccountDialogModel.username,
          password: passwordhash
        },
        callback: callback,
        processLoginResponseInstance: undefined,
        registering: true
      })
    },
    cancelCreateAccountDialog () {
      this.createAccountDialogModel.visible = false
    },
    processLoginOKResponse (response, loginRequestPostData) {
      this.$refs.processLoginResponseInstance.processLoginOKResponse(response, loginRequestPostData)
    },
    usernamePassLogin () {
      var TTT = this
      if (this.$store.state.globalDataStore.selectedAuthProvGUID === null) {
        Notify.create({color: 'negative', message: 'No AuthProvGUID selected - you shouldn\'t navigate here directly'})
        return
      }
      var passwordhash = bcrypt.hashSync(this.usernamePass.username + ':' + this.usernamePass.password + ':AG44', atob(TTT.authProvInfo.saltForPasswordHashing))
      var callback = {
        ok: function (response) {
          Loading.hide()
        },
        error: function (response) {
          Loading.hide()
          Notify.create({color: 'negative', message: 'Login Failed'})
        }
      }
      Loading.show()
      frontendFns.callLoginAPI({
        store: this.$store,
        credentialJSON: {
          username: this.usernamePass.username,
          password: passwordhash
        },
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
