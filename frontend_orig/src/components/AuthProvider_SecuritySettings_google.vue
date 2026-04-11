<template>
  <q-item>
    <q-item-section>
      <q-item-label v-if="authData.authMethodInUse">{{ authData.internalAuthProv.MenuText }} **Current**</q-item-label>
      <q-item-label v-if="!authData.authMethodInUse">{{ authData.internalAuthProv.MenuText }}</q-item-label>
      <q-item-label caption>
        {{ authData.auth.known_as }}
        <q-btn
          push
          v-if="authData.canUnlink"
          @click="$emit('unlink')"
        >Unlink</q-btn>
      </q-item-label>
    </q-item-section>
  </q-item>
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
