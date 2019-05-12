<template>
  <div class="fixed-center">
    <div>
      <div class="row">
        <h2>Security Settings</h2>
      </div>
      <p>Your authentication methods:</p>
      <q-list >
        <div v-for="curVal in currentTenantAuthsWithAuthProvData" :key=curVal.AuthUserKey>
          <q-item>
            <q-item-main v-if="curVal.auth.AuthProviderType === 'internal'">
              <AuthSecuritySettingsInternal
                :authData="curVal"
                :loggedInPerson="UserSettingsData.loggedInUser"
                @unlink="unlinkClick(curVal)"
              />
            </q-item-main>
          </q-item>
          <q-item>
            <q-item-main v-if="curVal.auth.AuthProviderType === 'google'">
              <AuthSecuritySettingsGoogle
                :authData="curVal"
                :loggedInPerson="UserSettingsData.loggedInUser"
                @unlink="unlinkClick(curVal)"
              />
            </q-item-main>
          </q-item>
        </div>
      </q-list>
      <div v-if="unusedTenantAuthsWithAuthProvData.length > 0">
        <p>Link new authentication methods:</p>
        <q-list >
          <div v-for="curVal in unusedTenantAuthsWithAuthProvData" :key=curVal.AuthUserKey>
            <q-item>
              <q-item-main>
                <q-btn
                  push
                  @click="linkClick"
                >{{ curVal.LinkText }}</q-btn>
              </q-item-main>
            </q-item>
          </div>
        </q-list>
      </div>
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
import AuthSecuritySettingsInternal from '../components/authSecuritySettingsInternal'
import AuthSecuritySettingsGoogle from '../components/authSecuritySettingsGoogle'

function getEmptyUserSettingsData () {
  return {
    loggedInPerson: {
      personAuths: [
      ]
    },
    loggedInUser: {
    }
  }
}

export default {
  name: 'SecuritySettings',
  components: {
    'AuthSecuritySettingsInternal': AuthSecuritySettingsInternal,
    'AuthSecuritySettingsGoogle': AuthSecuritySettingsGoogle
  },
  data () {
    return {
      UserSettingsData: getEmptyUserSettingsData()
    }
  },
  computed: {
    currentTenantAuthsWithAuthProvData () {
      var TTT = this
      var userAuthItems = TTT.UserSettingsData.loggedInPerson.personAuths.filter(function (a) { return a.tenantName === TTT.$store.state.globalDataStore.tenantInfo.Name })
      var canAnyUnlink = (userAuthItems.length > 1)
      return userAuthItems.map(
        function (a) {
          var internalAuthProvObj = TTT.$store.state.globalDataStore.tenantInfo.AuthProviders.filter(function (b) {
            return b.guid === a.AuthProviderGUID
          })[0]
          return {
            AuthUserKey: a.AuthUserKey,
            auth: a,
            internalAuthProv: internalAuthProvObj,
            canUnlink: (canAnyUnlink && internalAuthProvObj.AllowUnlink && (TTT.UserSettingsData.currentlyUsedAuthKey !== a.AuthUserKey))
          }
        }
      )
    },
    unusedTenantAuthsWithAuthProvData () {
      var TTT = this
      return TTT.$store.state.globalDataStore.tenantInfo.AuthProviders.filter(function (b) {
        if (!b.AllowLink) {
          return false
        }
        return !TTT.UserSettingsData.loggedInPerson.personAuths.map(function (c) {
          return c.AuthProviderGUID
        }).includes(b.guid)
      })
    }
  },
  methods: {
    unlinkClick (authData) {
      console.log(authData)
      Notify.create('TODO - unlink')
    },
    linkClick () {
      Notify.create('TODO')
    },
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
        headers: undefined,
        router: this.$router
      })
    }
  },
  mounted () {
    this.refreshUserSettingsData()
  }
}
</script>
