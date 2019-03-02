<template>
  <div>
    <q-btn
        color="primary"
        push
        @click="click"
      >Add Internal</q-btn>
  </div>
</template>

<script>
import { Notify } from 'quasar'

export default {
  // name: 'AuthAddInternal',
  props: [
    'person'
  ],
  data () {
    return {
    }
  },
  methods: {
    click () {
      Notify.create({color: 'positive', detail: 'TODO'})
    }
  }
}
</script>

<style>
</style>
