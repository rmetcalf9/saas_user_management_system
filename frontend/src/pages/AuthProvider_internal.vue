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
        <q-input
          v-model="usernamePass.username"
          placeholder="Username"
          autocomplete="username"
          name="username"
          ref="userNameInput"
          @keyup="textBoxKeyUp"
        />
        <q-input
          v-model="usernamePass.password"
          placeholder="Password"
          autocomplete="current-password"
          name="password"
          :type="isPwd ? 'password' : 'text'"
          @keyup="textBoxKeyUp"
        >
          <template v-slot:append>
            <q-icon
              :name="isPwd ? 'visibility_off' : 'visibility'"
              class="cursor-pointer"
              @click="isPwd = !isPwd"
            />
          </template>
        </q-input>
        <div class="text-center group authprovider_internal_loginbuttons row">
          <q-btn
            color="primary"
            push
            @click="usernamePassLogin"
          >
            Login
          </q-btn>
          <CreateAccountButton
            v-if='selectedAuthProvider.AllowUserCreation && tenantInfo.res.AllowUserCreation'
            @postCreateLogin="postCreateLogin"
          />
        </div>
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
import bcrypt from 'bcryptjs'
import ProcessLoginResponse from '../components/processLoginResponse'
import CreateAccountButton from '../components/internal/createAccountButton'
import frontendFns from '../frontendFns.js'

export default defineComponent({
  name: 'IndexPage',
  components: {
    DisplayInputMessage, ProcessLoginResponse, CreateAccountButton
  },
  setup () {
    const tenantInfoStore = useTenantInfoStore()
    return { tenantInfoStore }
  },
  data () {
    return {
      isPwd: true,
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
    postCreateLogin (eventData) {
      this.processLogin(eventData.username, eventData.password)
    },
    usernamePassLogin () {
      this.processLogin(this.usernamePass.username, this.usernamePass.password)
    },
    processLogin (username, password) {
      const TTT = this
      if (!this.tenantInfoStore.isAuthProviderSelected) {
        Notify.create({ color: 'negative', message: 'No AuthProvGUID selected - you shouldn\'t navigate here directly' })
        return
      }
      const passwordhash = bcrypt.hashSync(username + ':' + password + ':AG44', atob(TTT.selectedAuthProvider.saltForPasswordHashing))
      const credentialJson = {
        username,
        password: passwordhash
      }
      const callback = {
        ok: function (response) {
          Loading.hide()
        },
        error: function (response) {
          Loading.hide()
          Notify.create({ color: 'negative', message: 'Login Failed' })
        }
      }
      Loading.show()
      frontendFns.callLoginAPI({
        credentialJSON: credentialJson,
        callback,
        processLoginResponseInstance: TTT.$refs.processLoginResponseInstance,
        registering: false,
        router: this.$router
      })
    }
  }
})
</script>

<style>
.authprovider_internal_loginbuttons {
  padding: 10px;
}
</style>
