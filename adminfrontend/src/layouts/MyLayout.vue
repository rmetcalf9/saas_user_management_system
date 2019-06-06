<template>
  <!-- saas_user_management adminfrontend -->
  <q-layout view="lHh Lpr lFf">
    <q-header>
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
        <q-btn v-if="backroute !== ''" class="within-iframe-hide" flat @click="$router.replace(backroute)" style="margin-right: 15px">
          <q-icon name="keyboard_arrow_left" />
        </q-btn>

        <q-toolbar-title>
          SAAS User System - {{ pageTitle }}
          <div slot="subtitle">Running on Quasar v{{ $q.version }}</div>
        </q-toolbar-title>
      </q-toolbar>
    </q-header>

    <!-- Left Side Drawer -->
    <q-drawer side="left" v-model="leftDrawerOpen" :content-class="$q.theme === 'mat' ? 'bg-grey-2' : null">
      <q-list no-border link inset-separator>
        <q-item-label header>Navigation</q-item-label>

        <q-item :to='"/" + this.$route.params.tenantName + "/tenants"'>
          <q-item-section avatar>
            <q-icon color="primary" name="business" />
          </q-item-section>
          <q-item-section>Tenants</q-item-section>
        </q-item>
        <q-item :to='"/" + this.$route.params.tenantName + "/users"'>
          <q-item-section avatar>
            <q-icon color="primary" name="person" />
          </q-item-section>
          <q-item-section>Users</q-item-section>
        </q-item>
        <q-item :to='"/" + this.$route.params.tenantName + "/persons"'>
          <q-item-section avatar>
            <q-icon color="primary" name="directions_walk" />
          </q-item-section>
          <q-item-section>Persons</q-item-section>
        </q-item>
        <q-item :to='"/" + this.$route.params.tenantName + "/usersettings"'>
          <q-item-section avatar>
            <q-icon color="primary" name="settings" />
          </q-item-section>
          <q-item-section>User Settings</q-item-section>
        </q-item>
        <q-separator />
        <q-item clickable @click.native="clickLogout">
          <q-item-section avatar>
            <q-icon color="primary" name="exit_to_app" />
          </q-item-section>
          <q-item-section>User Logout</q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>

    <q-footer>
      <q-toolbar>
        <table width="100%"><tr>
        <td>
          <table><tr><td>
            <a v-if="! (serverInfo.Server.APIAPP_APIDOCSURL === '_')" v-bind:href="serverInfo.Server.APIAPP_APIDOCSURL" target="_blank">APIdocs</a>
          </td><td>
            <a href="https://github.com/rmetcalf9/saas_user_management_system" target="_blank">GitHub</a>
          </td></tr></table>
        </td>
        <td align="right">Version: {{serverInfo.Server.Version}}</td>
        </tr></table>
      </q-toolbar>
    </q-footer>
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
    },
    backroute () {
      // console.log(this.$route.path)
      if (this.$route.path === '/') return ''
      var x = this.$route.path.split('/')
      if (x.length < 4) return ''
      var o = ''
      for (var y in x) {
        if (y < (x.length - 1)) o += '/' + x[y]
      }
      var newPath = o.substring(1)
      // console.log('new Path is', newPath)
      return newPath
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
