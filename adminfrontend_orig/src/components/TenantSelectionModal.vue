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
        </q-page>
      </q-page-container>
    </q-layout>
  </q-dialog>
<!--
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
  </q-modal>-->
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
      var tmp = this.$refs.tenantTable
      if (tmp.tableSelected.length === 0) {
        Notify.create('No Tenant selected')
        return
      }
      this.visible = false
      this.$emit('ok', {
        selectedTenantList: tmp.tableSelected
      })
    },
    cancel () {
      this.visible = false
    },
    launchDialog () {
      var TTT = this
      TTT.visible = true
      setTimeout(function () {
        TTT.$store.commit('tablePersistStore/resetTableSettings', 'tenantsSel')
        TTT.$refs.tenantTable.tableSelected = []
        TTT.$refs.tenantTable.refresh()
      }, 5)
    }
  }
}
</script>

<style>
</style>
