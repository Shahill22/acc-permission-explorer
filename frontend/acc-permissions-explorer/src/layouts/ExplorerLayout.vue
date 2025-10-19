<template>
  <q-layout view="hHh LpR fFf">
    <q-header elevated>
      <q-toolbar>
        <q-toolbar-title>ACC Permissions Explorer</q-toolbar-title>
        <q-btn flat label="Logout" @click="logout" />
      </q-toolbar>
    </q-header>

    <q-drawer show-if-above side="left" width="340">
      <slot name="sidebar" />
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { useAuthStore } from 'src/stores/auth'
const auth = useAuthStore()

const logout = async () => {
  await auth.logout()
  window.location.href = '/#/login'
}
</script>
