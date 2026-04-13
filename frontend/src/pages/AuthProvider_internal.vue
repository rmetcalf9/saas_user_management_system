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
    <div>TODO</div>
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
    hasMutipleLoginMethods () {
      return this.tenantInfo.res.AuthProviders.length !== 0
    }
  },
  methods: {
    goBackToSelectAuthProviderScreen () {
      this.tenantInfoStore.clearAuthProvider()
      this.$router.push('/' + this.$route.params.tenantName + '/')
    }
  }
})
</script>

<style>
</style>
