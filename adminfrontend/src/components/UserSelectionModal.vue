<template>
  <q-modal v-model="visible" :content-css="{minWidth: '40vw', minHeight: '80vh'}">
    <q-modal-layout>
      <q-toolbar slot="header">
          <q-btn
          color="primary"
          flat
          round
          dense
          icon="keyboard_arrow_left"
          @click="cancel"
        />
        <q-toolbar-title>{{ title }}</q-toolbar-title>
      </q-toolbar>

      <div class="layout-padding">
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
      </div>
    </q-modal-layout>
  </q-modal>
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
      this.$store.commit('tablePersistStore/resetTableSettings', 'usersSel')
      this.$refs.userTable.tableSelected = []
      this.$refs.userTable.refresh()
      this.visible = true
    }
  }
}
</script>

<style>
</style>
