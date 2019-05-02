<template>
  <div>
    {{ authData.internalAuthProv.MenuText }}: {{ authData.auth.known_as }}
    <q-btn
        color="primary"
        push
        @click="resetPasswordClick"
      >Reset Password</q-btn>
    <q-modal v-model="resetPasswordDialogVisible" :content-css="{minWidth: '40vw', minHeight: '40vh'}">
      <q-modal-layout>
        <q-toolbar slot="header">
          <q-btn
            color="primary"
            flat
            round
            dense
            icon="keyboard_arrow_left"
            @click="cancelResetPasswordDialog"
          />
          <q-toolbar-title>
            Reset password for {{ authData.internalAuthProv.MenuText }}: {{ authData.auth.known_as }}
          </q-toolbar-title>
        </q-toolbar>
        <div class="layout-padding">
          <q-field helper="Must match your current password" label="Current Password" :label-width="3">
            <q-input type="password" v-model="dialogData.current_password" ref="someTextBoxDataInput1"/>
          </q-field>
          <q-field :helper="passwordERRORMessage" label="New Password" :label-width="3" :error="passwordERROR">
            <q-input type="password" v-model="dialogData.password" ref="someTextBoxDataInput2"/>
          </q-field>
          <q-field helper="New password repeat" label="New Password Repeat" :label-width="3" :error="passwordERROR">
            <q-input type="password" v-model="dialogData.password_repeat" @keyup.enter="okResetPasswordDialog" ref="someTextBoxDataInput3"/>
          </q-field>
          <div>&nbsp;</div>
          <q-btn
            @click="okResetPasswordDialog"
            color="primary"
            label="Ok"
            class = "float-right q-ml-xs"
          />
          <q-btn
            @click="cancelResetPasswordDialog"
            label="Cancel"
            class = "float-right"
          />
        </div>
      </q-modal-layout>
    </q-modal>
  </div>
</template>

<script>
import { Notify, Loading } from 'quasar'
import callbackHelper from '../callbackHelper'
import frontendFns from '../frontendFns.js'

export default {
  // name: 'AuthSecuritySettingsInternal',
  props: [
    'authData',
    'loggedInPerson'
  ],
  data () {
    return {
      resetPasswordDialogVisible: false,
      dialogData: {
        current_password: '',
        password: '',
        password_repeat: ''
      }
    }
  },
  computed: {
    passwordERROR () {
      return (this.passwordERRORMessage !== 'Password')
    },
    passwordERRORMessage () {
      return frontendFns.passwordERRORMessage(this.dialogData.password, this.dialogData.password_repeat)
    }
  },
  methods: {
    resetPasswordClick () {
      this.dialogData.current_password = ''
      this.dialogData.password = ''
      this.dialogData.password_repeat = ''
      this.resetPasswordDialogVisible = true
      this.$refs.someTextBoxDataInput1.focus()
    },
    okResetPasswordDialog () {
      if (this.passwordERROR) {
        Notify.create(this.passwordERRORMessage)
        return
      }
      this.resetPasswordDialogVisible = false

      var callback = {
        ok: function (response) {
          Loading.hide()
          Notify.create({color: 'positive', detail: 'Password reset sucessful'})
        },
        error: function (error) {
          Loading.hide()
          Notify.create('Reset Password failed - ' + callbackHelper.getErrorFromResponse(error))
        }
      }
      Loading.show()
      console.log('authData:', this.authData)
      console.log('loggedInPerson:', this.loggedInPerson)
      // var passwordhash = bcrypt.hashSync(this.createAccountDialogModel.username + ':' + this.createAccountDialogModel.password + ':AG44', atob(this.authProvInfo.saltForPasswordHashing))
      var postData = {
        authProviderGUID: this.authData.internalAuthProv.guid,
        credentialJSON: {
          username: 'this.createAccountDialogModel.username',
          password: 'passwordhash'
        },
        operationName: 'ResetPassword',
        operationData: {}
      }
      this.$store.dispatch('globalDataStore/callCurrentAuthAPI', {
        path: '/currentAuthInfo',
        method: 'post',
        postdata: postData,
        callback: callback,
        curPath: this.$router.history.current.path,
        headers: undefined,
        router: this.$router
      })
    },
    cancelResetPasswordDialog () {
      this.resetPasswordDialogVisible = false
    }
  }
}
</script>

<style>
</style>
