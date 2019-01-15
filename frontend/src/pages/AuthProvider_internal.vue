<template>
  <div class="fixed-center">
    <div>
      <q-input v-model="usernamePass.username" placeholder="Username" />
      <br>
      <q-input type="password" v-model="usernamePass.password" placeholder="Password" />
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
            TTT.$q.cookies.set('usersystemUserCredentials', response.data, {expires: 1, path: '/'})
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
      this.$store.dispatch('globalDataStore/callLoginAPI', {
        method: 'POST',
        path: '/authproviders',
        callback: callback,
        postdata: {
          credentialJSON: this.usernamePass,
          authProviderGUID: this.$store.state.globalDataStore.selectedAuthProvGUID
        }
      })
    }
  }
}
</script>
