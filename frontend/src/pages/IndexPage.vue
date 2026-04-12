<template>
  <q-page class="flex flex-center">
    <div v-if="tenantInfo.loading">
      Loading...
    </div>
    <div v-if="!tenantInfo.loading">
      <div v-if="tenantInfo.errored">
        Error Loading info
      </div>
      <div v-if="!tenantInfo.errored">
        tenantInfo: {{ tenantInfo }}
      </div>
    </div>
  </q-page>
</template>

<script>
import { defineComponent } from 'vue'
// import { Notify } from 'quasar'
import { useUserManagementClientStoreStore } from 'stores/saasUserManagementClientStore'
import { useTenantInfoStore } from 'stores/tenantInfo'
// import saasAPiClientCallBackend from '../saasAPiClientCallBackend.js'
// import callbackHelper from '../callbackHelper'

export default defineComponent({
  name: 'IndexPage',
  setup () {
    const userManagementClientStoreStore = useUserManagementClientStoreStore()
    const tenantInfoStore = useTenantInfoStore()
    return { userManagementClientStoreStore, tenantInfoStore }
  },
  data () {
    return {
    }
  },
  computed: {
    tmp () {
      return this.userManagementClientStoreStore.isLoggedIn
    },
    tenantInfo () {
      console.log('computing aaa')
      return this.tenantInfoStore.getInfo({
        router: this.$router,
        tenantName: this.$route.params.tenantName,
        skipcache: false
      })
    }
  },
  methods: {
  },
  mounted () {
  }
})
</script>
