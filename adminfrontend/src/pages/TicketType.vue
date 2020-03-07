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

  <q-list >
    <q-item clickable v-ripple highlight @click.native="editTicketType">
      <q-item-section >
        <q-item-label>Tenant Name: {{ ticketTypeData.ticketTypeName }}</q-item-label>
        <q-item-label caption>{{ ticketTypeData.description }}</q-item-label>
      </q-item-section>
      <q-item-section avatar>
        <q-icon color="primary" name="mode_edit" />
      </q-item-section>
    </q-item>
  </q-list>
  <q-list>
    <q-expansion-item
      expand-separator
      label="More ticket type information"
    >
      <q-item>
        <q-item-section >
          <q-item-label>Enabled:</q-item-label>
          <q-item-label caption v-if="ticketTypeData.enabled">Tickets of this type can currently be used</q-item-label>
          <q-item-label caption v-if="!ticketTypeData.enabled">Tickets of this type are not usable</q-item-label>
        </q-item-section>
      </q-item>
      <q-item>
        <q-item-section >
          <q-item-label>Allow User Creation:</q-item-label>
          <q-item-label caption v-if="ticketTypeData.allowUserCreation">Users without accounts can use this ticket to create an account</q-item-label>
          <q-item-label caption v-if="!ticketTypeData.allowUserCreation">Only users with an account can use this ticket</q-item-label>
        </q-item-section>
      </q-item>
      <q-item>
        <q-item-section >
          <q-item-label>Valid Duration</q-item-label>
          <q-item-label caption>Tickets created are valid for {{ ticketTypeData.issueDuration }} hours. ({{ ticketTypeData.issueDuration / 24 }} days)</q-item-label>
        </q-item-section>
      </q-item>
      <q-item>
        <q-item-section >
          <q-item-label>Post usage URLs</q-item-label>
          <q-item-label caption>After successful use users are sent to: <a :href="ticketTypeData.postUseURL">{{ ticketTypeData.postUseURL }}</a></q-item-label>
          <q-item-label caption>After unsuccessful use users are sent to: <a :href="ticketTypeData.postInvalidURL">{{ ticketTypeData.postUseURL }}</a></q-item-label>
        </q-item-section>
      </q-item>

      <q-item>
        <q-item-section >
          <q-item-label>Welcome Message</q-item-label>
          <q-item-label caption>Title: {{ ticketTypeData.welcomeMessage.title }}</q-item-label>
          <q-item-label caption>Body: {{ ticketTypeData.welcomeMessage.body }}</q-item-label>
          <q-item-label caption v-if="ticketTypeData.welcomeMessage.agreementRequired">User must agree in order to proceed</q-item-label>
          <q-item-label caption v-if="!ticketTypeData.welcomeMessage.agreementRequired">User not prompted for agreement</q-item-label>
          <q-item-label caption>Ok button text: {{ ticketTypeData.welcomeMessage.okButtonText }}</q-item-label>
        </q-item-section>
      </q-item>

      <q-item>
        <q-item-section >
          <q-item-label>Roles granted by tickets of this type</q-item-label>
          <q-item-label caption><q-chip size="10px" v-for="curVal in ticketTypeData.roles" :key=curVal>{{ curVal }}</q-chip></q-item-label>
        </q-item-section>
      </q-item>
      <q-item>
        <q-item-section >
          <q-item-label>Ticket Type metadata</q-item-label>
          <q-item-label caption>{{ ticketTypeData.metadata }}</q-item-label>
        </q-item-section>
      </q-item>
    </q-expansion-item>
  </q-list>
  <TicketsTable
    :defaultDisplayedColumns="['Name', 'Description']"
    persistantSettingsSlot="ticketsMain"
    :selectedTenantName="$route.params.selTenantNAME"
    :selectedTicketTypeID="$route.params.selTicketTypeID"
    :ticketTypeData="ticketTypeData"
  />

  <strictConfirmation
    ref="strictConfirmation"
    @ok="clickStrictConfirmationModalOK"
  />
  <editTicketTypeModal
    ref="editTicketTypeModal"
    @ok="clickEditTicketTypeModalModalOK"
  />

</q-page>
</template>

<style>
</style>

<script>
import { Notify, Loading } from 'quasar'
import callbackHelper from '../callbackHelper'
import strictConfirmation from '../components/Modals/StrictConfirmation.vue'
import editTicketTypeModal from '../components/Modals/editTicketTypeModal.vue'

import TicketsTable from '../components/TicketsTable'

function getEmptyTicketTypeData () {
  return {
    welcomeMessage: {
      title: '',
      body: '',
      agreementRequired: false,
      okButtonText: ''
    }
  }
}

export default {
  name: 'TicketTypePage',
  components: {
    strictConfirmation,
    editTicketTypeModal,
    TicketsTable
  },
  data () {
    return {
      ticketTypeData: getEmptyTicketTypeData()
    }
  },
  methods: {
    editTicketType () {
      this.$refs.editTicketTypeModal.launchDialog({
        title: 'Edit ' + this.$route.params.selTenantNAME + ' ticket type',
        callerData: { editing: true, id: this.ticketTypeData.id, tenantName: this.ticketTypeData.tenantName, metadata: this.ticketTypeData.metadata },
        editingExisting: true,
        initialValues: this.ticketTypeData
      })
    },
    clickEditTicketTypeModalModalOK (callerData, objData) {
      var TTT = this
      objData.id = callerData.id
      objData.tenantName = callerData.tenantName
      objData.metadata = callerData.metadata
      var callback = {
        ok: function (response) {
          Loading.hide()
          Notify.create({color: 'positive', message: 'Ticket Type Updated'})
          setTimeout(function () {
            TTT.refreshTicketTypeData()
          }, 400)
        },
        error: function (error) {
          Loading.hide()
          Notify.create({color: 'negative', message: 'Request failed - ' + callbackHelper.getErrorFromResponse(error)})
        }
      }
      Loading.show()
      this.$store.dispatch('globalDataStore/callAdminAPI', {
        path: '/tenants/' + this.$route.params.selTenantNAME + '/tickettypes/' + objData.id,
        method: 'post',
        postdata: objData,
        callback: callback,
        curPath: this.$router.history.current.path,
        headers: undefined
      })
    },
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
