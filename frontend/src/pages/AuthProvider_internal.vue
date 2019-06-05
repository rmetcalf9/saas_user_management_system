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

    <q-dialog v-model="createAccountDialogModel.visible">
      <q-layout view="Lhh lpR fff" container class="bg-white" style="width: 700px; max-width: 80vw;">
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
        Notify.create(this.passwordERRORMessage)
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
          Notify.create('Login Failed - ' + msg)
        }
      }
      Loading.show()
      var passwordhash = bcrypt.hashSync(this.createAccountDialogModel.username + ':' + this.createAccountDialogModel.password + ':AG44', atob(this.authProvInfo.saltForPasswordHashing))
      this.$store.dispatch('globalDataStore/callLoginAPI', {
        method: 'PUT',
        path: '/register',
        callback: callback,
        postdata: {
          credentialJSON: {
            username: this.createAccountDialogModel.username,
            password: passwordhash
          },
          authProviderGUID: this.$store.state.globalDataStore.selectedAuthProvGUID
        }
      })
    },
    cancelCreateAccountDialog () {
      this.createAccountDialogModel.visible = false
    },
    processLoginOKResponse (response, loginRequestPostData) {
      Loading.hide()
      this.$refs.processLoginResponseInstance.processLoginOKResponse(response, loginRequestPostData)
    },
    usernamePassLogin () {
      var TTT = this
      if (this.$store.state.globalDataStore.selectedAuthProvGUID === null) {
        Notify.create('No AuthProvGUID selected - you shouldn\'t navigate here directly')
        return
      }
      var passwordhash = bcrypt.hashSync(this.usernamePass.username + ':' + this.usernamePass.password + ':AG44', atob(TTT.authProvInfo.saltForPasswordHashing))
      var loginRequestPostData = {
        credentialJSON: {
          username: this.usernamePass.username,
          password: passwordhash
        },
        authProviderGUID: this.$store.state.globalDataStore.selectedAuthProvGUID
      }
      var callback = {
        ok: function (response) {
          TTT.processLoginOKResponse(response, loginRequestPostData)
        },
        error: function (response) {
          Loading.hide()
          Notify.create('Login Failed')
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
