<template>
  <q-page>
    <TicketTypesTable
      :defaultDisplayedColumns="['Name', 'Description']"
      persistantSettingsSlot="ticketTypesMain"
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
  }
}
</script>
