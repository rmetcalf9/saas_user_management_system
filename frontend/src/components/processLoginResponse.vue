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

var removeParamsFromUrlPath = function (params, path) {
  var a = path.split('?')
  if (a.length === 1) {
    return path // There are no params
  }
  var output = a[0]
  var b = a[1].split('&')
  var numAdded = 0
  for (var idx in b) {
    var c = b[idx].split('=')
    if (!params.includes(c[0])) {
      numAdded += 1
      if (numAdded === 1) {
        output += '?'
      } else {
        output += '&'
      }
      output += b[idx]
    }
  }
  return output
}

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

        // jwt-auth-cookie can sometimes be set by older apps (dockjob)
        // and needs to be cleared
        TTT.$q.cookies.remove('jwt-auth-cookie')

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

        // Not setting jwt-auth-cookie - this should now be done by the frontend once it has done inital refresh
        // console.log('AA:' + JSON.stringify(response.data))

        // no string contains in chrome: https://stackoverflow.com/questions/19589465/why-javascript-contains-property-is-not-working-in-chrome-browser

        returnAddressToUse = removeParamsFromUrlPath(['jwtretervialtoken'], returnAddressToUse)

        // if (returnAddressToUse.indexOf('?') > -1) {
        //   returnAddressToUse = returnAddressToUse + '&jwtretervialtoken=' + response.data.refresh.token
        // } else {
        //   returnAddressToUse = returnAddressToUse + '?jwtretervialtoken=' + response.data.refresh.token
        // }
        if ((returnAddressToUse.match(/\?/g) || []).length === 0) {
          // There are no question marks in string
          returnAddressToUse = returnAddressToUse + '?jwtretervialtoken=' + response.data.refresh.token
        } else {
          returnAddressToUse = returnAddressToUse + '&jwtretervialtoken=' + response.data.refresh.token
        }

        console.log('Redirecting back to main site:', returnAddressToUse)
        window.location.href = returnAddressToUse
      } else {
        // console.log('response:', response.data.possibleUsers)
        var items = []
        for (var x in response.data.possibleUsers) {
          // console.log(response.data.possibleUsers[x])
          items.push({label: response.data.possibleUsers[x].known_as + ' (' + response.data.possibleUsers[x].UserID + ')', value: response.data.possibleUsers[x].UserID})
        }
        // console.log(items)
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
