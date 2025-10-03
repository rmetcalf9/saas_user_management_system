<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title>
          <div @click="clicktoolbartitle">adminfrontend</div>
        </q-toolbar-title>

        <div v-if="serverInfoVersionMatchesCodeBaseVersion">Version {{ serverInfoVersion }}</div>
        <div v-if="!serverInfoVersionMatchesCodeBaseVersion">Version {{ serverInfoVersion }}
          <q-tooltip>
            <table><tr><td>Services: {{serverInfoVersion}}</td></tr>
            <tr><td>Code: {{ codebasever }}</td></tr></table>
          </q-tooltip>
        </div>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
    >
    <q-list>
      <div v-if="isAdminUser">
        <q-item-label
          header
          class="text-grey-8"
        >
          Admin
        </q-item-label>
        <q-item clickable :to='"/" + this.$route.params.tenantName + "/admin/locationscanner"'>
          <q-item-section avatar>
            <q-icon color="primary" name="add_location" />
          </q-item-section>
          <q-item-section>
            <q-item-label>TODO ADMIN MENU ITEM</q-item-label>
            <q-item-label caption>TODO ADMIN MENU ITEM</q-item-label>
          </q-item-section>
        </q-item>
      </div>
      <q-item-label
        header
        class="text-grey-8"
      >
        {{ host }} Links
      </q-item-label>
      <q-item clickable :to='"/" + this.$route.params.tenantName + "/"'>
        <q-item-section avatar>
          <q-icon color="primary" name="equalizer" />
        </q-item-section>
        <q-item-section>
          <q-item-label>Home</q-item-label>
          <q-item-label caption>Index Page</q-item-label>
        </q-item-section>
      </q-item>
      <q-separator />
      <saasUsermanagementLoginItem
        v-model="saasLogin"
        @userloggedout="userloggedout"
      />
      <div v-if="tenantName !== 'defaulttenant'">
        <q-separator />
        <q-item>
          <q-item-section>
            <q-item-label>non-prod Tenant</q-item-label>
            <q-item-label caption>{{ tenantName }}</q-item-label>
          </q-item-section>
        </q-item>
      </div>
    </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import { defineComponent, ref } from 'vue'
import { saasServiceName } from '../router/routes.js'
import { useUserManagementClientStoreStore } from 'stores/saasUserManagementClientStore'
import rjmversion from '../rjmversion'
import saasUsermanagementLoginItem from '../components/saasUsermanagementLoginItem.vue'

export default defineComponent({
  name: 'MainLayout',

  components: {
    saasUsermanagementLoginItem
  },

  setup () {
    const store = useUserManagementClientStoreStore()
    const leftDrawerOpen = ref(false)

    return {
      leftDrawerOpen,
      toggleLeftDrawer () {
        leftDrawerOpen.value = !leftDrawerOpen.value
      },
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
      return this.store.hasRole('adminfrontendadmin')
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
