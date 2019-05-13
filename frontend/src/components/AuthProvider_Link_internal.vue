<template>
  <div>
    <q-btn
      push
      @click="linkClick(authProvData)"
    >{{ authProvData.LinkText }}</q-btn>
  </div>
</template>

<script>
export default {
  // name: 'AuthSecuritySettingsInternal',
  props: [
    'authProvData'
  ],
  data () {
    return {
    }
  },
  methods: {
    linkClick (authProvData) {
      var TTT = this
      // TTT.$emit('completeError', authProvData, 'Link to Internal Auth Not Done')
      var credentialJSON = {}
      TTT.$emit('completeOK', authProvData, credentialJSON)
    }
  }
}
</script>

<style>
</style>
