<template>
  <div>
    <q-item-tile sublabel >
      Provider: Internal, Key:{{ authData.AuthUserKey }}
    <q-btn
        color="primary"
        push
        @click="resetPassword"
      >Reset Password</q-btn>
    </q-item-tile>
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
