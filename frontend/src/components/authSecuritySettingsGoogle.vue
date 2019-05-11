<template>
  <div>
    <q-item-tile label>{{ authData.internalAuthProv.MenuText }}</q-item-tile>
    <q-item-tile sublabel>
      {{ authData.auth.known_as }}
      <q-btn
        push
        v-if="authData.canUnlink"
        @click="$emit('unlink')"
      >Unlink</q-btn>
    </q-item-tile>
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
