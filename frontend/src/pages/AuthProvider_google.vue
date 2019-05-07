<template>
  <div>
    <div class="fixed-center">
      TODO Log in with Google<BR />
      AuthProvInfo: {{ authProvInfo }}
    </div>
  </div>
</template>

<style>
</style>

<script>
// Notes: https://developers.google.com/identity/sign-in/web/server-side-flow
import {
  Notify
} from 'quasar'

export default {
  name: 'AuthProvider_internal',
  data () {
    return {
    }
  },
  computed: {
    tenantInfo () {
      return this.$store.state.globalDataStore.tenantInfo
    },
    authProvInfo () {
      return this.$store.getters['globalDataStore/getAuthProvFromGUID'](this.$store.state.globalDataStore.selectedAuthProvGUID)
    }
  },
  methods: {
  },
  mounted: function () {
    if (this.$store.state.globalDataStore.messagePendingDisplay !== null) {
      Notify.create({color: 'negative', detail: this.$store.state.globalDataStore.messagePendingDisplay})
      this.$store.commit('globalDataStore/setMessageDisplayed')
    }
  }
}
</script>
