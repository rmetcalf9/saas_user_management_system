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
    }
  },
  methods: {
    openURL,
    clickLogout () {
      this.$store.commit('globalDataStore/SET_LOGOUT_CLICK_CUR_ROUTE', this.$router.currentRoute.path)
      this.$q.cookies.remove('usersystemUserCredentials')
      this.$router.replace('/' + this.$route.params.tenantName + '/logout')
    }
  }
}
</script>

<style>
</style>
