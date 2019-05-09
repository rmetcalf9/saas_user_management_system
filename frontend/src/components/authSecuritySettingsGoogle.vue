<template>
  <div>
    {{ authData.internalAuthProv.MenuText }}: {{ authData.auth.known_as }}
  </div>
</template>

<script>

export default {
  // name: 'AuthSecuritySettingsGoogle',
  props: [
    'authData',
    'loggedInPerson'
  ],
  data () {
    return {
    }
  },
  computed: {
  },
  methods: {
  }
}
</script>

<style>
</style>
