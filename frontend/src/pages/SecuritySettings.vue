<template>
  <div class="fixed-center text-center">
    <p class="text-faded">Security Settings Page</p>
    <q-btn
      color="secondary"
      style="width:200px;"
      @click="goBackClick"
    >Go back</q-btn>
  </div>
</template>

<script>
import { Notify, Loading } from 'quasar'
import callbackHelper from '../callbackHelper'

function getEmptyUserSettingsData () {
  return {
    a: 'a'
  }
}

export default {
  name: 'SecuritySettings',
  data () {
    return {
      UserSettingsData: getEmptyUserSettingsData()
    }
  },
  methods: {
    goBackClick () {
      window.location.href = this.$store.state.globalDataStore.usersystemReturnaddress
    },
    refreshUserSettingsData () {
      var TTT = this
      var callback = {
        ok: function (response) {
          Loading.hide()
          TTT.UserSettingsData = response.data
        },
        error: function (error) {
          Loading.hide()
          Notify.create('Person query failed - ' + callbackHelper.getErrorFromResponse(error))
          TTT.UserSettingsData = getEmptyUserSettingsData()
        }
      }
      Loading.show()
      this.$store.dispatch('globalDataStore/callCurrentAuthAPI', {
        path: '/currentAuthInfo',
        method: 'get',
        postdata: null,
        callback: callback,
        curPath: this.$router.history.current.path,
        headers: undefined
      })
    }
  },
  mounted () {
    this.refreshUserSettingsData()
  }
}
</script>
