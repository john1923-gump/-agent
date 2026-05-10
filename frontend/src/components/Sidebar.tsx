import { BookOpen, GitBranch, MessageSquare, Users, Swords, Sparkles } from 'lucide-react'
import { useAppStore } from '../stores/useAppStore'

const tabs = [
  { key: 'textbook' as const, label: '教材管理', icon: BookOpen, desc: '上传解析教材' },
  { key: 'graph' as const, label: '知识图谱', icon: GitBranch, desc: '图谱可视化' },
  { key: 'qa' as const, label: '智能问答', icon: MessageSquare, desc: 'RAG精准问答' },
  { key: 'teacher' as const, label: '教师对话', icon: Users, desc: '审阅与修改' },
  { key: 'arena' as const, label: '竞学堂', icon: Swords, desc: '对抗式学习' },
]

export default function Sidebar() {
  const { sidebarTab, setSidebarTab, textbooks, graph } = useAppStore()

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col shrink-0">
      <div className="p-5 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-primary-600" />
          <h1 className="text-lg font-bold text-gray-900">学科知识整合</h1>
        </div>
        <p className="text-xs text-gray-500 mt-1">智能体 · 竞学堂</p>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        {tabs.map(t => (
          <button
            key={t.key}
            onClick={() => setSidebarTab(t.key)}
            className={`sidebar-item w-full text-left ${sidebarTab === t.key ? 'active' : 'text-gray-600'}`}
          >
            <t.icon className="w-5 h-5" />
            <div>
              <div className="text-sm">{t.label}</div>
              <div className="text-xs text-gray-400">{t.desc}</div>
            </div>
          </button>
        ))}
      </nav>

      <div className="p-4 border-t border-gray-100 space-y-2">
        <div className="flex justify-between text-xs text-gray-500">
          <span>已加载教材</span>
          <span className="font-medium text-gray-700">{textbooks.length}</span>
        </div>
        <div className="flex justify-between text-xs text-gray-500">
          <span>知识节点</span>
          <span className="font-medium text-gray-700">{graph.nodes.length}</span>
        </div>
        <div className="flex justify-between text-xs text-gray-500">
          <span>知识关系</span>
          <span className="font-medium text-gray-700">{graph.edges.length}</span>
        </div>
      </div>
    </aside>
  )
}
