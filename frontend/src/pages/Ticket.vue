
<template>
  <q-layout>
    <q-page-container>
      <q-page padding v-if="ticket.isUsable === 'NOTFOUND'">
        <div class="fixed-center">This ticket is not valid</div>
      </q-page>
      <q-page padding v-if="ticket.isUsable === 'ERROR'">
        <div class="fixed-center"><p>This ticket has an error</p>
        <q-btn
          @click="pressContinueToSite"
          color="primary"
          label="Continue"
          class = "float-right q-ml-xs"
        />
        </div>
      </q-page>
      <q-page padding v-if="ticket.isUsable === 'EXPIRED'">
        <div class="fixed-center">TODO EXPIRED TICKET</div>
      </q-page>
      <q-page padding v-if="ticket.isUsable === 'INVALID'">
        <div class="fixed-center"><p>This ticket has already been used or is invalid</p>
        <q-btn
          @click="pressContinueToSite"
          color="primary"
          label="Continue"
          class = "float-right q-ml-xs"
        />
        </div>
      </q-page>
      <q-page padding v-if="ticket.isUsable === 'USABLE'">
        <div class="fixed-center">
          <p class="text-h4">{{ ticket.ticketType.welcomeMessage.title }}</p>
          <p>{{ ticket.ticketType.welcomeMessage.body }}</p>
          <q-checkbox
            v-if="ticket.ticketType.welcomeMessage.agreementRequired"
            name="accept_agreement"
            v-model="acceptAgreement"
            label="Accept agreement"
          />
          <q-btn
            @click="pressOK"
            color="primary"
            :label="ticket.ticketType.welcomeMessage.okButtonText"
            class = "float-right q-ml-xs"
            :disabled='okDisabled'
          />
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<style>
</style>

<script>
import { Notify, Loading } from 'quasar'
import callbackHelper from '../callbackHelper'

export default {
  name: 'Ticket',
  data () {
    return {
      ticket: {
        isUsable: 'LOADING'
      },
      acceptAgreement: false
    }
  },
  methods: {
    pressOK () {
      this.$store.commit('globalDataStore/updateUsersystemReturnaddress', this.ticket.ticketType.postUseURL)
      // this.$store.commit('globalDataStore/STORETICKETINUSE', this.ticket) Had issues with value disappearing
      this.$store.commit('globalDataStore/STORETICKETINUSE', this.$route.params.ticketGUID)
      this.$router.replace('/' + this.$store.state.globalDataStore.tenantInfo.Name + '/selectAuth')
    },
    pressContinueToSite () {
      window.location.href = this.ticket.ticketType.postInvalidURL
    }
  },
  computed: {
    okDisabled () {
      if (!this.ticket.ticketType.welcomeMessage.agreementRequired) return false
      return !this.acceptAgreement
    }
  },
  mounted () {
    var TTT = this
    var callback = {
      ok: function (response) {
        TTT.ticket = response.data
        TTT.agreeselected = false
        Loading.hide()
      },
      error: function (response) {
        Loading.hide()
        if (typeof (response) !== 'undefined') {
          if (typeof (response.orig) !== 'undefined') {
            if (typeof (response.orig.response) !== 'undefined') {
              if (response.orig.response === 404) {
                TTT.ticket = {
                  isUsable: 'NOTFOUND'
                }
                return
              }
            }
          }
        }
        TTT.ticket = {
          isUsable: 'ERROR'
        }
        Notify.create({color: 'negative', message: 'Fetch ticket failed - ' + callbackHelper.getErrorFromResponse(response)})
      }
    }
    Loading.show()
    this.$store.dispatch('globalDataStore/callLoginAPI', {
      method: 'GET',
      path: '/tickets/' + this.$route.params.ticketGUID,
      callback: callback,
      postdata: undefined
    })
  }
}
</script>
