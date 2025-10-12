<template><q-page>
  <TenantsTable
    :defaultDisplayedColumns="['Name', 'Description']"
    persistantSettingsSlot="tenantsMain"
    :clickSingleTenantCallback="clickSingleTenant"
  />
</q-page></template>

<style>
</style>

<script>
import TenantsTable from '../components/TenantsTable'

export default {
  name: 'TenantsPage',
  components: {
    TenantsTable
  },
  methods: {
    clickSingleTenant (props) {
      this.$router.push('/' + this.$route.params.tenantName + '/tenants/' + props.row.Name)
    }
  }
}
</script>
