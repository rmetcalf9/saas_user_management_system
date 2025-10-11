<template>
  <q-page>
    <PersonsTable
      :defaultDisplayedColumns="['guid']"
      persistantSettingsSlot="personsMain"
      :clickSinglePersonCallback="clickSinglePerson"
    />
  </q-page>
</template>

<script>
import PersonsTable from '../components/PersonsTable'

export default {
  name: 'PagePersons',
  components: {
    PersonsTable
  },
  methods: {
    clickSinglePerson (props) {
      console.log('TODO check this')
      this.$router.push('/' + this.$route.params.tenantName + '/persons/' + props.row.PersonID)
    }
  }
}
</script>

<style>
</style>
