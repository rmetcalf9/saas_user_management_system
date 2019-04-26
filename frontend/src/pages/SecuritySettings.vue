<template>
  <div class="fixed-center text-center">
    <p class="text-faded">Security Settings Page</p>
    <q-btn
      color="secondary"
      style="width:200px;"
      @click="goBackClick"
    >Go back</q-btn>
  </div>
</template>

<script>
export default {
  name: 'SecuritySettings',
  methods: {
    goBackClick () {
      window.location.href = this.$store.state.globalDataStore.usersystemReturnaddress
    }
  }
}
</script>
