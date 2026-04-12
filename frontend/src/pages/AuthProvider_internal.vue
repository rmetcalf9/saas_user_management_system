<template>
  <q-page class="flex flex-center indexpage-main">
    <DisplayInputMessage />
    <div>TODO</div>
  </q-page>
</template>

<script>
import { defineComponent } from 'vue'
// import { Notify } from 'quasar'
import DisplayInputMessage from '../components/displayInputMessage.vue'

export default defineComponent({
  name: 'IndexPage',
  components: {
    DisplayInputMessage
  },
  setup () {
  },
  data () {
    return {
    }
  }
})
</script>

<style>
</style>
