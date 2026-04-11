<template>
  <q-item>
    <q-item-section>
      <q-item-label v-if="authData.authMethodInUse">{{ authData.internalAuthProv.MenuText }} **Current**</q-item-label>
      <q-item-label v-if="!authData.authMethodInUse">{{ authData.internalAuthProv.MenuText }}</q-item-label>
      <q-item-label caption>
        {{ authData.auth.known_as }}
        <q-btn
            color="primary"
            push
            @click="resetPasswordClick"
          >Reset Password</q-btn>
        <q-btn
          push
          v-if="authData.canUnlink"
          @click="$emit('unlink')"
        >Unlink</q-btn>

      <q-dialog v-model="resetPasswordDialogVisible">
        <q-layout view="Lhh lpR fff" container class="bg-white" style="height: 400px; width: 700px; max-width: 80vw;">
          <q-header class="bg-primary">
            <q-toolbar>
              <q-toolbar-title>
                Reset password for {{ authData.internalAuthProv.MenuText }}: {{ authData.auth.known_as }}
              </q-toolbar-title>
              <q-btn flat v-close-popup round dense icon="close" />
            </q-toolbar>
          </q-header>

          <q-page-container>
            <q-page padding>
              <q-input
                type="password"
                v-model="dialogData.current_password"
                ref="someTextBoxDataInput1"
                error-message="Must match your current password"
                label="Current Password"
                :label-width="3"
              />
              <q-input
                type="password"
                v-model="dialogData.password"
                ref="someTextBoxDataInput2"
                label="New Password"
                :label-width="3"
                :error-message="passwordERRORMessage"
                :error="passwordERROR"
              />
              <q-input
                type="password"
                v-model="dialogData.password_repeat"
                @keyup.enter="okResetPasswordDialog"
                ref="someTextBoxDataInput3"
                label="New Password Repeat"
                :label-width="3"
                error-message="New password repeat"
                :error="passwordERROR"
              />
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
            </q-page>
          </q-page-container>

        </q-layout>
      </q-dialog>

      </q-item-label>
    </q-item-section>
  </q-item>
</template>

<script>
import { Notify, Loading } from 'quasar'
import callbackHelper from '../callbackHelper'
import frontendFns from '../frontendFns.js'
import bcrypt from 'bcryptjs'

function getUsernameFromAuthUserKey (authUserKey, authProvData) {
  // console.log('getUsernameFromAuthUserKey TODO')
  // console.log('authUserKey:', authUserKey)
  // console.log('authProvData:', authProvData)
  return authUserKey.substr(0, authUserKey.search(JSON.parse(authProvData.ConfigJSON).userSufix))
}

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
          Notify.create({color: 'positive', message: 'Password reset sucessful'})
        },
        error: function (error) {
          Loading.hide()
          Notify.create('Reset Password failed - ' + callbackHelper.getErrorFromResponse(error))
        }
      }
      Loading.show()
      var username = getUsernameFromAuthUserKey(this.authData.AuthUserKey, this.authData.internalAuthProv)
      var passwordhash = bcrypt.hashSync(username + ':' + this.dialogData.current_password + ':AG44', atob(this.authData.internalAuthProv.saltForPasswordHashing))
      var newPasswordhash = bcrypt.hashSync(username + ':' + this.dialogData.password + ':AG44', atob(this.authData.internalAuthProv.saltForPasswordHashing))
      var postData = {
        authProviderGUID: this.authData.internalAuthProv.guid,
        credentialJSON: {
          username: username,
          password: passwordhash
        },
        operationName: 'ResetPassword',
        operationData: {newPassword: newPasswordhash}
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
