import { defineStore } from 'pinia'
import http from 'src/lib/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({ authenticated: false }),
  actions: {
    async refresh() {
      const { data } = await http.get('/auth/me')
      this.authenticated = !!data.authenticated
    },
    async logout() {
      await http.get('/auth/logout')
      this.authenticated = false
    },
  },
})
