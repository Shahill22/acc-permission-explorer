<template>
  <ExplorerLayout>
    <template #sidebar>
      <div class="q-pa-sm">
        <q-input dense v-model="filter" placeholder="Filter..." class="q-mb-sm" />
        <q-tree
          :nodes="nodes"
          node-key="id"
          :filter="filter"
          :loading="loadingTree"
          @lazy-load="loadChildren"
          default-expand-all
        />
      </div>
    </template>

    <q-page padding>
      <q-breadcrumbs class="q-mb-md" v-if="breadcrumbs.length">
        <q-breadcrumbs-el
          v-for="(b, i) in breadcrumbs"
          :key="i"
          :label="b.label"
          clickable
          @click="navigateTo(b)"
        />
      </q-breadcrumbs>

      <q-card>
        <q-card-section>
          <div class="text-h6">Folder Contents</div>
          <q-table :rows="items" :columns="cols" row-key="id" :loading="loadingItems" flat />
        </q-card-section>
      </q-card>

      <q-card class="q-mt-md">
        <q-card-section>
          <div class="text-h6">Effective Permissions</div>
          <q-table :rows="perms" :columns="permCols" row-key="id" :loading="loadingPerms" flat />
          <div v-if="!loadingPerms && !perms.length" class="text-grey q-mt-sm">
            No permissions found.
          </div>
        </q-card-section>
      </q-card>
    </q-page>
  </ExplorerLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import http from 'src/lib/http'
import { useAuthStore } from 'src/stores/auth'
import ExplorerLayout from 'src/layouts/ExplorerLayout.vue'

const auth = useAuthStore()

const loadingTree = ref(false)
const loadingItems = ref(false)
const loadingPerms = ref(false)
const filter = ref('')
const nodes = ref([])
const breadcrumbs = ref([])
const items = ref([])
const perms = ref([])

const cols = [
  { name: 'name', label: 'Name', field: (r) => r?.attributes?.displayName, sortable: true },
  { name: 'type', label: 'Type', field: (r) => r?.type, sortable: true },
]
const permCols = [
  { name: 'principal', label: 'User/Role', field: 'principal' },
  { name: 'actions', label: 'Allowed Actions', field: 'actions' },
]

onMounted(init)

async function init() {
  await auth.refresh()
  if (!auth.authenticated) {
    window.location.href = '/#/login'
    return
  }
  await loadHubs()
}

async function loadHubs() {
  loadingTree.value = true
  const { data } = await http.get('/hubs')
  nodes.value = data.data.map((h) => ({
    id: `hub:${h.id}`,
    label: (h.attributes && h.attributes.name) || h.id,
    lazy: true,
    meta: { hubId: h.id },
  }))
  loadingTree.value = false
}

async function loadChildren({ node }) {
  if (node.id.startsWith('hub:')) {
    const hubId = node.meta.hubId
    const { data } = await http.get(`/projects/${hubId}`)
    node.children = data.data.map((p) => ({
      id: `proj:${p.id}`,
      label: (p.attributes && p.attributes.name) || p.id,
      lazy: true,
      meta: { projectId: p.id },
    }))
  } else if (node.id.startsWith('proj:')) {
    const projectId = node.meta.projectId
    const { data } = await http.get(`/top-folders/${projectId}`)
    node.children = data.data.map((f) => ({
      id: `folder:${projectId}:${f.id}`,
      label: (f.attributes && f.attributes.displayName) || f.id,
      lazy: true,
      meta: { projectId, folderId: f.id },
    }))
  } else if (node.id.startsWith('folder:')) {
    const { projectId, folderId } = node.meta
    const { data } = await http.get(`/folders/${projectId}/${encodeURIComponent(folderId)}`)
    node.children = data.data
      .filter((i) => i.type === 'folders')
      .map((f) => ({
        id: `folder:${projectId}:${f.id}`,
        label: (f.attributes && f.attributes.displayName) || f.id,
        lazy: true,
        meta: { projectId, folderId: f.id },
      }))
    await selectFolder(projectId, folderId, node.label)
  }
}

async function selectFolder(projectId, folderId, label) {
  breadcrumbs.value = [
    { id: projectId, label: 'Project', projectId },
    { id: folderId, label, projectId, folderId },
  ]

  loadingItems.value = true
  const { data: contents } = await http.get(`/folders/${projectId}/${encodeURIComponent(folderId)}`)
  items.value = contents.data

  loadingPerms.value = true
  try {
    const { data: permData } = await http.get(
      `/permissions/${projectId}/${encodeURIComponent(folderId)}`,
    )
    perms.value = (permData.data || []).map((row) => ({
      id: row.id || Math.random().toString(36).slice(2),
      principal:
        (row.attributes && (row.attributes.principalName || row.attributes.roleName)) || 'Unknown',
      actions: ((row.attributes && row.attributes.actions) || []).join(', '),
    }))
    // eslint-disable-next-line no-unused-vars
  } catch (error) {
    perms.value = []
  } finally {
    loadingPerms.value = false
    loadingItems.value = false
  }
}

function navigateTo() {
  // optional enhancement: re-select via tree path
}
</script>
