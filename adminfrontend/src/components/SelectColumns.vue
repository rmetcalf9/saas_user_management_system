<template>
  <q-select
    multiple
    outlined
    emit-value
    hide-selected
    :options="columnsForEnableDropdown"
    label="Fields:"
    style="width: 300px"
    v-model="localTableVisibleColumns"
    :display-value="''"
  >
    <template v-slot:selected-item>
    </template>
  </q-select>
</template>

<script>

export default {
  props: [
    'selected_col_names',
    'columns'
  ],
  data () {
    return {
      localTableVisibleColumns: []
    }
  },
  watch: {
    localTableVisibleColumns: {
      handler (newVal) {
        const toEmit = this.columns.filter(function (x) {
          return x.required
        }).map(function (x) {
          return x.name
        }).concat(newVal)
        this.$emit('update:selected_col_names', toEmit)
      },
      deep: true // ensures reactivity inside array
    }
  },
  methods: {
    // I think this is what Emit-value does
    updateselection (event) {
      // this.localTableVisibleColumns = event
      let visibleCols = []
      this.columnsForEnableDropdown.forEach(function (col) {
        event.forEach(function (evecol) {
          if (typeof (evecol) !== 'string') {
            if (evecol.value === col.value) {
              visibleCols = [...visibleCols, evecol.value]
              // console.log('evecol', evecol)
            }
          }
        })
      })
      console.log('viscols', visibleCols)
      // this.$emit('update:modelValue', [...visibleCols])
    }
  },
  computed: {
    columnsForEnableDropdown () {
      return this.columns.filter(function (x) { return !x.required }).map(function (x) {
        return {
          value: x.name,
          label: x.label,
          disable: x.required
        }
      })
    }
  },
  mounted () {
    const TTT = this
    this.localTableVisibleColumns = []
    this.selected_col_names.forEach(function (colName) {
      const matchingCols = TTT.columns.filter(function (x) {
        return x.name === colName
      })
      if (matchingCols.length !== 1) {
        console.log('There is not exactly 1 instance of col name ', colName)
      }
      if (!matchingCols[0].required) {
        TTT.localTableVisibleColumns.push(colName)
      }
    })
  }
}
</script>[

<style>
</style>
