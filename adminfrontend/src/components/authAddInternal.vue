<template>
  <div>
    <q-btn
        color="primary"
        push
        @click="click"
      >Add Internal Auth</q-btn>

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
      var possibleAuthProviders = tenant.AuthProviders.filter(function (x) { return x.Type === 'internal' })
      if (possibleAuthProviders.length === 0) {
        Notify.create({color: 'negative', message: 'Selected tenant dosen\'t have an internal auth provider'})
        return
      }
      if (possibleAuthProviders.length === 1) {
        TTT.tenantAndAuthProvSelected(tenant, possibleAuthProviders[0])
      } else {
        console.log('possibleAuthProviders', possibleAuthProviders)
        this.$q.dialog({
          title: 'Options',
          message: 'Choose your options',
          options: {
            type: 'radio',
            model: 0,
            // inline: true
            items: possibleAuthProviders.map(function (x, idx) {
              return {
                label: x.MenuText,
                value: idx
              }
            })
            // items: [
            //  { label: 'Option 1', value: 'opt1', color: 'secondary' },
            //  { label: 'Option 2', value: 'opt2' },
            //  { label: 'Option 3', value: 'opt3' }
            // ]
          },
          cancel: true,
          persistent: true
        }).onOk(data => {
          TTT.tenantAndAuthProvSelected(tenant, possibleAuthProviders[data])
        })
      }
    },
    tenantAndAuthProvSelected (tenant, selectedAuthProvider) {
      var TTT = this
      this.$q.dialog({
        title: 'Username for new Internal Auth',
        message: 'Enter username for auth',
        prompt: {
          model: '',
          type: 'text'
        },
        cancel: true,
        color: 'secondary'
      }).onOk(username => {
        if (username === '') {
          Notify.create({color: 'negative', message: 'You must enter a username'})
          return
        }
        TTT.tenantAndAuthProvAndUsernameSelected(tenant, selectedAuthProvider, username)
      })
    },
    tenantAndAuthProvAndUsernameSelected (tenant, selectedAuthProvider, username) {
      var TTT = this
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
          Notify.create({color: 'negative', message: 'Create Auth failed - ' + callbackHelper.getErrorFromResponse(error)})
        }
      }
      TTT.$store.dispatch('globalDataStore/callAdminAPI', {
        path: '/auths',
        method: 'post',
        postdata: createAuthPostData,
        callback: callback,
        curPath: TTT.$router.history.current.path
      })
    }

  }
}
</script>

<style>
</style>
