<template>
  <q-page>
    <UsersTable
      :defaultDisplayedColumns="['known_as', 'TenantRoles']"
      persistantSettingsSlot="usersMain"
      :clickSingleUserCallback="clickSingleUser"
    />
  </q-page>
</template>

<script>
import UsersTable from '../components/UsersTable'

export default {
  name: 'PageUsers',
  components: {
    UsersTable
  },
  methods: {
    clickSingleUser (props) {
      this.$router.push('/' + this.$route.params.tenantName + '/users/' + props.UserID)
    }
  }
}
</script>

<style>
</style>
