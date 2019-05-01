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
import { Notify } from 'quasar'
import frontendFns from '../frontendFns.js'

export default {
  // name: 'AuthSecuritySettingsInternal',
  props: [
    'authData'
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
      Notify.create({color: 'positive', detail: 'TODO'})
    },
    cancelResetPasswordDialog () {
      this.resetPasswordDialogVisible = false
    }
  }
}
</script>

<style>
</style>
