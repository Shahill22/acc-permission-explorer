<template>
  <div class="q-pa-xl flex flex-center column">
    <q-card class="q-pa-lg" style="min-width: 320px">
      <div class="text-h6 q-mb-md">ACC Permissions Explorer</div>
      <q-btn label="Sign in with Autodesk" color="primary" @click="signin" />
    </q-card>
  </div>
</template>

<script setup>
import http from 'src/lib/http'
const signin = async () => {
  const { data } = await http.get('/auth/login')
  window.location.href = data.auth_url // redirects to Autodesk OAuth
}
</script>
