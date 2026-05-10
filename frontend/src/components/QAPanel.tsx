import { useState, useRef, useEffect } from 'react'
import { Send, BookOpen, Loader2, FileText } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { qaApi } from '../services/api'
import { useAppStore } from '../stores/useAppStore'
import type { ChatMessage, QAReference } from '../types'

export default function QAPanel() {
  const { textbooks } = useAppStore()
  const [messages, setMessages] = useState<(ChatMessage & { references?: QAReference[] })[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [streaming, setStreaming] = useState('')
  const [filter, setFilter] = useState<string>('')
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, streaming])

  const handleSend = async () => {
    const q = input.trim()
    if (!q || loading) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: q }])
    setLoading(true)
    setStreaming('')

    try {
      const refs: QAReference[] = []
      await qaApi.askStream(q, filter || undefined,
        (token) => setStreaming(prev => prev + token),
        (r) => refs.push(...r),
      )
      setMessages(prev => [...prev, { role: 'assistant', content: streaming || '（无回答）', references: refs }])
      setStreaming('')
    } catch {
      try {
        const res = await qaApi.ask(q, filter || undefined)
        setMessages(prev => [...prev, { role: 'assistant', content: res.answer, references: res.references }])
      } catch {
        setMessages(prev => [...prev, { role: 'assistant', content: '抱歉，回答失败，请重试。' }])
      }
    }
    setLoading(false)
    setStreaming('')
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">智能问答</h2>
          <p className="text-sm text-gray-500">基于教材知识库的RAG精准问答，带引用来源</p>
        </div>
        <select value={filter} onChange={e => setFilter(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm">
          <option value="">全部教材</option>
          {textbooks.map(t => <option key={t.id} value={t.id}>{t.filename}</option>)}
        </select>
      </div>

      <div className="flex-1 overflow-auto space-y-4 mb-4 pr-2">
        {messages.length === 0 && (
          <div className="text-center py-20 text-gray-400">
            <BookOpen className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p className="text-lg">有什么想了解的？</p>
            <p className="text-sm mt-1">基于已上传教材进行精准问答</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-ai'}>
              <ReactMarkdown className="prose prose-sm max-w-none">{msg.content}</ReactMarkdown>
              {msg.references && msg.references.length > 0 && (
                <div className="mt-3 pt-2 border-t border-gray-200">
                  <p className="text-xs text-gray-500 mb-1">📚 引用来源：</p>
                  {msg.references.map((ref, j) => (
                    <div key={j} className="flex items-start gap-2 text-xs text-gray-600 mb-1">
                      <FileText className="w-3 h-3 mt-0.5 shrink-0" />
                      <span>《{ref.textbook_name}》{ref.chapter_title} 第{ref.page}页</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {streaming && (
          <div className="flex justify-start">
            <div className="chat-bubble-ai">
              <ReactMarkdown className="prose prose-sm max-w-none">{streaming}</ReactMarkdown>
              <span className="typing-cursor" />
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="flex gap-2">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
          placeholder="输入问题..."
          className="input-field flex-1"
          disabled={loading}
        />
        <button onClick={handleSend} disabled={loading || !input.trim()} className="btn-primary px-4">
          {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
        </button>
      </div>
    </div>
  )
}
