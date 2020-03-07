<template>
  <q-dialog v-model="visible">
    <q-layout view="Lhh lpR fff" container class="bg-white" style="height: 400px; width: 700px; max-width: 80vw;">
      <q-header class="bg-primary">
        <q-toolbar>
          <q-toolbar-title>
            {{ tenantName }} ticket batch created sucessfully ({{ ticketTypeName }})
          </q-toolbar-title>
          <q-btn flat v-close-popup round dense icon="close" />
        </q-toolbar>
      </q-header>

      <q-page-container>
        <q-page padding>
          <q-input
            v-model="resultsDisplay"
            filled
            type="textarea"
            readonly
          />
          <hr>
          {{ statsissued }} tickets issued, {{ statsreissued }} tickets reissued, {{ statsskipped }} foreign keys skipped
          <div>&nbsp;</div>
          <q-btn
            @click="close"
            color="primary"
            label="Close"
            class = "float-right q-ml-xs"
          />
        </q-page>
      </q-page-container>

    </q-layout>
  </q-dialog>
</template>

<script>
// import { Notify } from 'quasar'

export default {
  name: 'TicketCreateBatchResults',
  data () {
    return {
      visible: false,
      callerData: {},
      tenantName: '',
      ticketTypeName: '',
      results: [],
      statsissued: 0,
      statsreissued: 0,
      statsskipped: 0
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
    launchDialog ({ ticketTypeData, callerData, createBatchResult }) {
      var TTT = this
      this.callerData = callerData
      this.tenantName = ticketTypeData.tenantName
      this.ticketTypeName = ticketTypeData.ticketTypeName

      this.results = createBatchResult.data.results
      this.statsissued = createBatchResult.data.stats.issued
      this.statsreissued = createBatchResult.data.stats.reissued
      this.statsskipped = createBatchResult.data.stats.skipped

      TTT.visible = true // Must be visible for ref to exist
    }
  },
  computed: {
    resultsDisplay: {
      get () {
        return this.results
          .map(function (result) {
            return result.foreignkey + ', http://TODOticketurl?ticket=' + result.ticketGUID
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
