<template>
<q-page>
  <q-page-sticky position="bottom-right" :offset="[50, 50]">
    <q-btn
      color="negative"
      class="fixed"
      round
      @click="deleteTicketType"
      icon="delete"
    ></q-btn>
  </q-page-sticky>

  {{ ticketTypeData }}
  <strictConfirmation
    ref="strictConfirmation"
    @ok="clickStrictConfirmationModalOK"
  />
</q-page>
</template>

<style>
</style>

<script>
import { Notify, Loading } from 'quasar'
import callbackHelper from '../callbackHelper'
import strictConfirmation from '../components/Modals/StrictConfirmation.vue'

function getEmptyTicketTypeData () {
  return {
  }
}

export default {
  name: 'TicketTypePage',
  components: {
    strictConfirmation
  },
  data () {
    return {
      ticketTypeData: getEmptyTicketTypeData()
    }
  },
  methods: {
    deleteTicketType () {
      var TTT = this
      this.$refs.strictConfirmation.launchDialog(
        'This will delete this ticket type and all it\'s tickets - including used ones! To proceed type ' + TTT.ticketTypeData.ticketTypeName + ' and press ok',
        'Permanently delete ' + TTT.ticketTypeData.ticketTypeName + ' from ' + TTT.ticketTypeData.tenantName,
        TTT.ticketTypeData.ticketTypeName,
        { fn: TTT.deleteTicketTypeAfterStrictOK, name: TTT.ticketTypeData.ticketTypeName, id: TTT.ticketTypeData.id, tenantName: TTT.ticketTypeData.tenantName, objectversion: TTT.ticketTypeData.metadata.objectVersion }
      )
    },
    clickStrictConfirmationModalOK (callerData) {
      callerData.fn(callerData)
    },
    deleteTicketTypeAfterStrictOK (callerData) {
      var TTT = this
      var callback = {
        ok: function (response) {
          Notify.create({color: 'positive', message: 'Ticket Type ' + callerData.name + ' deleted'})
          TTT.$router.push('/' + TTT.$route.params.tenantName + '/tenants/' + callerData.tenantName + '/tickettypes')
        },
        error: function (error) {
          Notify.create({color: 'negative', message: 'Delete Ticket Type failed - ' + callbackHelper.getErrorFromResponse(error)})
        }
      }
      TTT.$store.dispatch('globalDataStore/callAdminAPI', {
        path: '/tenants/' + callerData.tenantName + '/tickettypes/' + callerData.id + '?objectversion=' + callerData.objectversion,
        method: 'delete',
        postdata: null,
        callback: callback,
        curPath: TTT.$router.history.current.path,
        headers: {}
      })
    },
    refreshTicketTypeData () {
      var TTT = this
      var callback = {
        ok: function (response) {
          Loading.hide()
          TTT.ticketTypeData = response.data
        },
        error: function (error) {
          Loading.hide()
          Notify.create({color: 'negative', message: 'Ticker Type failed - ' + callbackHelper.getErrorFromResponse(error)})
          TTT.ticketTypeData = getEmptyTicketTypeData()
        }
      }
      Loading.show()
      this.$store.dispatch('globalDataStore/callAdminAPI', {
        path: '/tenants/' + this.$route.params.selTenantNAME + '/tickettypes/' + this.$route.params.selTicketTypeID,
        method: 'get',
        postdata: null,
        callback: callback,
        curPath: this.$router.history.current.path,
        headers: undefined
      })
    }
  },
  mounted () {
    this.$store.commit('globalDataStore/SET_PAGE_TITLE', this.$route.params.selTenantNAME + ' ticket type')
    this.refreshTicketTypeData()
  }
}
</script>
