<template>
  <q-page class="flex flex-center">
    TODO - ticket type
  </q-page>
</template>

<style>
</style>

<script>
export default {
  name: 'TicketTypePage',
  mounted () {
    this.$store.commit('globalDataStore/SET_PAGE_TITLE', this.$route.params.selTenantNAME + ' ticket type')
  }
}
</script>
