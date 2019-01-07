<template>
  <div class="fixed-center">
    <div>
      <div class="row">
        <div class="col">
          <p>How do you want to verify who you are?</p>
        </div>
      </div>
      <div class="row">
        <div v-for="curVal in authMethod" :key=curVal.k>
          <q-btn class="col q-ma-sm" :label="curVal.text" @click="clickHandler1"/>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
</style>

<script>
export default {
  name: 'PageIndex',
  data () {
    return {
      authMethod: [
        { k: 'a', text: 'Login with website account' },
        { k: 'b', text: 'Login with google' },
        { k: 'c', text: 'Login with XX' }
      ]
    }
  }
}
</script>
