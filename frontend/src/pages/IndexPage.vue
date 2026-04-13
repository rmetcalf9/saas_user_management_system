<template>
  <q-page class="flex flex-center indexpage-main">
    <DisplayInputMessage />
    <div v-if="usersystemReturnaddress === ''">
      <div>Error - no return address passed</div>
    </div>
    <div v-if="usersystemReturnaddress !== ''">
      <div v-if="tenantInfo.loading">
        Loading...
      </div>
      <div v-if="!tenantInfo.loading">
        <div v-if="tenantInfo.errored">
          Error Loading info
        </div>
        <div v-if="!tenantInfo.errored">
          <div class="col">
            <div v-html="tenantInfo.res.TenantBannerHTML" />
            <p>{{ tenantInfo.res.SelectAuthMessage }}</p>
          </div>
          <div class="row">
            <div v-for="authProvider in tenantInfo.res.AuthProviders"
              :key="authProvider.guid"
            >
              <q-btn class="col q-ma-sm" :label="authProvider.MenuText" @click="clickAuth(authProvider)"/>
            </div>
          </div>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script>
import { defineComponent } from 'vue'
import { Notify } from 'quasar'
import { useUserManagementClientStoreStore } from 'stores/saasUserManagementClientStore'
import { useTenantInfoStore } from 'stores/tenantInfo'
import { useInputParamsStore } from 'stores/inputParams'
import DisplayInputMessage from '../components/displayInputMessage.vue'

// import saasAPiClientCallBackend from '../saasAPiClientCallBackend.js'
// import callbackHelper from '../callbackHelper'

export default defineComponent({
  name: 'IndexPage',
  components: {
    DisplayInputMessage
  },
  setup () {
    const userManagementClientStoreStore = useUserManagementClientStoreStore()
    const tenantInfoStore = useTenantInfoStore()
    const inputParamsStore = useInputParamsStore()
    return { userManagementClientStoreStore, tenantInfoStore, inputParamsStore }
  },
  data () {
    return {
    }
  },
  computed: {
    usersystemReturnaddress () {
      return this.inputParamsStore.usersystemReturnaddress
    },
    usersystemMessage () {
      return this.inputParamsStore.usersystemMessage
    },
    tenantInfo () {
      return this.tenantInfoStore.getInfo({
        router: this.$router,
        tenantName: this.$route.params.tenantName,
        skipcache: false
      })
    }
  },
  methods: {
    clickAuth (authProvider) {
      const targets = {
        internal: '/auth/internal'
      }
      if (!Object.keys(targets).includes(authProvider.Type)) {
        console.log('Uknown type', authProvider)
        Notify.create({
          color: 'negative',
          message: 'ERROR - unknown auth type ' + authProvider.Type
        })
        return
      }
      this.tenantInfoStore.selectAuthProvider({
        selectedAuthProvider: authProvider
      })
      this.$router.push('/' + this.$route.params.tenantName + targets[authProvider.Type])
    }
  },
  mounted () {
  }
})
</script>

<style>
.indexpage-main {
  padding: 10px;
}
</style>
