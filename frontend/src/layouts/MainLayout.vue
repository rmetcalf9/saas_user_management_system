<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-toolbar-title>
          <div @click="clicktoolbartitle">Login</div>
        </q-toolbar-title>

        <div v-if="serverInfoVersionMatchesCodeBaseVersion">Version {{ serverInfoVersion }}</div>
        <div v-if="!serverInfoVersionMatchesCodeBaseVersion">Version {{ serverInfoVersion }}
          <q-tooltip>
            <table><tbody><tr><td>Services: {{serverInfoVersion}}</td></tr>
            <tr><td>Code: {{ codebasever }}</td></tr></tbody></table>
          </q-tooltip>
        </div>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import { defineComponent } from 'vue'
import { saasServiceName } from '../router/routes.js'
import { useUserManagementClientStoreStore } from 'stores/saasUserManagementClientStore'
import rjmversion from '../rjmversion'

export default defineComponent({
  name: 'MainLayout',

  components: {
  },

  setup () {
    const store = useUserManagementClientStoreStore()

    return {
      toolbartitlelastclick: Date.now(),
      toolbartitleclickcount: 0,
      store
    }
  },
  data () {
    return {
      codebasever: rjmversion.codebasever,
      saasLogin: undefined
    }
  },
  methods: {
    userloggedout () {
      this.$router.replace('/' + this.$route.params.tenantName + '/')
    },
    clicktoolbartitle () {
      // console.log('Start of clicktoolbartitle')
      // Reset counter if last click was more than 2 seconds ago
      const curTime = Date.now()
      if ((curTime - this.toolbartitlelastclick) > 2000) {
        this.toolbartitlelastclick = curTime
        this.toolbartitleclickcount = 0
        return
      }

      // Not increment following rules
      this.toolbartitleclickcount = this.toolbartitleclickcount + 1
      this.toolbartitlelastclick = curTime

      if (this.toolbartitleclickcount > 7) {
        this.toolbartitleclickcount = 0
        this.$router.replace('/' + this.$route.params.tenantName + '/debug')
      }
      // console.log('End of clicktoolbartitle')
    }
  },
  computed: {
    host () {
      return window.location.host
    },
    isAdminUser () {
      return this.store.hasRole('frontendadmin')
    },
    serverInfoVersion () {
      const endpoints = this.store.endpointInfo
      console.log('MyLayout.vue - caculating serverInfoVersion')
      if (typeof (endpoints[saasServiceName]) === 'undefined') {
        return 'NotRead'
      }
      if (typeof (endpoints[saasServiceName].serverInfo) === 'undefined') {
        return 'NotRead'
      }
      if (typeof (endpoints[saasServiceName].serverInfo.Server) === 'undefined') {
        return 'NotRead'
      }
      if (typeof (endpoints[saasServiceName].serverInfo.Server.Version) === 'undefined') {
        return 'NotRead'
      }
      return endpoints[saasServiceName].serverInfo.Server.Version
    },
    serverInfoVersionMatchesCodeBaseVersion () {
      if (this.serverInfoVersion === 'NotRead') {
        // don't display the error if we haven't read services version yet
        return true
      }
      if (this.serverInfoVersion === this.codebasever) {
        return true
      }
      return false
    },
    tenantName () {
      return this.$route.params.tenantName
    }
  }
})
</script>
