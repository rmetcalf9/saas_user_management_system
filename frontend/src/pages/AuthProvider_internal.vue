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
          ref="userNameInput"
          @keyup="textBoxKeyUp"
        />
        <q-input
          type="password"
          v-model="usernamePass.password"
          placeholder="Password"
          @keyup="textBoxKeyUp"
        />
        <div class="text-center group authprovider_internal_loginbuttons">
          <q-btn
            color="primary"
            push
            @click="usernamePassLogin"
          >
            Login
          </q-btn>
          <q-btn
            v-if='selectedAuthProvider.AllowUserCreation && tenantInfo.res.AllowUserCreation'
            color="secondary"
            push
            @click="createAccountClick"
          >
            Create Account
          </q-btn>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script>
import { defineComponent } from 'vue'
// import { Notify } from 'quasar'
import DisplayInputMessage from '../components/displayInputMessage.vue'
import { useTenantInfoStore } from 'stores/tenantInfo'

export default defineComponent({
  name: 'IndexPage',
  components: {
    DisplayInputMessage
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
    textBoxKeyUp (e) {
      if (e.key === 'Enter') {
        this.usernamePassLogin()
      }
    },
    usernamePassLogin () {
      console.log('TODO process login')
    }
  }
})
</script>

<style>
.authprovider_internal_loginbuttons {
  padding: 10px;
}
</style>
