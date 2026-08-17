import { defineStore, acceptHMRUpdate } from 'pinia'

const SESSION_STORAGE_KEY = 'inputParams'

// This store remembers the input params sent by the app calling the login

export const useInputParamsStore = defineStore('inputParamsStore', {
  state: () => {
    let storedParams = {}

    try {
      storedParams = JSON.parse(
        sessionStorage.getItem(SESSION_STORAGE_KEY) || '{}'
      )
    } catch (e) {
      console.log('RJMDEBUG inputParamsStore invalid session storage')
    }

    return {
      usersystemReturnaddress: storedParams.usersystemReturnaddress || '',
      usersystemMessage: storedParams.usersystemMessage || ''
    }
  },
  getters: {
    getUsersystemReturnaddress: (state) => state.usersystemReturnaddress,
    getUsersystemMessage: (state) => state.usersystemMessage
  },
  actions: {
    setParams ({ usersystemReturnaddress, usersystemMessage }) {
      this.usersystemReturnaddress = usersystemReturnaddress
      this.usersystemMessage = usersystemMessage
      sessionStorage.setItem(
        SESSION_STORAGE_KEY,
        JSON.stringify({
          usersystemReturnaddress,
          usersystemMessage
        })
      )
    },
    clearUsersystemMessage () {
      this.usersystemMessage = ''
    }
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useInputParamsStore, import.meta.hot))
}
