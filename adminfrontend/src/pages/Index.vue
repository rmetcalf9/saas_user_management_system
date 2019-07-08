<template>
  <q-page class="flex flex-center">
    <table><tr><td align="center">
    <img alt="Quasar logo" src="~assets/quasar-logo-full.svg">
    </td></tr><tr><td>
    <h2>Welcome to {{ this.$route.params.tenantName }}</h2>
    </td></tr></table>
  </q-page>
</template>

<style>
</style>

<script>
export default {
  name: 'PageIndex'
}
</script>
