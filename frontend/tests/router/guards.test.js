import { describe, it, expect, beforeEach } from 'vitest'
import { createRouter, createMemoryHistory } from 'vue-router'

function createTestRouter() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/login', component: { template: '<div/>' } },
      { path: '/register', component: { template: '<div/>' } },
      { path: '/home', component: { template: '<div/>' }, meta: { requiresAuth: true } },
      { path: '/profile', component: { template: '<div/>' }, meta: { requiresAuth: true } },
      { path: '/contacts', component: { template: '<div/>' }, meta: { requiresAuth: true } },
      { path: '/', redirect: '/home' },
    ],
  })

  router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')
    if (to.meta.requiresAuth && !token) {
      next('/login')
    } else {
      next()
    }
  })

  return router
}

describe('AuthNavigationGuard', () => {
  let router

  beforeEach(() => {
    localStorage.clear()
    router = createTestRouter()
  })

  it('allows navigation to /login without token', async () => {
    await router.push('/login')
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('allows navigation to /register without token', async () => {
    await router.push('/register')
    expect(router.currentRoute.value.path).toBe('/register')
  })

  it('redirects to /login when accessing auth route without token', async () => {
    await router.push('/home')
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('redirects to /login when accessing /profile without token', async () => {
    await router.push('/profile')
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('allows navigation to auth route with token', async () => {
    localStorage.setItem('token', 'abc')
    await router.push('/home')
    expect(router.currentRoute.value.path).toBe('/home')
  })

  it('root path redirects to /home', async () => {
    localStorage.setItem('token', 'abc')
    await router.push('/')
    expect(router.currentRoute.value.path).toBe('/home')
  })

  it('root path without token redirects to /login', async () => {
    await router.push('/')
    expect(router.currentRoute.value.path).toBe('/login')
  })
})
