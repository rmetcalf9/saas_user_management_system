import { defineStore, acceptHMRUpdate } from 'pinia'

// This store remembers the input params sent by the app calling the login

export const useInputParamsStore = defineStore('inputParamsStore', {
  state: () => ({
    usersystemReturnaddress: '',
    usersystemMessage: ''
  }),
  getters: {},
  actions: {
    setParams ({ usersystemReturnaddress, usersystemMessage }) {
      this.usersystemReturnaddress = usersystemReturnaddress
      this.usersystemMessage = usersystemMessage
    },
    clearUsersystemMessage () {
      this.usersystemMessage = ''
    }
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useInputParamsStore, import.meta.hot))
}
