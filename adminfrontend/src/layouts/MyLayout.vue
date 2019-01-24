<template>
  <q-layout view="lHh Lpr lFf">
    <q-layout-header>
      <q-toolbar
        color="primary"
        :glossy="$q.theme === 'mat'"
        :inverted="$q.theme === 'ios'"
      >
        <q-btn
          flat
          dense
          round
          @click="leftDrawerOpen = !leftDrawerOpen"
          aria-label="Menu"
        >
          <q-icon name="menu" />
        </q-btn>

        <q-toolbar-title>
          SAAS User System - {{ pageTitle }}
          <div slot="subtitle">Running on Quasar v{{ $q.version }}</div>
        </q-toolbar-title>
      </q-toolbar>
    </q-layout-header>
    <q-layout-drawer
      v-model="leftDrawerOpen"
      :content-class="$q.theme === 'mat' ? 'bg-grey-2' : null"
    >
      <q-list
        no-border
        link
        inset-delimiter
      >
        <q-list-header>Functions</q-list-header>
        <q-item :to='"/" + this.$route.params.tenantName + "/tenants"'>
          <q-item-side icon="business" />
          <q-item-main label="Tenants" sublabel="" />
        </q-item>
        <q-item :to='"/" + this.$route.params.tenantName + "/users"'>
          <q-item-side icon="person" />
          <q-item-main label="Users" sublabel="" />
        </q-item>
        <q-list-header>User Options</q-list-header>
        <q-item @click.native="clickLogout">
          <q-item-side icon="exit_to_app" />
          <q-item-main label="Logout" />
        </q-item>
      </q-list>
    </q-layout-drawer>
    <q-page-container>
      <router-view />
    </q-page-container>

    <q-layout-footer>
      <q-toolbar
          color="primary"
          :glossy="$q.theme === 'mat'"
          :inverted="$q.theme === 'ios'"
        >
          <a v-if="! (serverInfo.Server.APIAPP_APIDOCSURL === '_')" v-bind:href="serverInfo.Server.APIAPP_APIDOCSURL" target="_blank">APIdocs</a>
          <div>&nbsp;</div>
          <a href="https://github.com/rmetcalf9/saas_user_management_system" target="_blank">GitHub</a>
          <div class="col"></div> <!-- eat up all the free space -->
          Version: {{serverInfo.Server.Version}}
      </q-toolbar>
    </q-layout-footer>

  </q-layout>
</template>

<script>
import { openURL } from 'quasar'

export default {
  name: 'MyLayout',
  data () {
    return {
      leftDrawerOpen: this.$q.platform.is.desktop
    }
  },
  computed: {
    pageTitle () {
      return this.$store.state.globalDataStore.pageTitle
    },
    serverInfo () {
      return this.$store.state.globalDataStore.serverInfo
    }
  },
  methods: {
    openURL,
    clickLogout () {
      this.$store.commit('globalDataStore/SET_LOGOUT_CLICK_CUR_ROUTE', this.$router.currentRoute.path)
      this.$q.cookies.remove('usersystemUserCredentials')
      this.$router.replace('/' + this.$route.params.tenantName + '/logout')
    }
  },
  created () {
    if (this.$route.params.tenantName === '') {
      /// go to root, this will give us a 404
      console.log('ERROR bad tenant Name')
      return
    }
    var a = 1
    if (a === 2) {
      console.log('NEVE')
    }
    /*
    Loading.show()
    // var TTT = this
    var callback = {
      ok: function (response) {
        Loading.hide()
      },
      error: function (response) {
        Loading.hide()
        console.log('TODO Fail')
      }
    }
    this.$store.dispatch('globalDataStore/readServerInfo', {
      tenantName: this.$route.params.tenantName,
      callback: callback,
      currentHREF: window.location.href
    })
    */
  }
}
</script>

<style>
</style>
