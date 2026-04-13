<template>
  <div></div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'ProcessLoginResponseComponent',
  methods: {
    processLoginOKResponse (response, loginRequestPostData) {
      console.log('TODO processLoginOKResponse', response, loginRequestPostData)
    }
  }
})
</script>
