<template>
  <q-page class="flex flex-center">
    <div class="col">
      <q-list bordered padding>
        <q-item>
          <q-item-label header>Debug Information and functions</q-item-label>
        </q-item>
        <q-item>
          <q-item-section>
            <q-item-label>Route Params</q-item-label>
            {{ $route.params }}
          </q-item-section>
        </q-item>
        <q-item>
          <q-item-section>
            <q-item-label>Full Path</q-item-label>
            {{ $route.fullPath }}
          </q-item-section>
        </q-item>
        <q-item>
          <q-item-section>
            <q-item-label>Login</q-item-label>
            <div>Loginservice Info:<br/> {{ loginUIBaseURL }}</div>
            <div>isAdminUser: {{ isAdminUser }}</div>
            <div>isLoggedIn: {{ isLoggedIn }}</div>
          </q-item-section>
        </q-item>
        <q-item>
          <q-item-section>
            <q-item-label>Endpoint Info</q-item-label>
            <div>{{ endpointInfo }}</div>
          </q-item-section>
        </q-item>
        <q-item>
           <q-item-section>
           <q-item-label>Make browser clear all caches for this app</q-item-label>
           <q-btn color="primary" label="Force Reload"
                     @click="forcereload" >
          </q-btn>
           </q-item-section>
         </q-item>
         <q-item>
            <q-item-section>
            <q-item-label>Test call backend</q-item-label>
            <q-btn color="primary" label="Call backend ten times"
                      @click="callbackend" >
           </q-btn>
            </q-item-section>
          </q-item>
       </q-list>
       <div
          class="row"
       >
         <div
           v-for="tenant in possibleTenants"
           :key="tenant"
           style="padding: 10px"
         >
           <q-btn color="primary" @click="btnBack('/' + tenant + '/')" v-if="tenant === $route.params.tenantName">Back {{ tenant }}</q-btn>
           <q-btn color="secondary" @click="btnBack('/' + tenant + '/')" v-if="tenant !== $route.params.tenantName">Back {{ tenant }}</q-btn>
         </div>
      </div>
    </div>
  </q-page>
</template>

<style>
</style>

<script>
import { Notify } from 'quasar'
import { useUserManagementClientStoreStore } from 'stores/saasUserManagementClientStore'
import saasApiClientCallBackend from '../saasAPiClientCallBackend'

export default {
  name: 'DebugInformation',
  setup () {
    const store = useUserManagementClientStoreStore()
    return { store }
  },
  data () {
    return {
      possibleTenants: [
        '', 'defaulttenant'
      ]
    }
  },
  methods: {
    callbackend () {
      this.callbackendInt({ numCallsToDo: 10 })
    },
    callbackendInt ({ numCallsToDo }) {
      const pageObj = this
      if (numCallsToDo === 0) {
        return
      }
      const callback = {
        ok: function (response) {
          Notify.create({
            color: 'positive',
            message: 'Success response received - ' + JSON.stringify(response.data)
          })
          console.log(response)
          pageObj.callbackendInt({ numCallsToDo: numCallsToDo - 1 })
        },
        error: function (response) {
          Notify.create({
            color: 'negative',
            message: 'ERROR response received - not stopping!'
          })
          console.log('ERROR response received - not stopping!', response)
          pageObj.callbackendInt({ numCallsToDo: numCallsToDo - 1 })
        }
      }
      saasApiClientCallBackend.callApi({
        prefix: 'info',
        router: this.$router,
        store: this.store,
        path: '/serverinfo',
        method: 'get',
        postdata: undefined,
        callback
      })
    },
    forcereload () {
      // Clear all caches - https://stackoverflow.com/questions/54376355/clear-workbox-cache-of-all-content
      caches.keys().then(cacheNames => {
        cacheNames.forEach(cacheName => {
          caches.delete(cacheName)
        })
      })
      window.location.reload(true)
    },
    btnBack (url) {
      try {
        this.$router.replace('' + url).catch((myerr) => {
          // console.log('Error going back 2', myerr)
          //  Ignoring this error
        })
      } catch {
        console.log('Error going back')
      }
    }
  },
  computed: {
    isAdminUser () {
      return this.store.hasRole('frontendadmin')
    },
    isLoggedIn () {
      return this.store.isLoggedIn
    },
    loginUIBaseURL () {
      return this.store.loginService
    },
    endpointInfo () {
      return this.store.endpointInfo
    }
  }
}
</script>
