<template>
  <q-dialog v-model="visible">
    <q-layout view="Lhh lpR fff" container class="bg-white" style="height: 400px; width: 700px; max-width: 80vw;">
      <q-header class="bg-primary">
        <q-toolbar>
          <q-toolbar-title>
            Create batch of tickets for {{ tenantName }} of type {{ ticketTypeName }}
          </q-toolbar-title>
          <q-btn flat v-close-popup round dense icon="close" />
        </q-toolbar>
      </q-header>

      <q-page-container>
        <q-page padding>
          Enter a comma seperated list of foreign keys for the tickets that need to be created.
          <q-input v-model="text" @keyup.enter="ok" ref="textInput" label="Text" :label-width="3" />
          (Your list contains {{ numberOfForeignKeys }} keys)<br>
          <p class="text-negative" v-if="repeatedKeys.length > 0">Repeated keys in input: {{ repeatedKeys }}</p>
          <q-select
            outlined v-model="foreignKeyDupAction"
            :options="foreignKeyDupActionOptions"
            label="Action to take for existing keys"
            :display-value="foreignKeyDupAction.label"
          >
            <template v-slot:option="scope">
              <q-item
                v-bind="scope.itemProps"
                v-on="scope.itemEvents"
              >
                <q-item-section>
                  <q-item-label v-html="scope.opt.label" />
                  <q-item-label caption>{{ scope.opt.description }}</q-item-label>
                </q-item-section>
              </q-item>
            </template>
          </q-select>
          XX {{ foreignKeyDupAction }}
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
// import { Notify } from 'quasar'

function getforeignKeyDupActionOptions () {
  return [
    { label: 'Skip', value: 'Skip', description: 'Skip over any existing foreign keys' },
    { label: 'Reissue All Active', value: 'ReissueAllActive', description: 'Any current tickets that are active for existing keys are disabled and re-issued' }
  ]
}

export default {
  name: 'TicketCreateBatchStart',
  data () {
    return {
      visible: false,
      text: 'x',
      tenantName: '',
      ticketTypeName: '',
      callerData: {},
      foreignKeyDupAction: getforeignKeyDupActionOptions()[0],
      foreignKeyDupActionOptions: getforeignKeyDupActionOptions()
    }
  },
  methods: {
    getStyleComponent (styleName) {
      return this.$refs[styleName + 'UI']
    },
    ok () {
      // var TTT = this
      // Validation checks

      this.visible = false
      this.$emit('ok', {
        callerData: this.callerData,
        keymap: this.keyList,
        foreignKeyDupAction: this.foreignKeyDupAction.value
      })
    },
    cancel () {
      this.visible = false
    },
    launchDialog ({ callerData, ticketTypeData }) {
      var TTT = this
      this.text = ''
      this.callerData = callerData
      // console.log(ticketTypeData)
      this.tenantName = ticketTypeData.tenantName
      this.ticketTypeName = ticketTypeData.ticketTypeName

      TTT.visible = true // Must be visible for ref to exist
      setTimeout(function () {
        // Highlight default field
        TTT.$refs.textInput.focus()
      }, 5)
    }
  },
  computed: {
    keyList () {
      var list = []
      this.text.split(',').map(function (text) {
        var key = text.trim()
        if (key !== '') {
          list.push(key)
        }
      })
      return list
    },
    numberOfForeignKeys () {
      return this.keyList.length
    },
    repeatedKeys () {
      var ret = []
      var items = {}
      this.text.split(',').map(function (text) {
        var key = text.trim().toUpperCase()
        if (key !== '') {
          if (typeof (items[key]) !== 'undefined') {
            ret.push(key)
          }
          items[key] = key
        }
      })
      return ret
    },
    okDisabled () {
      if (this.repeatedKeys.length !== 0) {
        return true
      }
      return this.numberOfForeignKeys === 0
    }
  }
}
</script>

<style>
</style>
