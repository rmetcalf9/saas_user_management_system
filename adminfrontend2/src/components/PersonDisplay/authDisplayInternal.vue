<template>
  <div class="row q-gutter-md">
    <div class="col">
      <div>
        Provider: {{ authData.tenantName }} - Internal
      </div>
      <div>
        AuthUserKey:{{ authData.AuthUserKey }}
      </div>
    </div>
    <div class="col flex flex-column justify-end">
      <div>
        <q-btn
            color="primary"
            push
            @click="resetPassword"
          >Reset Password</q-btn>
      </div>
    </div>
  </div>
</template>

<script>
import { Notify } from 'quasar'

export default {
  name: 'AuthDisplayInternal',
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
      // console.log('ss', this.authData)
      // console.log('AuthProviderGUID', this.authData.AuthProviderGUID)
      Notify.create({ color: 'positive', message: 'To reset the password remove this auth and add another one with type internal' })
    }
  }
}
</script>

<style>
</style>
