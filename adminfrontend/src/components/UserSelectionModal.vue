<template>
  <q-dialog v-model="visible">
    <q-layout view="Lhh lpR fff" container class="bg-white" style="width: 700px; max-width: 80vw;">
      <q-header class="bg-primary">
        <q-toolbar>
          <q-toolbar-title>
            {{ title }}
          </q-toolbar-title>
          <q-btn flat v-close-popup round dense icon="close" />
        </q-toolbar>
      </q-header>

      <q-page-container>
        <q-page padding>
          <UsersTable
            :defaultDisplayedColumns="['known_as']"
            persistantSettingsSlot="usersSel"
            :clickSingleUserCallback="clickSingleUser"
            ref="userTable"
          />
          <div>&nbsp;</div>
          <q-btn
            @click="ok"
            color="primary"
            label="Ok"
            class = "float-right q-ml-xs"
          />
          <q-btn
            @click="cancel"
            label="Cancel"
            class = "float-right"
          />
        </q-page>
      </q-page-container>

    </q-layout>
  </q-dialog>
</template>

<script>
import { Notify } from 'quasar'
import UsersTable from '../components/UsersTable'

export default {
  // name: 'UserSelectionModal',
  components: {
    UsersTable
  },
  props: [
    'title'
  ],
  data () {
    return {
      visible: false,
      filterText: ''
    }
  },
  methods: {
    clickSingleUser (props) {
      this.visible = false
      this.$emit('ok', {
        selectedUserList: [props.row]
      })
    },
    ok () {
      if (this.$refs.userTable.tableSelected.length === 0) {
        Notify.create('No user selected')
        return
      }
      this.visible = false
      this.$emit('ok', {
        selectedUserList: this.$refs.userTable.tableSelected
      })
    },
    cancel () {
      this.visible = false
    },
    launchDialog () {
      var TTT = this
      TTT.visible = true // Must be visible for ref to exist
      setTimeout(function () {
        TTT.$store.commit('tablePersistStore/resetTableSettings', 'usersSel')
        TTT.$refs.userTable.tableSelected = []
        TTT.$refs.userTable.refresh()
      }, 5)
    }
  }
}
</script>

<style>
</style>
