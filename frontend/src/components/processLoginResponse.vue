<template>
  <div>
  </div>
</template>

<script>
import {
  Notify,
  Loading
} from 'quasar'
import frontendFns from '../frontendFns.js'

export default {
  name: 'SecuritySettings',
  data () {
    return {}
  },
  methods: {
    processLoginOKResponse (response, loginRequestPostData) {
      var TTT = this
      // Decide if we got a JWTToken back or an identity selection list
      //   either forward to the JWTToken setting page or
      //   the identity selection page
      var gotLogin = false
      if ('jwtData' in response.data) {
        gotLogin = true
      }
      if (gotLogin) {
        var returnAddressToUse = null
        if (frontendFns.isSet(TTT.$store.state.globalDataStore.usersystemReturnaddressInternal)) {
          TTT.$q.cookies.set('usersystemUserCredentials', response.data, {expires: 1, path: '/'})
          var a = TTT.$store.state.globalDataStore.usersystemReturnaddressInternal
          TTT.$store.commit('globalDataStore/clearUsersystemReturnaddressInternal')
          TTT.$router.replace(a)
          return
        } else {
          if (!frontendFns.isSet(TTT.$store.state.globalDataStore.usersystemReturnaddress)) {
            Notify.create('Error - Webapplication failed to provide return address')
            return
          }
          returnAddressToUse = TTT.$store.state.globalDataStore.usersystemReturnaddress
        }
        // Expires in one day
        TTT.$q.cookies.set('usersystemUserCredentials', response.data, {expires: 1, path: '/'})
        console.log('Redirecting back to main site:', returnAddressToUse)
        window.location.href = returnAddressToUse
      } else {
        console.log('response:', response.data.possibleUsers)
        var items = []
        for (var x in response.data.possibleUsers) {
          console.log(response.data.possibleUsers[x])
          items.push({label: response.data.possibleUsers[x].known_as + ' (' + response.data.possibleUsers[x].UserID + ')', value: response.data.possibleUsers[x].UserID})
        }
        console.log(items)
        TTT.$q.dialog({
          title: 'Select User',
          message: 'You have access to mutiple user accounts on this site',
          options: {
            type: 'radio',
            model: items[0].value,
            items: items
          },
          cancel: true,
          preventClose: true,
          color: 'secondary'
        }).onOk(data => {
          var postUserSelectionCallback = {
            ok: function (response) {
              TTT.processLoginOKResponse(response, loginRequestPostData)
            },
            error: function (response) {
              Loading.hide()
              Notify.create('Login Failed')
            }
          }
          Loading.show()
          loginRequestPostData.UserID = data
          this.$store.dispatch('globalDataStore/callLoginAPI', {
            method: 'POST',
            path: '/authproviders',
            callback: postUserSelectionCallback,
            postdata: loginRequestPostData
          })
          Notify.create('Identity selection not implemented ' + data)
        })
      }
    }
  }
}
</script>

<style>
</style>
