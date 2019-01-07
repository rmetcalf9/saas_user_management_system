<template>
  <div class="fixed-center">
    <div>
      <q-input v-model="usernamePass.username" placeholder="Username" />
      <br>
      <q-input type="password" v-model="usernamePass.password" placeholder="Password" />
      <p class="text-center group">
        <q-btn
          color="primary"
          push
          @click="usernamePassLogin"
        >
          Login
        </q-btn>
      </p>
    </div>
  </div>
</template>

<style>
</style>

<script>
export default {
  name: 'AuthProvider_internal',
  data () {
    return {
      usernamePass: {
        username: '',
        password: ''
      }
    }
  },
  computed: {
    tenantInfo () {
      return this.$store.state.globalDataStore.tenantInfo
    }
  },
  methods: {
    usernamePassLogin () {
      console.log('TODO')
    }
  }
}
</script>
