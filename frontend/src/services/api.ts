import axios from 'axios'
import type {
  TextbookMeta, KnowledgeGraph, KnowledgePoint,
  QAResponse, ChatMessage, ArenaSession, ArenaQuestion, ArenaRound, ArenaOpponent,
} from '../types'

const api = axios.create({
  baseURL: '/api',
  timeout: 300000, // 5分钟超时
})

export const textbookApi = {
  upload: async (file: File) => {
    const form = new FormData()
    form.append('file', file)
    const { data } = await api.post('/textbooks/upload', form)
    return data as { textbook: TextbookMeta; chapter_count: number; knowledge_points: number; graph_nodes: number; graph_edges: number }
  },
  list: async () => {
    const { data } = await api.get('/textbooks/list')
    return data as TextbookMeta[]
  },
  get: async (id: string) => {
    const { data } = await api.get(`/textbooks/${id}`)
    return data
  },
  delete: async (id: string) => {
    await api.delete(`/textbooks/${id}`)
  },
  getExtractionStatus: async () => {
    const { data } = await api.get('/textbooks/extraction-status')
    return data as Record<string, { status: string; filename: string; progress?: number; total?: number; knowledge_points?: number; error?: string }>
  },
}

export const knowledgeApi = {
  getGraph: async () => {
    const { data } = await api.get('/knowledge/graph')
    return data as KnowledgeGraph
  },
  getPoints: async () => {
    const { data } = await api.get('/knowledge/points')
    return data as KnowledgePoint[]
  },
  integrate: async () => {
    const { data } = await api.post('/knowledge/integrate')
    return data
  },
  applyIntegration: async (result: any) => {
    const { data } = await api.post('/knowledge/integrate/apply', result)
    return data
  },
}

export const qaApi = {
  ask: async (question: string, textbookFilter?: string) => {
    const { data } = await api.post('/qa/ask', { question, textbook_filter: textbookFilter })
    return data as QAResponse
  },
  askStream: async (question: string, textbookFilter?: string, onToken?: (t: string) => void, onRefs?: (r: any[]) => void) => {
    const response = await fetch('/api/qa/ask/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, textbook_filter: textbookFilter }),
    })
    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    let answer = ''
    while (reader) {
      const { done, value } = await reader.read()
      if (done) break
      const text = decoder.decode(value)
      const lines = text.split('\n')
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        try {
          const payload = JSON.parse(line.slice(6))
          if (payload.type === 'token') { answer += payload.data; onToken?.(payload.data) }
          if (payload.type === 'references') onRefs?.(payload.data)
        } catch {}
      }
    }
    return answer
  },
  teacherChat: async (message: string, history: ChatMessage[]) => {
    const { data } = await api.post('/qa/teacher-chat', { message, history })
    return data as { reply: string; graph_updated: boolean }
  },
}

export const arenaApi = {
  getOpponents: async () => {
    const { data } = await api.get('/arena/opponents')
    return data as ArenaOpponent[]
  },
  start: async (mode: string = 'student', textbookFilter?: string) => {
    const { data } = await api.post('/arena/start', { mode, textbook_filter: textbookFilter })
    return data as { session: ArenaSession; question: ArenaQuestion }
  },
  answer: async (sessionId: string, answer: string) => {
    const { data } = await api.post('/arena/answer', { session_id: sessionId, answer })
    return data as { round: ArenaRound; session: ArenaSession; next_question: ArenaQuestion | null }
  },
  getSession: async (sessionId: string) => {
    const { data } = await api.get(`/arena/session/${sessionId}`)
    return data as ArenaSession
  },
}
