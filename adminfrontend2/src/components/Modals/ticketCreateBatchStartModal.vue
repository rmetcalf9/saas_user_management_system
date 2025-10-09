<template>
  <q-dialog v-model="visible">
    <q-card style="width: 700px; max-width: 80vw; max-height: 90vh; display: flex; flex-direction: column;">
      <!-- Header -->
      <q-toolbar class="bg-primary text-white">
        <q-toolbar-title>
          Create batch of tickets for {{ tenantName }} of type {{ ticketTypeName }}
        </q-toolbar-title>
        <q-btn flat v-close-popup round dense icon="close" />
      </q-toolbar>

      <!-- Scrollable body -->
      <q-card-section style="flex: 1; overflow-y: auto;">
        <div class="q-mb-md">
          Enter a comma separated list of foreign keys for the tickets that need to be created.
        </div>

        <q-input
          v-model="text"
          @keyup.enter="ok"
          ref="textInput"
          label="Text"
          :label-width="3"
        />

        <div class="q-mt-sm">(Your list contains {{ numberOfForeignKeys }} keys)</div>

        <p class="text-negative q-mt-sm" v-if="repeatedKeys.length > 0">
          Repeated keys in input: {{ repeatedKeys }}
        </p>

        <q-select
          outlined
          v-model="foreignKeyDupAction"
          :options="foreignKeyDupActionOptions"
          label="Action to take for existing keys"
          :display-value="foreignKeyDupAction.label"
          class="q-mt-md"
        >
          <template v-slot:option="scope">
            <q-item v-bind="scope.itemProps">
              <q-item-section>
                <q-item-label>{{ scope.opt.label }}</q-item-label>
                <q-item-label caption>{{ scope.opt.description }}</q-item-label>
              </q-item-section>
            </q-item>
          </template>
        </q-select>
      </q-card-section>

      <!-- Footer -->
      <q-separator />
      <q-card-actions
        align="right"
        class="bg-grey-2"
        style="position: sticky; bottom: 0; z-index: 1;"
      >
        <q-btn
          @click="ok"
          color="primary"
          label="Ok"
          class="q-ml-xs"
          :disabled="okDisabled"
        />
        <q-btn
          @click="cancel"
          label="Cancel"
        />
      </q-card-actions>
    </q-card>
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
      const TTT = this
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
      const list = []
      this.text.split(',').forEach(function (text) {
        const key = text.trim()
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
      const ret = []
      const items = {}
      this.text.split(',').forEach(function (text) {
        const key = text.trim().toUpperCase()
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
