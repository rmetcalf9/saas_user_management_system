<template>
  <div class="fixed-center">
    <div>
      <div class="row">
        <h2>Security Settings</h2>
      </div>
      <p>Your authentication methods:</p>
      <q-list >
        <div v-for="curVal in currentTenantAuthsWithAuthProvData" :key=curVal.AuthUserKey>
          <AuthProvSecuritySettingsInternal
            :authData="curVal"
            :loggedInPerson="UserSettingsData.loggedInUser"
            @unlink="unlinkClick(curVal)"
             v-if="curVal.auth.AuthProviderType === 'internal'"
          />
          <AuthProvSecuritySettingsGoogle
            :authData="curVal"
            :loggedInPerson="UserSettingsData.loggedInUser"
            @unlink="unlinkClick(curVal)"
             v-if="curVal.auth.AuthProviderType === 'google'"
          />
        </div>
      </q-list>
      <div v-if="unusedTenantAuthsWithAuthProvData.length > 0">
        <p>Link new authentication methods:</p>
        <q-list >
          <div v-for="curVal in unusedTenantAuthsWithAuthProvData" :key=curVal.AuthUserKey>
            <AuthProvLinkInternal
              :authProvData="curVal"
              @completeError="linkCompleteError"
              @completeOK="linkCompleteOK"
              v-if="curVal.Type === 'internal'"
            />
            <AuthProvLinkGoogle
              :authProvData="curVal"
              @completeError="linkCompleteError"
              @completeOK="linkCompleteOK"
              v-if="curVal.Type === 'google'"
            />
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
import AuthProvSecuritySettingsInternal from '../components/AuthProvider_SecuritySettings_internal'
import AuthProvLinkInternal from '../components/AuthProvider_Link_internal'

import AuthProvSecuritySettingsGoogle from '../components/AuthProvider_SecuritySettings_google'
import AuthProvLinkGoogle from '../components/AuthProvider_Link_google'

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
    'AuthProvSecuritySettingsInternal': AuthProvSecuritySettingsInternal,
    'AuthProvLinkInternal': AuthProvLinkInternal,
    'AuthProvSecuritySettingsGoogle': AuthProvSecuritySettingsGoogle,
    'AuthProvLinkGoogle': AuthProvLinkGoogle
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
            canUnlink: (canAnyUnlink && internalAuthProvObj.AllowUnlink && (TTT.UserSettingsData.currentlyUsedAuthKey !== a.AuthUserKey)),
            authMethodInUse: (TTT.UserSettingsData.currentlyUsedAuthKey === a.AuthUserKey)
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
    linkCompleteError (authProv, errMsg) {
      Notify.create(errMsg)
    },
    linkCompleteOK (authProv, credentialJSON) {
      var TTT = this
      var linkRequestPostData = {
        credentialJSON: credentialJSON,
        authProviderGUID: authProv.guid
      }
      var callback = {
        ok: function (response) {
          Loading.hide()
          TTT.refreshUserSettingsData()
          Notify.create({color: 'positive', message: 'New Login method added'})
        },
        error: function (response) {
          console.log('response:', response)
          Notify.create('Link error - ' + callbackHelper.getErrorFromResponse(response))
        }
      }
      TTT.$store.dispatch('globalDataStore/callCurrentAuthAPI', {
        path: '/loggedInUserAuths/link',
        method: 'post',
        postdata: linkRequestPostData,
        callback: callback,
        curPath: this.$router.history.current.path,
        headers: undefined,
        router: this.$router
      })
    },
    unlinkClick (authData) {
      var TTT = this
      TTT.$q.dialog({
        title: 'Confirm',
        message: 'Are you sure you want to unlink accout "' + authData.auth.known_as + '"',
        ok: {
          push: true,
          label: 'Yes - Unlink'
        },
        cancel: {
          push: true,
          label: 'Cancel'
        }
        // preventClose: false,
        // noBackdropDismiss: false,
        // noEscDismiss: false
      }).onOk(() => {
        TTT.unlinkClickSure(authData)
      })
    },
    unlinkClickSure (authData) {
      var TTT = this
      var callback = {
        ok: function (response) {
          Loading.hide()
          TTT.refreshUserSettingsData()
          Notify.create({color: 'positive', message: 'Login method remvoed'})
        },
        error: function (error) {
          Loading.hide()
          Notify.create('Unlink request failed - ' + callbackHelper.getErrorFromResponse(error))
        }
      }
      Loading.show()
      this.$store.dispatch('globalDataStore/callCurrentAuthAPI', {
        path: '/loggedInUserAuths/delete',
        method: 'post',
        postdata: { AuthKey: authData.AuthUserKey },
        callback: callback,
        curPath: this.$router.history.current.path,
        headers: undefined,
        router: this.$router
      })
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
