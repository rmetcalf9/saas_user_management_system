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
  Notify
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
      var callback = {
        ok: function (response) {
          console.log(response)
          // TODO Decide if we got a JWTToken back or an identity selection list
          //   either forward to the JWTToken setting page or
          //   the identity selection page
        },
        error: function (response) {
          Notify.create('Login Failed')
        }
      }
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
