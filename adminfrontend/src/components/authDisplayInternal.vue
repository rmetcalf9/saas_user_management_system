<template>
  <div>
      Provider: {{ authData.tenantName }} - Internal, Key:{{ authData.AuthUserKey }}
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
  // name: 'AuthDisplayInternal',
  props: [
    'person',
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
