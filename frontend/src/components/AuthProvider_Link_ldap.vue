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

      // console.log('saltForPasswordHashing:', this.authProvData.saltForPasswordHashing)
      // console.log('atob:', atob(this.authProvData.saltForPasswordHashing))

      // var passphraseBase64 = btoa('tyttt')
      var passphraseBase64 = this.authProvData.saltForPasswordHashing
      var passphrase = get32BytesFromSalt(atob(passphraseBase64))
      var plainText = this.ldapLoginDialogModel.password
      // var IV = CryptoJS.lib.WordArray.random(16)
      var IV = CryptoJS.enc.Base64.parse('/0iT3mjRzasxO1pTQggZCg==')
      var passphraseWordArray = CryptoJS.enc.Base64.parse(btoa(passphrase))

      var encOptions = {
        iv: IV,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
      }
      var encrypted = CryptoJS.AES.encrypt(plainText, passphraseWordArray, encOptions)

      // console.log("Result IV = ", IV.toString(CryptoJS.enc.Base64))
      // console.log("Result cipherText = ", encrypted.ciphertext.toString(CryptoJS.enc.Base64))

      var credentialJSON = {
        username: this.ldapLoginDialogModel.username,
        password: encrypted.ciphertext.toString(CryptoJS.enc.Base64),
        iv: IV.toString(CryptoJS.enc.Base64)
      }

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
