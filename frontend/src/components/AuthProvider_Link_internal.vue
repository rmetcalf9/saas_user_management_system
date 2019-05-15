<template>
  <div>
    <q-btn
      push
      @click="linkClick()"
    >{{ authProvData.LinkText }}</q-btn>
    <q-modal v-model="createAccountDialogModel.visible" :content-css="{minWidth: '40vw', minHeight: '30vh'}">
      <q-modal-layout>
        <q-toolbar slot="header">
            <q-btn
            color="primary"
            flat
            round
            dense
            icon="keyboard_arrow_left"
            @click="cancelCreateAccountDialog"
          />
          <q-toolbar-title>
            Create Account
          </q-toolbar-title>
        </q-toolbar>

        <div class="layout-padding">
          <q-field helper="Username" label="Username" :label-width="3">
            <q-input v-model="createAccountDialogModel.username" ref="usernameDialogInput"/>
          </q-field>
          <q-field :helper="passwordERRORMessage" label="Password" :label-width="3" :error="passwordERROR">
            <q-input type="password" v-model="createAccountDialogModel.password" />
          </q-field>
          <q-field helper="Retype Password" label="Retype" :label-width="3" :error="passwordERROR">
            <q-input type="password" v-model="createAccountDialogModel.password2" @keyup.enter="okCreateAccountDialog" />
          </q-field>
          <q-btn
            @click="okCreateAccountDialog"
            color="primary"
            label="Ok"
            class = "float-right q-ml-xs"
          />
          <q-btn
            @click="cancelCreateAccountDialog"
            label="Cancel"
            class = "float-right"
          />
        </div>
      </q-modal-layout>
    </q-modal>
  </div>
</template>

<script>
import frontendFns from '../frontendFns.js'
import bcrypt from 'bcryptjs'
import {
  Notify,
  Loading
} from 'quasar'

export default {
  // name: 'AuthSecuritySettingsInternal',
  props: [
    'authProvData'
  ],
  data () {
    return {
      createAccountDialogModel: {
        visible: false,
        username: '',
        password: '',
        password2: ''
      }
    }
  },
  computed: {
    passwordERROR () {
      return (this.passwordERRORMessage !== 'Password')
    },
    passwordERRORMessage () {
      return frontendFns.passwordERRORMessage(this.createAccountDialogModel.password, this.createAccountDialogModel.password2)
    }
  },
  methods: {
    linkClick (authProvData) {
      this.createAccountDialogModel = {
        visible: true,
        username: '',
        password: '',
        password2: ''
      }
      this.$refs.usernameDialogInput.focus()
    },
    okCreateAccountDialog () {
      var TTT = this
      if (this.passwordERROR) {
        Notify.create(this.passwordERRORMessage)
        return
      }
      Loading.show()
      var passwordhash = bcrypt.hashSync(
        this.createAccountDialogModel.username + ':' + this.createAccountDialogModel.password + ':AG44',
        atob(this.authProvData.saltForPasswordHashing)
      )
      var credentialJSON = {
        username: this.createAccountDialogModel.username,
        password: passwordhash
      }
      TTT.$emit('completeOK', TTT.authProvData, credentialJSON)
    },
    cancelCreateAccountDialog () {
      this.createAccountDialogModel.visible = false
    }
  }
}
</script>

<style>
</style>
