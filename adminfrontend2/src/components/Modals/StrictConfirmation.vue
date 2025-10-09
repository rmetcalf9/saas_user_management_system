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
          {{ message }}
          <q-input v-model="text" @keyup.enter="ok" ref="textInput" label="Text" :label-width="3" />
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

export default {
  // name: 'StrictConfirmation',
  data () {
    return {
      visible: false,
      title: 'Not Set',
      text: '',
      expectedText: 'Not Set',
      message: 'Not Set',
      callerData: {}
    }
  },
  methods: {
    getStyleComponent (styleName) {
      return this.$refs[styleName + 'UI']
    },
    ok () {
      const TTT = this
      // Validation checks
      if (TTT.text !== TTT.expectedText) {
        Notify.create({ color: 'negative', message: 'You did not type ' + TTT.expectedText })
        return
      }

      this.visible = false
      this.$emit('ok', this.callerData)
    },
    cancel () {
      this.visible = false
    },
    launchDialog (message, title, expectedText, callerData) {
      const TTT = this
      this.message = message
      this.text = ''
      this.expectedText = expectedText
      this.title = title
      this.callerData = callerData

      TTT.visible = true // Must be visible for ref to exist
      setTimeout(function () {
        // Highlight default field
        TTT.$refs.textInput.focus()
      }, 5)
    }
  },
  computed: {
    okDisabled () {
      return false
      // if (this.dialogData.op === 'add') {
      //   return false
      // }
      // return !this.changed
    }
  }
}
</script>

<style>
</style>
