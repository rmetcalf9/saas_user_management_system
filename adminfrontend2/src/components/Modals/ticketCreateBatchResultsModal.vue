<template>
  <q-dialog v-model="visible">
    <q-card style="width: 700px; max-width: 80vw; max-height: 90vh; display: flex; flex-direction: column;">
      <!-- Header -->
      <q-toolbar class="bg-primary text-white">
        <q-toolbar-title>
          {{ tenantName }} ticket batch created successfully ({{ ticketTypeName }})
        </q-toolbar-title>
        <q-btn flat v-close-popup round dense icon="close" />
      </q-toolbar>

      <!-- Scrollable Body -->
      <q-card-section style="flex: 1; overflow-y: auto;">
        <q-input
          v-model="resultsDisplay"
          filled
          type="textarea"
          readonly
          autogrow
        />

        <div class="q-mt-md">
          <q-separator spaced />
          {{ statsissued }} tickets issued,
          {{ statsreissued }} tickets reissued,
          {{ statsskipped }} foreign keys skipped
        </div>
      </q-card-section>

      <!-- Footer -->
      <q-separator />
      <q-card-actions
        align="right"
        class="bg-grey-2"
        style="position: sticky; bottom: 0; z-index: 1;"
      >
        <q-btn
          @click="close"
          color="primary"
          label="Close"
          class="q-ml-xs"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script>
// import { Notify } from 'quasar'
import adminfrontendfns from '../../adminfrontendfns.js'
import { useUserManagementClientStoreStore } from 'stores/saasUserManagementClientStore'

export default {
  name: 'TicketCreateBatchResults',
  setup () {
    const userManagementClientStoreStore = useUserManagementClientStoreStore()
    return {
      userManagementClientStoreStore
    }
  },
  data () {
    return {
      visible: false,
      callerData: {},
      tenantName: '',
      ticketTypeName: '',
      results: [],
      statsissued: 0,
      statsreissued: 0,
      statsskipped: 0,
      ticketTypeData: {},
      tenantData: {}
    }
  },
  methods: {
    getStyleComponent (styleName) {
      return this.$refs[styleName + 'UI']
    },
    close () {
      this.visible = false
      this.$emit('close', this.callerData)
    },
    launchDialog ({ ticketTypeData, callerData, createBatchResult, tenantData }) {
      const TTT = this
      this.callerData = callerData
      this.tenantName = ticketTypeData.tenantName
      this.ticketTypeName = ticketTypeData.ticketTypeName

      this.results = createBatchResult.data.results
      this.statsissued = createBatchResult.data.stats.issued
      this.statsreissued = createBatchResult.data.stats.reissued
      this.statsskipped = createBatchResult.data.stats.skipped

      this.ticketTypeData = ticketTypeData
      this.tenantData = tenantData

      TTT.visible = true // Must be visible for ref to exist
    }
  },
  computed: {
    resultsDisplay: {
      get () {
        const TTT = this
        return this.results
          .map(function (result) {
            return result.foreignKey + ', ' + adminfrontendfns.getURLforTicketGUID(TTT.userManagementClientStoreStore, result.ticketGUID, TTT.tenantName, TTT.ticketTypeData, TTT.tenantData)
          })
          .reduce(function (acculmator, result) {
            return acculmator + result + '\n'
          }, '')
      }
    }
  }
}
</script>

<style>
</style>
