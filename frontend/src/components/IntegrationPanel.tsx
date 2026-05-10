import { useState } from 'react'
import { GitMerge, ArrowRight, Check, X, BarChart3, Shield, BookOpen } from 'lucide-react'
import { knowledgeApi } from '../services/api'
import { useAppStore } from '../stores/useAppStore'
import type { IntegrationResult, IntegrationPair } from '../types'
import toast from 'react-hot-toast'

const DECISION_LABELS = {
  merge: { label: '合并', color: 'bg-blue-100 text-blue-700', icon: GitMerge },
  keep: { label: '保留', color: 'bg-green-100 text-green-700', icon: Check },
  remove: { label: '移除', color: 'bg-red-100 text-red-700', icon: X },
}

export default function IntegrationPanel() {
  const { integrationResult, setIntegrationResult, setGraph } = useAppStore()
  const [loading, setLoading] = useState(false)
  const [applying, setApplying] = useState(false)

  const handleIntegrate = async () => {
    setLoading(true)
    try {
      const { result } = await knowledgeApi.integrate()
      setIntegrationResult(result)
      if (result) {
        const ratio = (result.compression_ratio * 100).toFixed(1)
        toast.success(`整合完成！压缩率 ${ratio}%，找到 ${result.pairs.length} 组相似知识点`)
      }
    } catch {
      toast.error('整合分析失败')
    }
    setLoading(false)
  }

  const handleApply = async () => {
    if (!integrationResult) return
    setApplying(true)
    try {
      const res = await knowledgeApi.applyIntegration(integrationResult)
      setGraph(res.graph)
      setIntegrationResult(null)
      toast.success('整合方案已应用到知识图谱')
    } catch {
      toast.error('应用失败')
    }
    setApplying(false)
  }

  if (!integrationResult) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-6">
        <div className="w-16 h-16 rounded-2xl bg-indigo-100 flex items-center justify-center">
          <GitMerge className="w-8 h-8 text-indigo-600" />
        </div>
        <div className="text-center">
          <h3 className="text-lg font-bold text-gray-900">跨教材知识整合</h3>
          <p className="text-sm text-gray-500 mt-1 max-w-xs">
            语义对齐多本教材的知识点，去重合并，压缩至原始体量30%以内
          </p>
        </div>
        <button onClick={handleIntegrate} disabled={loading} className="btn-primary px-8">
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              LLM分析中...
            </span>
          ) : '开始跨教材整合分析'}
        </button>
      </div>
    )
  }

  const ratio = integrationResult.compression_ratio
  const ratioPercent = (ratio * 100).toFixed(1)
  const isTargetMet = ratio <= 0.30

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-bold text-lg">整合方案</h3>
          <p className="text-sm text-gray-500">
            {integrationResult.original_count} → {integrationResult.final_count} 个知识点
          </p>
        </div>
        <div className="flex gap-2">
          <button onClick={handleIntegrate} disabled={loading} className="btn-secondary text-sm">
            {loading ? '重新分析中...' : '重新分析'}
          </button>
          <button onClick={handleApply} disabled={applying} className="btn-primary text-sm">
            {applying ? '应用中...' : '应用整合方案'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="card bg-gradient-to-br from-indigo-50 to-white">
          <div className="flex items-center gap-2 mb-2">
            <BarChart3 className="w-4 h-4 text-indigo-600" />
            <span className="text-xs font-medium text-indigo-600">压缩率</span>
          </div>
          <div className="flex items-end gap-1">
            <span className={`text-2xl font-bold ${isTargetMet ? 'text-green-600' : 'text-amber-600'}`}>
              {ratioPercent}%
            </span>
            <span className="text-xs text-gray-400 mb-1">/ 目标 30%</span>
          </div>
          <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${isTargetMet ? 'bg-green-500' : 'bg-amber-500'}`}
              style={{ width: `${Math.min(ratio * 100, 100)}%` }}
            />
          </div>
          <div className="mt-1 flex justify-between text-xs text-gray-400">
            <span>原文 {integrationResult.original_text_chars.toLocaleString()} 字</span>
            <span>精华 {integrationResult.final_text_chars.toLocaleString()} 字</span>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-green-50 to-white">
          <div className="flex items-center gap-2 mb-2">
            <Shield className="w-4 h-4 text-green-600" />
            <span className="text-xs font-medium text-green-600">质量控制</span>
          </div>
          <div className="space-y-1 text-xs">
            <div className="flex justify-between">
              <span className="text-gray-500">依赖完整性</span>
              <span className={integrationResult.integrity_report?.status === 'ok' ? 'text-green-600' : 'text-amber-600'}>
                {integrationResult.integrity_report?.status === 'ok' ? '✓ 完整' : '⚠ 有断裂'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">保留知识点</span>
              <span className="font-medium">{integrationResult.integrity_report?.total_preserved || integrationResult.final_count}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="flex items-center gap-2 mb-3">
          <BookOpen className="w-4 h-4 text-gray-600" />
          <span className="text-sm font-medium">决策统计</span>
        </div>
        <div className="grid grid-cols-3 gap-3">
          <div className="text-center p-2 bg-blue-50 rounded-lg">
            <div className="text-xl font-bold text-blue-600">{integrationResult.merge_count}</div>
            <div className="text-xs text-blue-500">合并</div>
          </div>
          <div className="text-center p-2 bg-green-50 rounded-lg">
            <div className="text-xl font-bold text-green-600">{integrationResult.keep_count}</div>
            <div className="text-xs text-green-500">保留</div>
          </div>
          <div className="text-center p-2 bg-red-50 rounded-lg">
            <div className="text-xl font-bold text-red-600">{integrationResult.remove_count}</div>
            <div className="text-xs text-red-500">移除</div>
          </div>
        </div>
      </div>

      {integrationResult.coverage_report && Object.keys(integrationResult.coverage_report).length > 0 && (
        <div className="card">
          <div className="text-sm font-medium mb-3">分类保留率</div>
          <div className="space-y-2">
            {Object.entries(integrationResult.coverage_report).map(([type, info]) => (
              <div key={type} className="flex items-center gap-3">
                <span className="text-xs text-gray-500 w-16">{type}</span>
                <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${info.rate >= 0.6 ? 'bg-green-500' : 'bg-amber-500'}`}
                    style={{ width: `${info.rate * 100}%` }}
                  />
                </div>
                <span className="text-xs text-gray-600 w-20 text-right">
                  {info.preserved}/{info.original} ({(info.rate * 100).toFixed(0)}%)
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {integrationResult.pairs.length > 0 && (
        <div className="space-y-3">
          <div className="text-sm font-medium text-gray-700">
            整合决策明细 ({integrationResult.pairs.length} 组)
          </div>
          {integrationResult.pairs.map((pair, i) => (
            <IntegrationCard key={i} pair={pair} />
          ))}
        </div>
      )}
    </div>
  )
}

function IntegrationCard({ pair }: { pair: IntegrationPair }) {
  const decision = DECISION_LABELS[pair.decision]
  const Icon = decision.icon

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-3">
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${decision.color}`}>
          <Icon className="w-3 h-3 inline mr-1" />{decision.label}
        </span>
        <span className="text-xs text-gray-400">相似度 {(pair.similarity * 100).toFixed(0)}%</span>
      </div>
      <div className="flex items-start gap-3 text-sm">
        <div className="flex-1 p-3 bg-blue-50 rounded-lg">
          <p className="font-medium text-blue-800">{pair.kp_a.name}</p>
          <p className="text-xs text-blue-600 mt-1">《{pair.kp_a.textbook_name}》· {pair.kp_a.chapter_title}</p>
          <p className="text-xs text-gray-600 mt-1 line-clamp-2">{pair.kp_a.description}</p>
        </div>
        <ArrowRight className="w-5 h-5 text-gray-400 shrink-0 mt-4" />
        <div className="flex-1 p-3 bg-gray-50 rounded-lg">
          <p className="font-medium text-gray-800">{pair.kp_b.name}</p>
          <p className="text-xs text-gray-600 mt-1">《{pair.kp_b.textbook_name}》· {pair.kp_b.chapter_title}</p>
          <p className="text-xs text-gray-600 mt-1 line-clamp-2">{pair.kp_b.description}</p>
        </div>
      </div>
      <p className="text-xs text-gray-500 mt-2">💡 {pair.reason}</p>
      {pair.merged_content && (
        <div className="mt-2 p-2 bg-green-50 rounded text-xs text-green-800 border border-green-200">
          <span className="font-medium">合并后：</span>{pair.merged_content}
        </div>
      )}
    </div>
  )
}
