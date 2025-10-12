<template>
<q-dialog v-model="visible">
  <q-card style="width: 700px; max-width: 80vw; max-height: 90vh; display: flex; flex-direction: column;">
    <!-- Header -->
    <q-toolbar class="bg-primary text-white">
      <q-toolbar-title>
        {{ title }}
      </q-toolbar-title>
      <q-btn flat v-close-popup round dense icon="close" />
    </q-toolbar>

    <!-- Scrollable Body -->
    <q-card-section style="flex: 1; overflow-y: auto;">
      <TenantsTable
        :defaultDisplayedColumns="['Name', 'Description']"
        :persistantSettingsSlot="tablePersistSettingsSlot"
        :clickSingleTenantCallback="clickSingleTenant"
        ref="tenantTable"
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
        v-if="multiselection"
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
import TenantsTable from '../components/TenantsTable'
import { useTablePersistSettingsStore } from 'stores/tablePersistSettingsStore'

export default {
  name: 'TenantSelectionModal',
  components: {
    TenantsTable
  },
  props: [
    'title',
    'multiselection'
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
      return 'tenantsSel'
    }
  },
  methods: {
    clickSingleTenant (props) {
      this.visible = false
      this.$emit('ok', {
        selectedTenantList: [props]
      })
    },
    ok () {
      const tmp = this.$refs.tenantTable
      if (tmp.tableSelected.length === 0) {
        Notify.create('No Tenant selected')
        return
      }
      this.visible = false
      console.log('AAAA', tmp)
      this.$emit('ok', {
        selectedTenantList: tmp.tableSelected
      })
    },
    cancel () {
      this.visible = false
    },
    launchDialog () {
      const TTT = this
      TTT.visible = true
      setTimeout(function () {
        TTT.tablePersistSettingsStore.resetTableSettings(this.tablePersistSettingsSlot)
        TTT.$refs.tenantTable.tableSelected = []
        TTT.$refs.tenantTable.refresh()
      }, 5)
    }
  }
}
</script>

<style>
</style>
