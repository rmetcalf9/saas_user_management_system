<template>
  <q-page>
    <TenantsTable
      :defaultDisplayedColumns="['Name', 'Description', '...']"
      persistantSettingsSlot="tenantsMain"
      :clickSingleTenantCallback="clickSingleTenant"
    />
  </q-page>
</template>

<script>
import TenantsTable from '../components/TenantsTable'

export default {
  name: 'PageTenants',
  components: {
    TenantsTable
  },
  methods: {
    clickSingleTenant (props) {
      this.$router.push('/' + this.$route.params.tenantName + '/tenants/' + props.Name)
    }
  }
}
</script>

<style>
</style>
