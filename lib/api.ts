const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'

export async function getLLMConfig() {
  const res = await fetch(`${API_BASE}/api/llm/config`)
  return res.json()
}

export async function saveLLMConfig(config: {
  provider: string
  api_key: string
  base_url?: string
}) {
  const res = await fetch(`${API_BASE}/api/llm/config`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(config),
  })
  return res.json()
}
