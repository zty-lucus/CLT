import { setActivePinia, createPinia } from 'pinia'
import { beforeEach } from 'vitest'

beforeEach(() => {
  localStorage.clear()
  setActivePinia(createPinia())
})
