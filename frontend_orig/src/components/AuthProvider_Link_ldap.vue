<template>
  <div>
    <q-btn
      push
      @click="linkClick()"
    >{{ authProvData.LinkText }}</q-btn>

    <q-dialog v-model="ldapLoginDialogModel.visible">
      <q-layout view="Lhh lpR fff" container class="bg-white" style="height: 400px; width: 700px; max-width: 80vw;">
        <q-header class="bg-primary">
          <q-toolbar>
            <q-toolbar-title>
              LDAP Login
            </q-toolbar-title>
            <q-btn flat v-close-popup round dense icon="close" />
          </q-toolbar>
        </q-header>
        <q-page-container>
          <q-page padding>
            <q-input
              v-model="ldapLoginDialogModel.username"
              ref="usernameDialogInput" helper="Username"
              label="Username"
              :label-width="3"
            />
            <q-input type="password"
              v-model="ldapLoginDialogModel.password"
              label="Password"
              @keyup.enter="okLoginDialog"
              :label-width="3"
            />
            <q-btn
              @click="okLoginDialog"
              color="primary"
              label="Ok"
              class = "float-right q-ml-xs"
            />
            <q-btn
              @click="cancelLoginDialog"
              label="Cancel"
              class = "float-right"
            />
          </q-page>
        </q-page-container>
      </q-layout>
    </q-dialog>

  </div>
</template>

<script>
import {
  Loading
} from 'quasar'
import ldapShared from '../ldap_shared.js'

export default {
  // name: 'AuthSecuritySettingsLdap',
  props: [
    'authProvData'
  ],
  data () {
    return {
      ldapLoginDialogModel: {
        visible: false,
        username: '',
        password: ''
      }
    }
  },
  methods: {
    linkClick () {
      this.ldapLoginDialogModel = {
        visible: true,
        username: '',
        password: ''
      }
      var TTT = this
      this.$nextTick(function () {
        TTT.$refs.usernameDialogInput.focus()
      })
    },
    returnError (errMsg) {
      Loading.hide()
      this.ldapLoginDialogModel.visible = false
      this.$emit('completeError', this.authProvData, 'Link with LDAP error - ' + errMsg)
    },
    okLoginDialog () {
      var TTT = this

      var credentialJSON = ldapShared.getCredentialDict(this.authProvData.saltForPasswordHashing, this.ldapLoginDialogModel.username, this.ldapLoginDialogModel.password)

      Loading.show()
      TTT.$emit('completeOK', TTT.authProvData, credentialJSON)
      this.ldapLoginDialogModel.visible = false
    },
    cancelLoginDialog () {
      this.ldapLoginDialogModel.visible = false
    }

  }
}
</script>

<style>
</style>
