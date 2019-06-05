<template>
  <div>
    <q-btn
        color="primary"
        push
        @click="click"
      >Add Internal</q-btn>
    <TenantSelectionModal
      ref="TenantSelectionModal"
      :title="'Select Tenant to Associate new auth with'"
      @ok="tenantSelected"
      :multiselection="false"
    />

  </div>
</template>

<script>
import { Notify } from 'quasar'
import TenantSelectionModal from '../components/TenantSelectionModal'
import bcrypt from 'bcryptjs'
import callbackHelper from '../callbackHelper'

export default {
  // name: 'AuthAddInternal',
  props: [
    'person'
  ],
  components: {
    TenantSelectionModal
  },
  data () {
    return {
    }
  },
  methods: {
    click () {
      this.$refs.TenantSelectionModal.launchDialog()
    },
    tenantSelected (res) {
      var TTT = this
      var tenant = res.selectedTenantList[0]
      this.$q.dialog({
        title: 'Username for new Internal Auth',
        message: 'Enter username for auth',
        prompt: {
          model: '',
          type: 'text'
        },
        cancel: true,
        color: 'secondary'
      }).then(username => {
        if (username === '') {
          Notify.create({color: 'negative', message: 'You must enter a username'})
          return
        }
        var selectedAuthProvider = 'undefined'
        for (var curAuthProviderIdx in tenant.AuthProviders) {
          if (tenant.AuthProviders[curAuthProviderIdx].Type === 'internal') {
            selectedAuthProvider = tenant.AuthProviders[curAuthProviderIdx]
          }
        }
        if (selectedAuthProvider === 'undefined') {
          Notify.create({color: 'negative', message: 'Selected tenant dosen\'t have an internal auth provider'})
          return
        }
        var salt = selectedAuthProvider.saltForPasswordHashing
        var randPassword1 = Array(1).fill('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz').map(function (x) { return x[Math.floor(Math.random() * x.length)] }).join('')
        var randPassword2 = Array(14).fill('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$!.{}()').map(function (x) { return x[Math.floor(Math.random() * x.length)] }).join('')
        var randPassword = randPassword1 + randPassword2
        var passwordhash = bcrypt.hashSync(username + ':' + randPassword + ':AG44', atob(salt))

        var createAuthPostData = {
          personGUID: TTT.person.guid,
          tenantName: tenant.Name,
          authProviderGUID: selectedAuthProvider.guid,
          credentialJSON: {
            username: username,
            password: passwordhash
          }
        }
        var callback = {
          ok: function (response) {
            TTT.$emit('updateMaster', {})
            TTT.$q.dialog({
              title: 'New Internal Auth account created',
              message: 'Username: ' + username + ' Password: ' + randPassword
            })
          },
          error: function (error) {
            Notify.create('Create Auth failed - ' + callbackHelper.getErrorFromResponse(error))
          }
        }
        TTT.$store.dispatch('globalDataStore/callAdminAPI', {
          path: '/auths',
          method: 'post',
          postdata: createAuthPostData,
          callback: callback,
          curPath: TTT.$router.history.current.path
        })
      })
    }
  }
}
</script>

<style>
</style>
