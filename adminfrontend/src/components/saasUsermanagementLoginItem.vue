<template>
  <div>
    <div v-if="viewstyle === 'item'">
      <q-item clickable @click="clickLogout" v-if="isLoggedIn">
        <q-item-section avatar>
          <q-icon color="primary" name="exit_to_app" />
        </q-item-section>
        <q-item-section>
          <q-item-label>{{ LogoutText }}</q-item-label>
          <q-item-label caption>{{ LogoutTextCaption }}</q-item-label>
        </q-item-section>
      </q-item>
      <q-item clickable @click="clickLogin" v-if="!isLoggedIn">
        <q-item-section avatar>
          <q-icon color="primary" name="exit_to_app" />
        </q-item-section>
        <q-item-section>
          <q-item-label>{{ LoginText }}</q-item-label>
          <q-item-label caption>{{ LoginTextCaption }}</q-item-label>
        </q-item-section>
      </q-item>
    </div>
    <div v-if="viewstyle === 'button'">
    <q-btn
      v-if="isLoggedIn"
      color="primary"
      style="width:200px;"
      @click="clickLogout"
    >{{ LogoutText }}</q-btn>
    <q-btn
      v-if="!isLoggedIn"
      :color="Color"
      style="width:200px;"
      @click="clickLogin"
    >{{ LoginText }}</q-btn>
    </div>
    <div v-if="viewstyle === 'securitysettingsbutton'">
      <q-btn
        :color="Color"
        style="width:200px;"
        @click="clickSecuritySettings"
      >Security Settings</q-btn>
    </div>
  </div>
</template>

<script>
import { useUserManagementClientStoreStore } from 'stores/saasUserManagementClientStore'

export default {
  name: 'saasUserManagementLoginItem',
  props: {
    value: {
      type: Object,
      default: function () {
        return { }
      }
    },
    viewstyle: {
      type: String,
      default: 'item'
    },
    LoginText: {
      type: String,
      default: 'Login'
    },
    LogoutText: {
      type: String,
      default: 'Logout'
    },
    LoginTextCaption: {
      type: String,
      default: ''
    },
    LogoutTextCaption: {
      type: String,
      default: ''
    },
    ReturnAddressuasarPathOverride: {
      type: String,
      default: 'none'
    },
    Color: {
      type: String,
      default: 'primary'
    }
  },
  setup () {
    const store = useUserManagementClientStoreStore()
    return { store }
  },
  data () {
    return {
    }
  },
  methods: {
    clickSecuritySettings (event) {
      const returnAddress = this.getReturnAddress()
      window.location.href = this.store.getLoginUIURLFn(undefined, '/SecuritySettings', returnAddress)
    },
    getReturnAddress () {
      const thisQuasarPath = this.$router.currentRoute.value.path
      let returnAddress = window.location.protocol + '//' + window.location.host + window.location.pathname + '#' + thisQuasarPath
      if (this.ReturnAddressuasarPathOverride !== 'none') {
        returnAddress = window.location.protocol + '//' + window.location.host + window.location.pathname + '#' + this.ReturnAddressuasarPathOverride
      }
      return returnAddress
    },
    clickLogin (event) {
      // Divert user to login url
      const returnAddress = this.getReturnAddress()
      window.location.href = this.store.getLoginUIURLFn(undefined, '/', returnAddress)
    },
    clickLogout (event) {
      this.store.logout()
      this.$emit('userloggedout', null)
    }
  },
  computed: {
    isLoggedIn () {
      return this.store.isLoggedIn
    }
  },
  mounted: function () {
    // Tell the outside world about the default value on first load
    //  I am assuming if we emit the same value as current nothing changes
    this.$emit('input', this.value)
  }
}
</script>
