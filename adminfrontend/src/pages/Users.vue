<template>
  <q-page>
    <UsersTable
      :defaultDisplayedColumns="['known_as', 'TenantRoles']"
    />
  </q-page>
</template>

<style>
</style>

<script>
import UsersTable from '../components/UsersTable'

export default {
  name: 'PageUsers',
  components: {
    UsersTable
  }
}
</script>
