<template>
  <div class="row q-gutter-md">
    <div class="col">
      <div>
        Tenant: {{ authData.tenantName }}
      </div>
      <div>
        Provider Type: Internal
      </div>
      <div>
        Prompt: {{ authProviderPrompt.MenuText }}
      </div>
      <div>
        AuthUserKey: {{ authData.AuthUserKey }}
      </div>
    </div>
    <div class="col flex flex-column justify-end">
      <div>
        <q-btn
            color="primary"
            push
            @click="resetPassword"
          >Reset Password</q-btn>
      </div>
    </div>
  </div>
</template>

<script>
import { Notify, Loading } from 'quasar'
import callbackHelper from '../../callbackHelper'
import saasApiClientCallBackend from '../../saasAPiClientCallBackend'
import { useUserManagementClientStoreStore } from 'stores/saasUserManagementClientStore'
import bcrypt from 'bcryptjs'

function getEmptyTenantData () {
  return {
    AuthProviders: []
  }
}

export default {
  name: 'AuthDisplayInternal',
  props: [
    'person',
    'authData'
  ],
  emits: ['refresh'],
  setup () {
    const userManagementClientStoreStore = useUserManagementClientStoreStore()
    return {
      userManagementClientStoreStore
    }
  },
  data () {
    return {
      tenantData: getEmptyTenantData()
    }
  },
  computed: {
    tenantName () {
      // This is the LOGGED in tenant name - not the one for the auths we are viewing
      return this.$route.params.tenantName
    },
    authProviderPrompt () {
      const TTT = this
      const thisAuthProvs = this.tenantData.AuthProviders.filter(function (x) {
        return x.guid === TTT.authData.AuthProviderGUID
      })
      if (thisAuthProvs.length !== 1) {
        return 'Error'
      }
      return thisAuthProvs[0]
    }
  },
  methods: {
    resetPassword () {
      const TTT = this
      const thisAuthProvs = this.tenantData.AuthProviders.filter(function (x) {
        return x.guid === TTT.authData.AuthProviderGUID
      })
      if (thisAuthProvs.length !== 1) {
        Notify.create({
          color: 'negative',
          message: 'Unable to determine auth providers'
        })
        console.log('Expected only one result:', thisAuthProvs)
        return
      }
      const thisAuthProv = thisAuthProvs[0]
      console.log('AuthProviderGUID', this.authData.AuthProviderGUID)
      const userSuffix = JSON.parse(thisAuthProv.ConfigJSON).userSufix

      function textBeforeSuffix (searchString, userSuffix) {
        const index = searchString.indexOf(userSuffix)
        if (index === -1) {
          return searchString
        }
        return searchString.slice(0, index)
      }
      const userName = textBeforeSuffix(this.authData.AuthUserKey, userSuffix)

      const salt = thisAuthProv.saltForPasswordHashing
      const randPassword1 = Array(1).fill('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz').map(function (x) { return x[Math.floor(Math.random() * x.length)] }).join('')
      const randPassword2 = Array(14).fill('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$!.{}()').map(function (x) { return x[Math.floor(Math.random() * x.length)] }).join('')
      const randPassword = randPassword1 + randPassword2
      const passwordhash = bcrypt.hashSync(userName + ':' + randPassword + ':AG44', atob(salt))

      console.log('sss', thisAuthProv)

      const createAuthPostData = {
        personGUID: TTT.person.guid,
        tenantName: this.tenantData.Name,
        authProviderGUID: thisAuthProv.guid,
        credentialJSON: {
          username: userName,
          password: passwordhash
        }
      }

      const base64encodedkey = btoa(this.authData.AuthUserKey)
      const callback = {
        ok: function (response) {
          TTT.resetPasswordStage2({
            createAuthPostData,
            randPassword
          })
        },
        error: function (error) {
          Notify.create({ color: 'negative', message: 'Delete auth failed ( ' + this.authData.AuthUserKey + ') - ' + callbackHelper.getErrorFromResponse(error) })
        }
      }
      saasApiClientCallBackend.callApi({
        prefix: 'admin',
        router: this.$router,
        store: this.userManagementClientStoreStore,
        path: '/' + TTT.tenantName + '/auths/' + base64encodedkey,
        method: 'delete',
        postdata: null,
        callback
      })
    },
    resetPasswordStage2 ({ createAuthPostData, randPassword }) {
      const TTT = this
      const callback = {
        ok: function (response) {
          TTT.$emit('refresh')
          TTT.$q.dialog({
            title: 'New Internal Auth account created',
            message: 'Username: ' + createAuthPostData.credentialJSON.username + ' Password: ' + randPassword
          })
        },
        error: function (error) {
          Notify.create({ color: 'negative', message: 'Create Auth failed - ' + callbackHelper.getErrorFromResponse(error) + ' The user has been lost and needs to be recreated' })
        }
      }
      saasApiClientCallBackend.callApi({
        prefix: 'admin',
        router: this.$router,
        store: this.userManagementClientStoreStore,
        path: '/' + TTT.tenantName + '/auths',
        method: 'post',
        postdata: createAuthPostData,
        callback
      })
    },
    refreshTenantData () {
      const tenantNameToLoad = this.authData.tenantName
      const TTT = this
      const callback = {
        ok: function (response) {
          Loading.hide()
          TTT.tenantData = response.data
        },
        error: function (error) {
          Loading.hide()
          Notify.create({ color: 'negative', message: 'Tenant query failed - ' + callbackHelper.getErrorFromResponse(error) })
          TTT.tenantData = getEmptyTenantData()
        }
      }
      Loading.show()
      saasApiClientCallBackend.callApi({
        prefix: 'admin',
        router: this.$router,
        store: this.userManagementClientStoreStore,
        path: '/' + TTT.tenantName + '/tenants/' + tenantNameToLoad,
        method: 'get',
        postdata: undefined,
        callback
      })
    },
    refresh () {
      this.refreshTenantData()
    }
  },
  mounted () {
    this.refresh()
  }
}
</script>

<style>
</style>
