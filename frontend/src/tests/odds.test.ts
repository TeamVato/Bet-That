import { beforeAll, afterAll, afterEach, test, expect } from 'vitest'
import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'
import { api } from '@/utils/api'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const server = setupServer(
  http.get(`${BASE_URL}/odds/best`, () => {
    return HttpResponse.json({ items: [{ game_id:'NE@DEN-2025-10-05', market:'spread', price_home:1.91, price_away:1.91, ts:'2025-09-26T15:30:00Z' }] })
  })
)

beforeAll(()=>server.listen())
afterEach(()=>server.resetHandlers())
afterAll(()=>server.close())

test('loads odds best', async ()=>{
  const data = await api.oddsBest()
  expect(data.items.length).toBe(1)
})
