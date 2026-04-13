<template>
  <div></div>
</template>

<script>
import { defineComponent } from 'vue'
import { Notify } from 'quasar'
import { useInputParamsStore } from 'stores/inputParams'

export default defineComponent({
  name: 'DisplayInputMessageComponent',
  setup () {
    const inputParamsStore = useInputParamsStore()
    return { inputParamsStore }
  },
  mounted () {
    if (this.inputParamsStore.usersystemMessage === '') {
      return
    }
    Notify.create({
      color: 'negative',
      message: this.inputParamsStore.usersystemMessage
    })
    this.inputParamsStore.clearUsersystemMessage()
  }
})
</script>

<style>
</style>
