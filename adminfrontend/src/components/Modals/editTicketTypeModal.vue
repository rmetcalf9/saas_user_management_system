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
        <q-input v-model="objData.ticketTypeName" ref="textInput" label="Ticket Type Name" :label-width="3" :error="invalid_ticketTypeName" :error-message="invalidlabel_ticketTypeName"  @input="registerChange" />
        <q-input v-model="objData.description" label="Description" :label-width="3" :error="invalid_description" :error-message="invalidlabel_description"  @input="registerChange" />
        <q-field helper="Enabled" :label-width="3">
          <q-toggle v-model="objData.enabled" label="Enabled"  @input="registerChange" />
          <q-toggle v-model="objData.allowUserCreation" label="Allow User Creation"  @input="registerChange" />
        </q-field>
        <q-input v-model="objData.issueDuration" type="number" label="Hours tickets are valid for after creation" @input="registerChange"
        />
        <q-card>
          <q-card-section>
            <div class="text-h6">Welcome Message</div>
            <q-input v-model="objData.welcomeMessage.title" label="Title" :label-width="3" @input="registerChange" />
            <q-input v-model="objData.welcomeMessage.body" label="Body" :label-width="3" @input="registerChange" />
            <q-toggle v-model="objData.welcomeMessage.agreementRequired" label="Agreement Required" @input="registerChange" />
            <q-input v-model="objData.welcomeMessage.okButtonText" label="Ok button text" :label-width="3" @input="registerChange" />
          </q-card-section>
        </q-card>
        <q-input v-model="objData.postUseURL" label="post Use URL" :label-width="3" :error="invalid_postUseURL" :error-message="invalidlabel_postUseURL" @input="registerChange" />
        <q-input v-model="objData.postInvalidURL" label="post Invalid URL" :label-width="3" :error="invalid_postInvalidURL" :error-message="invalidlabel_postInvalidURL"  @input="registerChange"/>
        <q-select
          label="Roles this ticket grants to users"
          v-model="objData.roles"
          use-input
          use-chips
          multiple
          input-debounce="0"
          @new-value="roleNewValue"
          @input="registerChange"
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
      objData: getDefaultObjectData(),
      changed: false
    }
  },
  methods: {
    registerChange () {
      this.changed = true
    },
    getStyleComponent (styleName) {
      return this.$refs[styleName + 'UI']
    },
    ok () {
      if (!this.changed) {
        Notify.create({color: 'negative', message: 'No changes made'})
        return
      }
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
    launchDialog ({ title, callerData, editingExisting, initialValues }) {
      var TTT = this
      this.title = title
      this.callerData = callerData
      this.editingExisting = editingExisting
      this.changed = false

      if (this.editingExisting) {
        // we need to init dialog with existing values
        this.objData = getDefaultObjectData()
        this.objData.ticketTypeName = initialValues.ticketTypeName
        this.objData.description = initialValues.description
        this.objData.enabled = initialValues.enabled
        this.objData.welcomeMessage.agreementRequired = initialValues.welcomeMessage.agreementRequired
        this.objData.welcomeMessage.title = initialValues.welcomeMessage.title
        this.objData.welcomeMessage.body = initialValues.welcomeMessage.body
        this.objData.welcomeMessage.okButtonText = initialValues.welcomeMessage.okButtonText
        this.objData.allowUserCreation = initialValues.allowUserCreation
        this.objData.issueDuration = initialValues.issueDuration
        this.objData.roles = []
        initialValues.roles.map(function (x) {
          TTT.objData.roles.push(x)
        })
        this.objData.postUseURL = initialValues.postUseURL
        this.objData.postInvalidURL = initialValues.postInvalidURL
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
      if (!this.changed) {
        return true
      }
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
    invalid_description () {
      return this.objData.description.length < 4
    },
    invalidlabel_description () {
      return 'Description must be more than 3 characters long'
    },
    invalid_postUseURL () {
      return this.objData.postUseURL.length < 4
    },
    invalidlabel_postUseURL () {
      return 'postUseURL must be more than 3 characters long'
    },
    invalid_postInvalidURL () {
      return this.objData.postInvalidURL.length < 4
    },
    invalidlabel_postInvalidURL () {
      return 'postInvalidURL must be more than 3 characters long'
    },
    invalidlabel_GLOB () {
      if (this.invalid_ticketTypeName) {
        return this.invalidlabel_ticketTypeName
      }
      if (this.invalid_description) {
        return this.invalidlabel_description
      }
      return undefined
    }
  }
}

</script>

<style>
</style>
