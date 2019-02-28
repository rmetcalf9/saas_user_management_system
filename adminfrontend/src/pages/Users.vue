<template>
  <q-page>
    <UsersTable
      :defaultDisplayedColumns="['known_as', 'TenantRoles']"
      persistantSettingsSlot="usersMain"
      :clickSingleUserCallback="clickSingleUser"
    />
  </q-page>
</template>

<style>
</style>

<script>
import UsersTable from '../components/UsersTable'

export default {
  name: 'PageUsers',
  methods: {
    clickSingleUser (props) {
      this.$router.push('/' + this.$route.params.tenantName + '/users/' + props.row.UserID)
    }
  },
  components: {
    UsersTable
  }
}
</script>
