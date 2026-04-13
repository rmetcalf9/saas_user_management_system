<template>
  <div></div>
</template>

<script>
import { defineComponent } from 'vue'
import { Cookies, Loading, Notify } from 'quasar'
import { useInputParamsStore } from 'stores/inputParams'
import { useTenantInfoStore } from 'stores/tenantInfo'
import saasAPiClientCallBackend from '../saasAPiClientCallBackend.js'

function removeParamsFromUrlPath (params, path) {
  const a = path.split('?')
  if (a.length === 1) {
    return path // There are no params
  }
  let output = a[0]
  const b = a[1].split('&')
  let numAdded = 0
  for (const idx in b) {
    const c = b[idx].split('=')
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

export default defineComponent({
  name: 'ProcessLoginResponseComponent',
  setup () {
    const inputParamsStore = useInputParamsStore()
    const tenantInfoStore = useTenantInfoStore()
    return { tenantInfoStore, inputParamsStore }
  },
  methods: {
    processLoginOKResponse (response, loginRequestPostData) {
      // const TTT = this
      // Decide if we got a JWTToken back or an identity selection list
      //   either forward to the JWTToken setting page or
      //   the identity selection page
      let gotLogin = false
      if ('jwtData' in response.data) {
        gotLogin = true
      }
      if (gotLogin) {
        let returnAddressToUse = this.inputParamsStore.usersystemReturnaddress

        // jwt-auth-cookie can sometimes be set by older apps (dockjob)
        // and needs to be cleared
        Cookies.remove('jwt-auth-cookie', { path: '/' })

        // Not setting jwt-auth-cookie - this should now be done by the frontend once it has done inital refresh
        // console.log('AA:' + JSON.stringify(response.data))

        // no string contains in chrome: https://stackoverflow.com/questions/19589465/why-javascript-contains-property-is-not-working-in-chrome-browser

        returnAddressToUse = removeParamsFromUrlPath(['jwtretervialtoken'], returnAddressToUse)

        if ((returnAddressToUse.match(/\?/g) || []).length === 0) {
          // There are no question marks in string
          returnAddressToUse = returnAddressToUse + '?jwtretervialtoken=' + response.data.refresh.token
        } else {
          returnAddressToUse = returnAddressToUse + '&jwtretervialtoken=' + response.data.refresh.token
        }

        console.log('Redirecting back to main site:', returnAddressToUse)
        window.location.href = returnAddressToUse
      } else {
        this.processOkResponseDuplicateUserAccounts(response, loginRequestPostData)
      }
    },
    processOkResponseDuplicateUserAccounts (response, loginRequestPostData) {
      // console.log('response:', response.data.possibleUsers)
      const TTT = this
      const items = []
      for (const x in response.data.possibleUsers) {
        // console.log(response.data.possibleUsers[x])
        items.push({ label: response.data.possibleUsers[x].known_as + ' (' + response.data.possibleUsers[x].UserID + ')', value: response.data.possibleUsers[x].UserID })
      }
      // console.log(items)
      TTT.$q.dialog({
        title: 'Select User',
        message: 'You have access to multiple user accounts on this site',
        options: {
          type: 'radio',
          model: items[0].value,
          items
        },
        cancel: true,
        preventClose: true,
        color: 'secondary'
      }).onOk(data => {
        const postUserSelectionCallback = {
          ok: function (response) {
            Loading.hide()
            TTT.processLoginOKResponse(response, loginRequestPostData)
          },
          error: function (response) {
            Loading.hide()
            Notify.create('Login Failed')
          }
        }
        Loading.show()
        loginRequestPostData.UserID = data
        saasAPiClientCallBackend.callApi({
          prefix: 'login',
          router: this.$router,
          path: '/' + this.tenantInfoStore.selectedAuthTenantName + '/authproviders',
          method: 'POST',
          postdata: loginRequestPostData,
          callback: postUserSelectionCallback
        })
      })
    }
  }
})
</script>
