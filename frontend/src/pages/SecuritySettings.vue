<template>
  <div class="fixed-center">
    <div>
      <div class="row">
        <h2>Security Settings</h2>
      </div>
      <div class="row">
        <div class="col">
          <p>Your authentication methods:</p>
        </div>
      </div>
      <div class="row">
        <div v-for="curVal in currentTenantAuthsWithAuthProvData" :key=curVal.AuthUserKey>
          {{ curVal }}
        </div>
      </div>
    </div>
    <div>
      <div class="row">
        <q-btn
          color="primary"
          style="width:200px;"
          @click="goBackClick"
        >Go back</q-btn>
      </div>
    </div>
  </div>
</template>

<script>
import { Notify, Loading } from 'quasar'
import callbackHelper from '../callbackHelper'

function getEmptyUserSettingsData () {
  return {
    loggedInPerson: {
      personAuths: [
      ]
    }
  }
}

export default {
  name: 'SecuritySettings',
  data () {
    return {
      UserSettingsData: getEmptyUserSettingsData()
    }
  },
  computed: {
    currentTenantAuthsWithAuthProvData () {
      var TTT = this
      return TTT.UserSettingsData.loggedInPerson.personAuths.filter(function (a) { return a.tenantName === TTT.$store.state.globalDataStore.tenantInfo.Name }).map(
        function (a) {
          return {
            AuthUserKey: a.AuthUserKey,
            auth: a,
            internalAuthProv: TTT.$store.state.globalDataStore.tenantInfo.AuthProviders.filter(function (b) {
              return b.guid === a.AuthProviderGUID
            })[0]
          }
        }
      )
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
