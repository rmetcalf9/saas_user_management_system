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
    <q-modal v-model="createAccountDialogModel.visible" :content-css="{minWidth: '40vw', minHeight: '30vh'}">
      <q-modal-layout>
        <q-toolbar slot="header">
            <q-btn
            color="primary"
            flat
            round
            dense
            icon="keyboard_arrow_left"
            @click="cancelCreateAccountDialog"
          />
          <q-toolbar-title>
            Create Account
          </q-toolbar-title>
        </q-toolbar>

        <div class="layout-padding">
          <q-field helper="Username" label="Username" :label-width="3">
            <q-input v-model="createAccountDialogModel.username" ref="usernameDialogInput"/>
          </q-field>
          <q-field :helper="passwordERRORMessage" label="Password" :label-width="3" :error="passwordERROR">
            <q-input type="password" v-model="createAccountDialogModel.password" />
          </q-field>
          <q-field helper="Retype Password" label="Retype" :label-width="3" :error="passwordERROR">
            <q-input type="password" v-model="createAccountDialogModel.password2" @keyup.enter="okCreateAccountDialog" />
          </q-field>
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
        </div>
      </q-modal-layout>
    </q-modal>
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

export default {
  name: 'AuthProvider_internal',
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
      if (/[A-Z]/.test(this.createAccountDialogModel.password) !== true) {
        return 'Password must contain at least one uppercase letter'
      }
      if (/[a-z]/.test(this.createAccountDialogModel.password) !== true) {
        return 'Password must contain at least one lowercase letter'
      }
      if (/\d/.test(this.createAccountDialogModel.password) !== true) {
        return 'Password must contain at least one number'
      }
      if (this.createAccountDialogModel.password.length < 5) {
        return 'Password must be at least 5 characters'
      }
      if (this.createAccountDialogModel.password !== this.createAccountDialogModel.password2) {
        return 'Passwords must match'
      }
      return 'Password'
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
          Notify.create({color: 'positive', detail: 'Account created'})
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
    usernamePassLogin () {
      var TTT = this
      if (this.$store.state.globalDataStore.selectedAuthProvGUID === null) {
        Notify.create('No AuthProvGUID selected - you shouldn\'t navigate here directly')
        return
      }

      var callback = {
        ok: function (response) {
          Loading.hide()
          // Decide if we got a JWTToken back or an identity selection list
          //   either forward to the JWTToken setting page or
          //   the identity selection page
          var gotLogin = false
          if ('jwtData' in response.data) {
            gotLogin = true
          }
          if (gotLogin) {
            if (TTT.$store.state.globalDataStore.usersystemReturnaddress === null) {
              Notify.create('Error - Webapplication failed to provide return address')
              return
            }
            if (typeof (TTT.$store.state.globalDataStore.usersystemReturnaddress) === 'undefined') {
              Notify.create('Error - Webapplication failed to provide return address (undefined)')
              return
            }
            if (TTT.$store.state.globalDataStore.usersystemReturnaddress === 'undefined') {
              Notify.create('Error - Webapplication failed to provide return address (undefined string)')
              return
            }
            // Expires in one day
            TTT.$q.cookies.set('usersystemUserCredentials', response.data, {expires: 1, path: '/'})
            console.log('Redirecting back to main site:', TTT.$store.state.globalDataStore.usersystemReturnaddress)
            window.location.href = TTT.$store.state.globalDataStore.usersystemReturnaddress
          } else {
            Notify.create('Identity selection not implemented')
            console.log(response.data)
          }
        },
        error: function (response) {
          Loading.hide()
          Notify.create('Login Failed')
        }
      }
      Loading.show()
      var passwordhash = bcrypt.hashSync(this.usernamePass.username + ':' + this.usernamePass.password + ':AG44', atob(TTT.authProvInfo.saltForPasswordHashing))
      this.$store.dispatch('globalDataStore/callLoginAPI', {
        method: 'POST',
        path: '/authproviders',
        callback: callback,
        postdata: {
          credentialJSON: {
            username: this.usernamePass.username,
            password: passwordhash
          },
          authProviderGUID: this.$store.state.globalDataStore.selectedAuthProvGUID
        }
      })
    }
  },
  mounted: function () {
    if (this.$store.state.globalDataStore.messagePendingDisplay !== null) {
      Notify.create({color: 'negative', detail: this.$store.state.globalDataStore.messagePendingDisplay})
      this.$store.commit('globalDataStore/setMessageDisplayed')
    }
    var TTT = this
    this.$nextTick(function () {
      TTT.$refs.userNameInput.focus()
    })
  }
}
</script>
