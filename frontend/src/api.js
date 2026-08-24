const API_URL = import.meta.env.VITE_API_URL || ''

async function request(path, options = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (res.status === 204) return null
  const body = await res.json().catch(() => null)
  if (!res.ok) {
    const detail = body?.detail
    let message = `Erro ${res.status}`
    if (Array.isArray(detail)) {
      message = detail.map((e) => e.msg || e.loc.join('.')).join('; ')
    } else if (typeof detail === 'string') {
      message = detail
    }
    throw new Error(message)
  }
  return body
}

export function listRecords(params = {}) {
  const qs = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => {
    if (v !== '' && v !== null && v !== undefined) qs.set(k, v)
  })
  return request(`/records?${qs.toString()}`)
}

export function getRecord(id) {
  return request(`/records/${id}`)
}

export function createRecord(data) {
  return request('/records', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function updateRecord(id, data) {
  return request(`/records/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export function deleteRecord(id) {
  return request(`/records/${id}`, { method: 'DELETE' })
}

export const CONDITION_LABELS = {
  mint: 'Mint (NOVO)',
  excellent: 'Excelente',
  very_good: 'Muito Bom',
  good: 'Bom',
  fair: 'Regular',
  poor: 'Pobre',
}
