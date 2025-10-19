import axios from 'axios'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE,
  withCredentials: true, // send/receive cookies for Django session
})

http.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response && err.response.status === 401) {
      window.location.href = '/#/login' // hash router default in Quasar
    }
    return Promise.reject(err)
  },
)

export default http
