<template>
  <div>
    <q-btn
      color="secondary"
      push
      @click="createAccountDialogModel.visible = true"
    >
      Create Account
    </q-btn>
    <q-dialog v-model="createAccountDialogModel.visible">
      <q-card style="width: 700px; max-width: 80vw; max-height: 90vh; display: flex; flex-direction: column;">
        <!-- Header -->
        <q-toolbar class="bg-primary text-white">
          <q-toolbar-title>Create Account</q-toolbar-title>
          <q-btn flat v-close-popup round dense icon="close" />
        </q-toolbar>

        <!-- Scrollable Body -->
        <q-card-section style="flex: 1; overflow-y: auto;">
          <q-input
            v-model="createAccountDialogModel.username"
            ref="usernameDialogInput"
            helper="Username"
            label="Username"
            :label-width="3"
           />
          <q-input
            type="password"
            v-model="createAccountDialogModel.password"
            label="Password"
            :label-width="3"
            :error-message="passwordERRORMessage"
            :error="passwordERROR"
           />
          <q-input
            type="password"
            v-model="createAccountDialogModel.password2"
            @keyup="textBoxKeyUp"
            label="Retype Password"
            :label-width="3"
            :error-message="passwordERRORMessage"
            :error="passwordERROR"
          />
        </q-card-section>

        <!-- Footer -->
        <q-separator />
        <q-card-actions
          align="right"
          class="bg-grey-2"
          style="position: sticky; bottom: 0; z-index: 1;"
        >
          <q-btn
            @click="okCreateAccountDialog"
            color="primary"
            label="Ok"
            class = "float-right q-ml-xs"
          />
          <q-btn
            @click="createAccountDialogModel.visible = false"
            label="Cancel"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { Notify, Loading } from 'quasar'
import frontendFns from '../../frontendFns.js'
import callbackHelper from '../../callbackHelper'
import bcrypt from 'bcryptjs'
import { useTenantInfoStore } from 'stores/tenantInfo'

export default defineComponent({
  name: 'InteralCreateAccountButtonComponent',
  components: {
  },
  emits: ['postCreateLogin'],
  setup () {
    const tenantInfoStore = useTenantInfoStore()
    return { tenantInfoStore }
  },
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
    },
    selectedAuthProvider () {
      return this.tenantInfoStore.selectedAuth
    }
  },
  methods: {
    textBoxKeyUp (e) {
      if (e.key === 'Enter') {
        this.okCreateAccountDialog()
      }
    },
    okCreateAccountDialog () {
      const TTT = this
      if (this.passwordERROR) {
        Notify.create({ color: 'negative', message: this.passwordERRORMessage })
        return
      }
      const callback = {
        ok: this.createOk,
        error: this.createError
      }
      const passwordhash = bcrypt.hashSync(this.createAccountDialogModel.username + ':' + this.createAccountDialogModel.password + ':AG44', atob(TTT.selectedAuthProvider.saltForPasswordHashing))
      const credentialJson = {
        username: this.createAccountDialogModel.username,
        password: passwordhash
      }
      Loading.show()
      frontendFns.callLoginAPI({
        credentialJSON: credentialJson,
        callback,
        processLoginResponseInstance: undefined,
        registering: true,
        router: this.$router
      })
    },
    createOk (response) {
      const TTT = this
      Loading.hide()
      TTT.createAccountDialogModel.visible = false
      Notify.create({ color: 'positive', message: 'Account created' })
      TTT.$emit('postCreateLogin', {
        username: TTT.createAccountDialogModel.username,
        password: TTT.createAccountDialogModel.password
      })
    },
    createError (response) {
      Loading.hide()
      Notify.create({
        color: 'negative',
        message: 'Create Account failed - ' + callbackHelper.getErrorFromResponse(response)
      })
    }
  }
})
</script>

<style>
</style>
