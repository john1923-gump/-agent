import { useEffect, useRef, useState, useCallback } from 'react'
import * as echarts from 'echarts'
import { useAppStore } from '../stores/useAppStore'
import { knowledgeApi } from '../services/api'
import type { GraphNode } from '../types'
import { Search, ZoomIn, ZoomOut, Maximize2, RefreshCw } from 'lucide-react'

const TYPE_COLORS: Record<string, string> = {
  '概念': '#3b82f6',
  '定理': '#ef4444',
  '方法': '#10b981',
  '现象': '#f59e0b',
}

const TYPE_SYMBOLS: Record<string, string> = {
  '概念': 'circle',
  '定理': 'diamond',
  '方法': 'triangle',
  '现象': 'rect',
}

const TEXTBOOK_COLORS = ['#6366f1', '#ec4899', '#14b8a6', '#f97316', '#8b5cf6', '#06b6d4']

const RELATION_LABELS: Record<string, string> = {
  'prerequisite': '前置',
  'parallel': '并列',
  'contains': '包含',
  'applies_to': '应用',
  '同章节': '同章节',
  '同概念': '同概念',
}

const RELATION_COLORS: Record<string, string> = {
  'prerequisite': '#ef4444',
  'parallel': '#3b82f6',
  'contains': '#10b981',
  'applies_to': '#f59e0b',
  '同章节': '#94a3b8',
  '同概念': '#8b5cf6',
}

type ViewMode = 'force' | 'sankey'

export default function KnowledgeGraphView() {
  const chartRef = useRef<HTMLDivElement>(null)
  const chartInstance = useRef<echarts.ECharts | null>(null)
  const { graph, setGraph } = useAppStore()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [colorMode, setColorMode] = useState<'type' | 'textbook'>('type')
  const [viewMode, setViewMode] = useState<ViewMode>('force')

  useEffect(() => {
    loadGraph()
    return () => { chartInstance.current?.dispose() }
  }, [])

  useEffect(() => {
    if (chartRef.current && graph.nodes.length > 0) {
      renderChart()
    }
  }, [graph, colorMode, searchTerm, viewMode])

  const loadGraph = async () => {
    try {
      const g = await knowledgeApi.getGraph()
      setGraph(g)
    } catch {}
  }

  const renderSankeyChart = useCallback(() => {
    if (!chartRef.current) return

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current)
    }

    const chart = chartInstance.current
    const textbookSet = [...new Set(graph.nodes.map(n => n.textbook_name))]
    const typeSet = Object.keys(TYPE_COLORS)

    const links: { source: string; target: string; value: number }[] = []
    const nodeMap = new Map<string, number>()

    for (const n of graph.nodes) {
      const key = `${n.textbook_name}|||${n.type}`
      nodeMap.set(key, (nodeMap.get(key) || 0) + n.frequency)
    }

    nodeMap.forEach((value, key) => {
      const [textbook, type] = key.split('|||')
      links.push({ source: textbook, target: type, value })
    })

    const allNodes = [
      ...textbookSet.map(t => ({ name: t, itemStyle: { color: TEXTBOOK_COLORS[textbookSet.indexOf(t) % TEXTBOOK_COLORS.length] } })),
      ...typeSet.map(t => ({ name: t, itemStyle: { color: TYPE_COLORS[t] } })),
    ]

    chart.setOption({
      tooltip: { trigger: 'item', triggerOn: 'mousemove' },
      series: [{
        type: 'sankey',
        layout: 'none',
        emphasis: { focus: 'adjacency' },
        nodeAlign: 'left',
        data: allNodes,
        links,
        lineStyle: { color: 'gradient', curveness: 0.5 },
        label: { fontSize: 12 },
        nodeWidth: 20,
        nodeGap: 12,
      }],
    }, true)
  }, [graph])

  const renderForceGraph = useCallback(() => {
    if (!chartRef.current) return

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current)
    }

    const chart = chartInstance.current
    const filteredNodes = graph.nodes.filter(n =>
      !searchTerm || n.label.includes(searchTerm) || n.textbook_name.includes(searchTerm)
    )
    const filteredIds = new Set(filteredNodes.map(n => n.id))
    const filteredEdges = graph.edges.filter(e => filteredIds.has(e.source) && filteredIds.has(e.target))

    const textbookSet = [...new Set(graph.nodes.map(n => n.textbook_name))]
    const textbookColorMap = new Map(textbookSet.map((t, i) => [t, TEXTBOOK_COLORS[i % TEXTBOOK_COLORS.length]]))

    const nodes = filteredNodes.map(n => ({
      id: n.id,
      name: n.label,
      symbolSize: n.size,
      symbol: TYPE_SYMBOLS[n.type] || 'circle',
      category: colorMode === 'type' ? n.type : n.textbook_name,
      itemStyle: {
        color: colorMode === 'type' ? TYPE_COLORS[n.type] : textbookColorMap.get(n.textbook_name),
        borderColor: '#fff',
        borderWidth: 2,
        opacity: Math.max(0.5, Math.min(1, n.confidence || 0.8)),
      },
      label: { show: n.size > 15, fontSize: Math.max(10, n.size / 3) },
      tooltip: `<b>${n.label}</b><br/>类型：${n.type}<br/>教材：${n.textbook_name}<br/>章节：${n.chapter_title || '未知'}<br/>频次：${n.frequency}<br/>置信度：${((n.confidence || 0.8) * 100).toFixed(0)}%<br/>${n.description ? '描述：' + n.description : ''}`,
    }))

    const categories = colorMode === 'type'
      ? Object.keys(TYPE_COLORS).map(k => ({ name: k }))
      : textbookSet.map(t => ({ name: t }))

    const edges = filteredEdges.map(e => ({
      source: e.source,
      target: e.target,
      lineStyle: {
        width: Math.max(1, e.weight * 3),
        curveness: 0.2,
        color: RELATION_COLORS[e.relation] || '#ccc',
      },
      label: {
        show: true,
        formatter: RELATION_LABELS[e.relation] || e.relation,
        fontSize: 10,
        color: RELATION_COLORS[e.relation] || '#999',
      },
    }))

    chart.setOption({
      tooltip: { trigger: 'item', formatter: (p: any) => p.data?.tooltip || '' },
      legend: { data: categories.map(c => c.name), top: 10, textStyle: { fontSize: 12 } },
      animationDuration: 500,
      series: [{
        type: 'graph',
        layout: 'force',
        data: nodes,
        links: edges,
        categories,
        roam: true,
        draggable: true,
        force: { repulsion: 300, gravity: 0.1, edgeLength: [80, 200], layoutAnimation: true },
        emphasis: { focus: 'adjacency', lineStyle: { width: 4 } },
        lineStyle: { color: '#ccc', opacity: 0.6 },
      }],
    }, true)

    chart.off('click')
    chart.on('click', (params: any) => {
      if (params.dataType === 'node') {
        const node = graph.nodes.find(n => n.id === params.data.id)
        if (node) setSelectedNode(node)
      }
    })
  }, [graph, colorMode, searchTerm])

  const renderChart = useCallback(() => {
    if (viewMode === 'sankey') {
      renderSankeyChart()
    } else {
      renderForceGraph()
    }
  }, [viewMode, renderSankeyChart, renderForceGraph])

  const handleZoom = (factor: number) => {
    if (viewMode === 'force') {
      chartInstance.current?.dispatchAction({ type: 'graphRoam', zoom: factor })
    }
  }

  return (
    <div className="space-y-4 h-full flex flex-col">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">知识图谱</h2>
          <p className="text-sm text-gray-500">
            {graph.nodes.length} 个节点 · {graph.edges.length} 条关系 · {viewMode === 'force' ? '支持拖拽/缩放/搜索' : '教材→类型分布'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center bg-gray-100 rounded-lg p-1">
            <button onClick={() => setViewMode('force')}
              className={`px-3 py-1 text-xs rounded-md transition-colors ${viewMode === 'force' ? 'bg-white shadow-sm text-primary-600' : 'text-gray-500'}`}>
              力导向图
            </button>
            <button onClick={() => setViewMode('sankey')}
              className={`px-3 py-1 text-xs rounded-md transition-colors ${viewMode === 'sankey' ? 'bg-white shadow-sm text-primary-600' : 'text-gray-500'}`}>
              桑基图
            </button>
          </div>
          {viewMode === 'force' && (
            <div className="flex items-center bg-gray-100 rounded-lg p-1">
              <button onClick={() => setColorMode('type')}
                className={`px-3 py-1 text-xs rounded-md transition-colors ${colorMode === 'type' ? 'bg-white shadow-sm text-primary-600' : 'text-gray-500'}`}>
                按类型
              </button>
              <button onClick={() => setColorMode('textbook')}
                className={`px-3 py-1 text-xs rounded-md transition-colors ${colorMode === 'textbook' ? 'bg-white shadow-sm text-primary-600' : 'text-gray-500'}`}>
                按教材
              </button>
            </div>
          )}
          <button onClick={loadGraph} className="btn-secondary flex items-center gap-1 text-sm">
            <RefreshCw className="w-4 h-4" /> 刷新
          </button>
        </div>
      </div>

      {viewMode === 'force' && (
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="搜索知识点或教材..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="input-field pl-10"
            />
          </div>
          <button onClick={() => handleZoom(1.2)} className="btn-secondary p-2"><ZoomIn className="w-4 h-4" /></button>
          <button onClick={() => handleZoom(0.8)} className="btn-secondary p-2"><ZoomOut className="w-4 h-4" /></button>
          <button onClick={() => { chartInstance.current?.resize(); handleZoom(1) }} className="btn-secondary p-2">
            <Maximize2 className="w-4 h-4" />
          </button>
        </div>
      )}

      <div className="flex-1 flex gap-4 min-h-0">
        <div ref={chartRef} className="flex-1 bg-white rounded-xl border border-gray-200 shadow-sm" />

        {selectedNode && (
          <div className="w-80 card shrink-0 overflow-auto">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-gray-900">节点详情</h3>
              <button onClick={() => setSelectedNode(null)} className="text-gray-400 hover:text-gray-600 text-lg">×</button>
            </div>
            <div className="space-y-3 text-sm">
              <div>
                <span className="text-gray-500 text-xs">名称</span>
                <div className="font-medium text-base">{selectedNode.label}</div>
              </div>
              <div>
                <span className="text-gray-500 text-xs">描述</span>
                <div className="text-gray-700 leading-relaxed">
                  {selectedNode.description || '暂无描述'}
                </div>
              </div>
              <div className="flex gap-4">
                <div>
                  <span className="text-gray-500 text-xs">类型</span>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="w-3 h-3 rounded-full" style={{ background: TYPE_COLORS[selectedNode.type] }} />
                    <span className="px-2 py-0.5 rounded-full text-xs" style={{ background: TYPE_COLORS[selectedNode.type] + '20', color: TYPE_COLORS[selectedNode.type] }}>
                      {selectedNode.type}
                    </span>
                  </div>
                </div>
                <div>
                  <span className="text-gray-500 text-xs">频次</span>
                  <div className="font-medium mt-1">{selectedNode.frequency}</div>
                </div>
              </div>
              <div>
                <span className="text-gray-500 text-xs">教材来源</span>
                <div className="text-gray-700">{selectedNode.textbook_name}</div>
              </div>
              <div>
                <span className="text-gray-500 text-xs">所属章节</span>
                <div className="text-gray-700">{selectedNode.chapter_title || '未知'}</div>
              </div>
              <div>
                <span className="text-gray-500 text-xs">关联关系</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {graph.edges.filter(e => e.source === selectedNode.id || e.target === selectedNode.id).map((e, i) => (
                    <span key={i} className="px-2 py-0.5 rounded-full text-xs" style={{ background: RELATION_COLORS[e.relation] + '20', color: RELATION_COLORS[e.relation] }}>
                      {RELATION_LABELS[e.relation] || e.relation}
                    </span>
                  ))}
                  {graph.edges.filter(e => e.source === selectedNode.id || e.target === selectedNode.id).length === 0 && (
                    <span className="text-gray-400 text-xs">暂无关系</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {graph.nodes.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center text-gray-400">
            <p className="text-lg">暂无知识图谱数据</p>
            <p className="text-sm mt-1">请先上传教材文件</p>
          </div>
        </div>
      )}
    </div>
  )
}
