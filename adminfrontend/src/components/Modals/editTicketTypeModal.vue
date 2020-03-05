<template>
  <q-dialog v-model="visible">
    <q-layout view="Lhh lpR fff" container class="bg-white" style="height: 400px; width: 700px; max-width: 80vw;">
      <q-header class="bg-primary">
        <q-toolbar>
          <q-toolbar-title>
            {{ title }}
          </q-toolbar-title>
          <q-btn flat v-close-popup round dense icon="close" />
        </q-toolbar>
      </q-header>

      <q-page-container>
        <q-page padding>
        <q-input v-model="objData.ticketTypeName" ref="textInput" label="Ticket Type Name" :label-width="3" :error="invalid_ticketTypeName" :error-message="invalidlabel_ticketTypeName" />
        <q-input v-model="objData.description" label="Description" :label-width="3" />
        <q-field helper="Enabled" :label-width="3">
          <q-toggle v-model="objData.enabled" label="Enabled" />
          <q-toggle v-model="objData.allowUserCreation" label="Allow User Creation"  />
        </q-field>
        <q-input v-model="objData.issueDuration" type="number" label="Hours tickets are valid for after creation"
        />
        <q-card>
          <q-card-section>
            <div class="text-h6">Welcome Message</div>
            <q-input v-model="objData.welcomeMessage.title" label="Title" :label-width="3" />
            <q-input v-model="objData.welcomeMessage.body" label="Body" :label-width="3" />
            <q-toggle v-model="objData.welcomeMessage.agreementRequired" label="Agreement Required" />
            <q-input v-model="objData.welcomeMessage.okButtonText" label="Ok button text" :label-width="3" />
          </q-card-section>
        </q-card>
        <q-input v-model="objData.postUseURL" label="post Use URL" :label-width="3" />
        <q-input v-model="objData.postInvalidURL" label="post Invalid URL" :label-width="3" />
        <q-select
          label="Roles this ticket grants to users"
          v-model="objData.roles"
          use-input
          use-chips
          multiple
          input-debounce="0"
          @new-value="roleNewValue"
        /> Roles this ticket grants to users

          <div>&nbsp;</div>
          <q-btn
            @click="ok"
            color="primary"
            label="Ok"
            class = "float-right q-ml-xs"
            :disabled='okDisabled'
          />
          <q-btn
            @click="cancel"
            label="Cancel"
            class = "float-right"
          />
        </q-page>
      </q-page-container>

    </q-layout>
  </q-dialog>
</template>

<script>
import { Notify } from 'quasar'

function getDefaultObjectData () {
  return {
    // id: GUID for ticket Type
    // tenantName: tenant this ticket is valid for
    ticketTypeName: '',
    description: '',
    enabled: true,
    welcomeMessage: {
      agreementRequired: false,
      title: 'Welcome Message Title',
      body: 'welcome message text',
      okButtonText: 'Ok'
    },
    allowUserCreation: true,
    issueDuration: (24 * 7), // default to a week
    roles: [],
    postUseURL: '',
    postInvalidURL: ''
  }
}

export default {
  // name: 'EditTicketTypeModal',
  data () {
    return {
      visible: false,
      title: 'Not Set',
      callerData: {},
      editingExisting: false,
      objData: getDefaultObjectData()
    }
  },
  methods: {
    getStyleComponent (styleName) {
      return this.$refs[styleName + 'UI']
    },
    ok () {
      // var TTT = this
      // Validation checks
      var x = this.invalidlabel_GLOB
      if (typeof (x) !== 'undefined') {
        Notify.create({color: 'negative', message: x})
        return
      }

      this.visible = false
      this.$emit('ok', this.callerData, this.objData)
    },
    cancel () {
      this.visible = false
    },
    launchDialog ({ title, callerData, editingExisting }) {
      var TTT = this
      this.title = title
      this.callerData = callerData
      this.editingExisting = editingExisting

      if (this.editingExisting) {
        // we need to init dialog with existing values
        this.objData = getDefaultObjectData()
      } else {
        // blank values
        this.objData = getDefaultObjectData()
      }

      TTT.visible = true // Must be visible for ref to exist
      setTimeout(function () {
        // Highlight default field
        TTT.$refs.textInput.focus()
      }, 5)
    },
    roleNewValue (val, done) {
      // if (val.length < 3) {
      //  Notify.create({color: 'negative', message: 'Must have at least 3 characters'})
      //  return
      // }
      done(val, 'add-unique')
    }
  },
  computed: {
    okDisabled () {
      if (typeof (this.invalidlabel_GLOB) !== 'undefined') {
        return true
      }
      return false
    },
    invalid_ticketTypeName () {
      return this.objData.ticketTypeName.length < 4
    },
    invalidlabel_ticketTypeName () {
      return 'Ticket Type Name must be more than 3 characters long'
    },
    invalidlabel_GLOB () {
      if (this.invalid_ticketTypeName) {
        return this.invalidlabel_ticketTypeName
      }
      return undefined
    }
  }
}
</script>

<style>
</style>
