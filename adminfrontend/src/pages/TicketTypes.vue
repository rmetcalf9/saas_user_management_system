<template>
  <q-page>
    <TicketTypesTable
      :defaultDisplayedColumns="['Name', 'Description']"
      persistantSettingsSlot="ticketTypesMain"
      :selectedTenantName="$route.params.selTenantNAME"
    />
  </q-page>
</template>

<style>
</style>

<script>
import TicketTypesTable from '../components/TicketTypesTable'

export default {
  name: 'TicketTypesPage',
  components: {
    TicketTypesTable
  },
  data () {
    return {
    }
  },
  mounted () {
    this.$store.commit('globalDataStore/SET_PAGE_TITLE', 'Ticket types for ' + this.$route.params.selTenantNAME)
  }
}
</script>
