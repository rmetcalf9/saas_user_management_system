<template>
  <div>
    {{ authData.internalAuthProv.MenuText }}: {{ authData.auth.known_as }}
    <q-btn
        color="primary"
        push
        @click="resetPassword"
      >Reset Password</q-btn>
  </div>
</template>

<script>
import { Notify } from 'quasar'

export default {
  // name: 'AuthSecuritySettingsInternal',
  props: [
    'authData'
  ],
  data () {
    return {
    }
  },
  methods: {
    resetPassword () {
      Notify.create({color: 'positive', detail: 'TODO'})
    }
  }
}
</script>

<style>
</style>
