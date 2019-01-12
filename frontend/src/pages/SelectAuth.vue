<template>
  <div class="fixed-center">
    <div>
      <div class="row">
        <div class="col">
          <p>How do you want to verify who you are?</p>
        </div>
      </div>
      <div class="row">
        <div v-for="curVal in tenantInfo.AuthProviders" :key=curVal.guid>
          <q-btn class="col q-ma-sm" :label="curVal.MenuText" @click="clickHandler1(curVal)"/>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
</style>

<script>
export default {
  name: 'SelectAuth',
  data () {
    return {
    }
  },
  computed: {
    tenantInfo () {
      return this.$store.state.globalDataStore.tenantInfo
    }
  },
  methods: {
    clickHandler1 (authProvider) {
      this.$store.commit('globalDataStore/updateSelectedAuthProvGUID', authProvider.guid)
      this.$router.replace('/' + this.$store.state.globalDataStore.tenantInfo.Name + '/AuthProvider/' + authProvider.Type)
    }
  }
}
</script>
