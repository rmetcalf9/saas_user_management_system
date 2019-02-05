<template>
  <div class="fixed-center">
    <div>
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
      }
    }
  },
  computed: {
    tenantInfo () {
      return this.$store.state.globalDataStore.tenantInfo
    }
  },
  methods: {
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
      var masterSecretKey = 'admin:admin:AG44'
      var base64encodedSalt = this.$store.getters['globalDataStore/getAuthProvFromGUID'](this.$store.state.globalDataStore.selectedAuthProvGUID).saltForPasswordHashing
      var salt = atob(base64encodedSalt)
      var passwordhash = bcrypt.hashSync(masterSecretKey, salt)
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
