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
import CryptoJS from 'crypto-js'

function get32BytesFromSalt (salt) {
  var retBytes = ''
  for (let i = 0; i < 32; i++) {
    retBytes += salt[i % salt.length]
  }
  // idx = x % len(salt)
  // retBytes = retBytes + salt[idx:(idx+1)]
  return retBytes
}

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
      this.$refs.usernameDialogInput.focus()
    },
    returnError (errMsg) {
      Loading.hide()
      this.ldapLoginDialogModel.visible = false
      this.$emit('completeError', this.authProvData, 'Link with LDAP error - ' + errMsg)
    },
    okLoginDialog () {
      var TTT = this
      // console.log('this.authProvData.saltForPasswordHashing:', this.authProvData.saltForPasswordHashing)
      // console.log('atob:', atob(this.authProvData.saltForPasswordHashing))
      var salt32Bytes = get32BytesFromSalt(atob(this.authProvData.saltForPasswordHashing))
      var iv = CryptoJS.lib.WordArray.random(16)
      console.log('saltBytes:', salt32Bytes)
      console.log('iv:', iv)
      // TTT.$emit('completeOK', TTT.authProvData, credentialJSON)

      console.log('C:', CryptoJS)

      // var MODE = CryptoJS.mode.CFB(CryptoJS.pad.ZeroPadding)

      // var options = {iv: iv, asBytes: true, mode: MODE}
      var options = {iv: iv, asBytes: true}

      var encryptedPassword = CryptoJS.AES.encrypt(this.ldapLoginDialogModel.password, salt32Bytes, {options})

      var credentialJSON = {
        username: this.ldapLoginDialogModel.username,
        password: btoa(encryptedPassword.ciphertext.toString()),
        ivx: btoa(iv.toString())
      }
      // console.log('credentialJSON:', credentialJSON)
      TTT.$emit('completeOK', TTT.authProvData, credentialJSON)
    },
    cancelLoginDialog () {
      this.ldapLoginDialogModel.visible = false
    }

  }
}
</script>

<style>
</style>
