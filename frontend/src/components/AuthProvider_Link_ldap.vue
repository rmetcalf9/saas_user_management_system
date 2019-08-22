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

      console.log('CryptoJS:', CryptoJS)

      // msgString is expected to be Utf8 encoded
      var iv = CryptoJS.lib.WordArray.random(16)
      var key = get32BytesFromSalt(atob(this.authProvData.saltForPasswordHashing))
      var msgString = this.ldapLoginDialogModel.password

      var encrypted = CryptoJS.AES.encrypt(msgString, key, {
        iv: iv
      })

      var credentialJSON = {
        username: this.ldapLoginDialogModel.username,
        password: encrypted.ciphertext.toString(CryptoJS.enc.Base64),
        iv: iv.toString(CryptoJS.enc.Base64)
      }

      // console.log('this.authProvData.saltForPasswordHashing:', this.authProvData.saltForPasswordHashing)
      // console.log('atob:', atob(this.authProvData.saltForPasswordHashing))
      // TTT.$emit('completeOK', TTT.authProvData, credentialJSON)

      // var options = {iv: iv, asBytes: true, mode: MODE}
      // var options = {iv: iv, asBytes: true}

      // var encryptedObj = CryptoJS.AES.encrypt(this.ldapLoginDialogModel.password, salt32Bytes, {options})

      // console.log('encryptedObj', encryptedObj)
      // console.log('saltBytes:', salt32Bytes)
      // console.log('iv BASE64:', iv.toString(CryptoJS.enc.Base64))
      // console.log('cipherText:', encryptedObj.toString())

      // var KEY = CryptoJS.enc.Base64.parse(btoa(get32BytesFromSalt(atob(this.authProvData.saltForPasswordHashing))))
      // var IV = CryptoJS.lib.WordArray.random(16)
      // var plaintext = this.ldapLoginDialogModel.password

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
