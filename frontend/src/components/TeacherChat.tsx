import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, GitMerge, Loader2, BookOpen, Edit3, CheckCircle } from 'lucide-react'
import { qaApi } from '../services/api'
import { useAppStore } from '../stores/useAppStore'
import type { ChatMessage } from '../types'
import toast from 'react-hot-toast'

const SUGGESTED_QUESTIONS = [
  '为什么细胞膜和细胞质被保留为两个独立知识点？',
  '帮我把"细胞膜"和"cell membrane"合并',
  '当前整合方案的压缩率是多少？',
  '哪些知识点被移除了？原因是什么？',
  '请解释"同概念"关系的含义',
  '把所有"现象"类知识点标记为核心',
]

export default function TeacherChat() {
  const { integrationResult, graph, knowledgePoints, addChatMessage, clearChat, chatHistory, setGraph } = useAppStore()
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [graphUpdated, setGraphUpdated] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [chatHistory])

  const handleSend = async (message?: string) => {
    const msg = message || input.trim()
    if (!msg || loading) return

    const userMsg: ChatMessage = { role: 'user', content: msg }
    addChatMessage(userMsg)
    setInput('')
    setLoading(true)

    try {
      const { reply, graph_updated } = await qaApi.teacherChat(msg, chatHistory)
      const assistantMsg: ChatMessage = { role: 'assistant', content: reply }
      addChatMessage(assistantMsg)

      if (graph_updated) {
        setGraphUpdated(true)
        toast.success('知识图谱已根据教师反馈更新')
        setTimeout(() => setGraphUpdated(false), 3000)
      }
    } catch {
      const errorMsg: ChatMessage = { role: 'assistant', content: '抱歉，处理您的问题时出现了错误，请稍后重试。' }
      addChatMessage(errorMsg)
    }
    setLoading(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const renderMessage = (msg: ChatMessage, idx: number) => {
    const isUser = msg.role === 'user'
    const content = msg.content.replace(/\[ACTION:[^\]]+\]/g, '').trim()

    return (
      <div key={idx} className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
          isUser ? 'bg-indigo-100' : 'bg-emerald-100'
        }`}>
          {isUser ? <User className="w-4 h-4 text-indigo-600" /> : <Bot className="w-4 h-4 text-emerald-600" />}
        </div>
        <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? 'bg-indigo-600 text-white rounded-tr-md'
            : 'bg-white border border-gray-200 shadow-sm rounded-tl-md'
        }`}>
          <div className="whitespace-pre-wrap">{content}</div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Edit3 className="w-5 h-5 text-indigo-600" />
            教师对话
          </h2>
          <p className="text-sm text-gray-500 mt-0.5">审阅整合决策 · 调整知识图谱 · 讨论教学策略</p>
        </div>
        <div className="flex items-center gap-2">
          {graphUpdated && (
            <span className="flex items-center gap-1 text-xs text-green-600 bg-green-50 px-2 py-1 rounded-full animate-pulse">
              <CheckCircle className="w-3 h-3" /> 图谱已更新
            </span>
          )}
          <button onClick={clearChat} className="btn-secondary text-sm">清空对话</button>
        </div>
      </div>

      <div className="flex gap-4 flex-1 min-h-0">
        <div className="flex-1 flex flex-col card overflow-hidden">
          <div ref={scrollRef} className="flex-1 overflow-auto p-4 space-y-4">
            {chatHistory.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full gap-4 text-center">
                <div className="w-14 h-14 rounded-2xl bg-indigo-100 flex items-center justify-center">
                  <Bot className="w-7 h-7 text-indigo-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">教师助手已就绪</p>
                  <p className="text-sm text-gray-500 mt-1 max-w-sm">
                    我可以帮你解释整合决策、修改知识点、分析知识图谱结构。试试下面的问题：
                  </p>
                </div>
                <div className="flex flex-wrap gap-2 justify-center max-w-lg">
                  {SUGGESTED_QUESTIONS.map((q, i) => (
                    <button
                      key={i}
                      onClick={() => handleSend(q)}
                      className="px-3 py-1.5 rounded-full bg-indigo-50 text-indigo-600 text-xs hover:bg-indigo-100 transition-colors"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}
            {chatHistory.map((msg, i) => renderMessage(msg, i))}
            {loading && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-emerald-600" />
                </div>
                <div className="bg-white border border-gray-200 shadow-sm rounded-2xl rounded-tl-md px-4 py-3">
                  <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
                </div>
              </div>
            )}
          </div>

          <div className="border-t border-gray-100 p-4">
            <div className="flex gap-2">
              <textarea
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={'输入问题或指令，如"把XX和YY改为保留"'}
                className="flex-1 input-field resize-none"
                rows={2}
              />
              <button onClick={() => handleSend()} disabled={!input.trim() || loading} className="btn-primary self-end">
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        <div className="w-72 card overflow-auto shrink-0">
          <h3 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
            <BookOpen className="w-4 h-4" />
            当前知识图谱
          </h3>
          <div className="space-y-2 text-xs">
            <div className="p-2 bg-gray-50 rounded-lg">
              <div className="font-medium text-gray-700">节点总数</div>
              <div className="text-lg font-bold text-indigo-600">{graph.nodes.length}</div>
            </div>
            <div className="p-2 bg-gray-50 rounded-lg">
              <div className="font-medium text-gray-700">关系总数</div>
              <div className="text-lg font-bold text-indigo-600">{graph.edges.length}</div>
            </div>
            <div className="p-2 bg-gray-50 rounded-lg">
              <div className="font-medium text-gray-700">知识点</div>
              <div className="text-lg font-bold text-indigo-600">{knowledgePoints.length}</div>
            </div>
          </div>

          {integrationResult && (
            <div className="mt-4 pt-4 border-t border-gray-100">
              <h4 className="font-medium text-gray-700 mb-2 flex items-center gap-1">
                <GitMerge className="w-3.5 h-3.5" /> 最近整合结果
              </h4>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-500">压缩率</span>
                  <span className={`font-medium ${integrationResult.compression_ratio <= 0.3 ? 'text-green-600' : 'text-amber-600'}`}>
                    {(integrationResult.compression_ratio * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">知识点</span>
                  <span>{integrationResult.original_count} → {integrationResult.final_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">合并</span>
                  <span className="text-blue-600">{integrationResult.merge_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">保留</span>
                  <span className="text-green-600">{integrationResult.keep_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">移除</span>
                  <span className="text-red-600">{integrationResult.remove_count}</span>
                </div>
              </div>
            </div>
          )}

          {knowledgePoints.length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-100">
              <h4 className="font-medium text-gray-700 mb-2">知识点列表</h4>
              <div className="space-y-1 max-h-60 overflow-auto">
                {knowledgePoints.slice(0, 20).map(kp => (
                  <div key={kp.id} className="flex items-center gap-2 p-1.5 hover:bg-gray-50 rounded text-xs">
                    <span className={`w-2 h-2 rounded-full ${
                      kp.type === '概念' ? 'bg-blue-500' :
                      kp.type === '定理' ? 'bg-red-500' :
                      kp.type === '方法' ? 'bg-green-500' : 'bg-amber-500'
                    }`} />
                    <span className="flex-1 truncate">{kp.name}</span>
                    <span className="text-gray-400">{kp.type}</span>
                  </div>
                ))}
                {knowledgePoints.length > 20 && (
                  <div className="text-gray-400 text-center">还有 {knowledgePoints.length - 20} 个...</div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
