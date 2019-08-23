<template>
  <div>
    <q-btn
      push
      @click="linkClick()"
    >{{ authProvData.LinkText }}</q-btn>

    <q-dialog v-model="createAccountDialogModel.visible">
      <q-layout view="Lhh lpR fff" container class="bg-white" style="height: 400px; width: 700px; max-width: 80vw;">
        <q-header class="bg-primary">
          <q-toolbar>
            <q-toolbar-title>
              Create Account
            </q-toolbar-title>
            <q-btn flat v-close-popup round dense icon="close" />
          </q-toolbar>
        </q-header>
        <q-page-container>
          <q-page padding>
            <q-input
              v-model="createAccountDialogModel.username"
              ref="usernameDialogInput" helper="Username"
              label="Username"
              :label-width="3"
            />
            <q-input type="password"
              v-model="createAccountDialogModel.password"
              :error-message="passwordERRORMessage"
              label="Password"
              :label-width="3"
              :error="passwordERROR"
            />
            <q-input
              type="password"
              v-model="createAccountDialogModel.password2"
              @keyup.enter="okCreateAccountDialog"
              :error-message="passwordERRORMessage"
              label="Retype Password"
              :label-width="3"
              :error="passwordERROR"
            />
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
          </q-page>
        </q-page-container>
      </q-layout>
    </q-dialog>
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
      var TTT = this
      this.$nextTick(function () {
        TTT.$refs.usernameDialogInput.focus()
      })
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
