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
import { useGlobalValsStore } from 'stores/globalValsStore'
import TicketTypesTable from '../components/TicketTypesTable'

export default {
  name: 'PageTicketTypes',
  components: {
    TicketTypesTable
  },
  setup () {
    const globalValsStore = useGlobalValsStore()
    return {
      globalValsStore
    }
  },
  methods: {
  },
  mounted () {
    this.globalValsStore.pageTitle = 'Ticket types for ' + this.$route.params.selTenantNAME
  }
}
</script>
