<template>
<q-dialog v-model="visible">
  <q-card
    style="width: 700px; max-width: 80vw; max-height: 90vh; display: flex; flex-direction: column;"
  >
    <!-- Header -->
    <q-toolbar class="bg-primary text-white">
      <q-toolbar-title>
        {{ title }}
      </q-toolbar-title>
      <q-btn flat v-close-popup round dense icon="close" />
    </q-toolbar>

    <!-- Scrollable Content -->
    <q-card-section style="flex: 1; overflow-y: auto;">
      <UsersTable
        :defaultDisplayedColumns="['known_as']"
        persistantSettingsSlot="usersSel"
        :clickSingleUserCallback="clickSingleUser"
        ref="userTable"
      />
    </q-card-section>

    <!-- Footer -->
    <q-separator />
    <q-card-actions
      align="right"
      class="bg-grey-2"
      style="position: sticky; bottom: 0; z-index: 1;"
    >
      <q-btn
        @click="ok"
        color="primary"
        label="Ok"
        class="q-ml-xs"
      />
      <q-btn
        @click="cancel"
        label="Cancel"
      />
    </q-card-actions>
  </q-card>
</q-dialog>

</template>

<script>
import { Notify } from 'quasar'
import UsersTable from '../components/UsersTable'
import { useTablePersistSettingsStore } from 'stores/tablePersistSettingsStore'

export default {
  name: 'UserSelectionModal',
  components: {
    UsersTable
  },
  props: [
    'title'
  ],
  setup () {
    const tablePersistSettingsStore = useTablePersistSettingsStore()
    return {
      tablePersistSettingsStore
    }
  },
  data () {
    return {
      visible: false,
      filterText: ''
    }
  },
  computed: {
    tablePersistSettingsSlot () {
      return 'usersSel'
    }
  },
  methods: {
    clickSingleUser (props) {
      this.visible = false
      this.$emit('ok', {
        selectedUserList: [props]
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
      const TTT = this
      TTT.visible = true // Must be visible for ref to exist
      setTimeout(function () {
        TTT.tablePersistSettingsStore.resetTableSettings(this.tablePersistSettingsSlot)
        TTT.$refs.userTable.tableSelected = []
        TTT.$refs.userTable.refresh()
      }, 5)
    }
  }
}
</script>

<style>
</style>
