const routes = [
  {
    path: '/login',
    component: () => import('pages/LoginPage.vue'),
  },
  {
    path: '/',
    component: () => import('layouts/ExplorerLayout.vue'),
    children: [{ path: '', component: () => import('pages/ExplorerPage.vue') }],
  },
  // Always leave this as last one
  { path: '/:catchAll(.*)*', component: () => import('pages/ErrorNotFound.vue') },
]

export default routes
