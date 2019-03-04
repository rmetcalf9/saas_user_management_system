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
        <TenantsTable
          :defaultDisplayedColumns="['Name', 'Description']"
          persistantSettingsSlot="tenantsSel"
          :clickSingleTenantCallback="clickSingleTenant"
          ref="tenantTable"
        />
        <div>&nbsp;</div>
        <q-btn
          v-if="multiselection"
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
import TenantsTable from '../components/TenantsTable'

export default {
  // name: 'TenantSelectionModal',
  components: {
    TenantsTable
  },
  props: [
    'title',
    'multiselection'
  ],
  data () {
    return {
      visible: false,
      filterText: ''
    }
  },
  methods: {
    clickSingleTenant (props) {
      this.visible = false
      this.$emit('ok', {
        selectedTenantList: [props.row]
      })
    },
    ok () {
      if (this.$refs.tenantTable.tableSelected.length === 0) {
        Notify.create('No Tenant selected')
        return
      }
      this.visible = false
      this.$emit('ok', {
        selectedTenantList: this.$refs.tenantTable.tableSelected
      })
    },
    cancel () {
      this.visible = false
    },
    launchDialog () {
      this.$store.commit('tablePersistStore/resetTableSettings', 'tenantsSel')
      this.$refs.tenantTable.tableSelected = []
      this.$refs.tenantTable.refresh()
      this.visible = true
    }
  }
}
</script>

<style>
</style>
