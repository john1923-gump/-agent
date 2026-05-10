import { useState, useRef } from 'react'
import { Upload, FileText, Trash2, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAppStore } from '../stores/useAppStore'
import { textbookApi, knowledgeApi } from '../services/api'

interface Props {
  onUploaded: () => void
}

export default function FileUploader({ onUploaded }: Props) {
  const { textbooks, setTextbooks } = useAppStore()
  const [uploading, setUploading] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleUpload = async (files: FileList | null) => {
    if (!files?.length) return
    setUploading(true)
    for (const file of Array.from(files)) {
      try {
        const result = await textbookApi.upload(file)
        toast.success(`${file.name} 上传成功，${result.chapters_count}个章节，${result.knowledge_points_count}个知识点`)
      } catch (e: any) {
        const detail = e.response?.data?.detail || e.message
        toast.error(`${file.name} 上传失败: ${detail}`)
      }
    }
    setUploading(false)
    onUploaded()
  }

  const handleDelete = async (id: string, name: string) => {
    try {
      await textbookApi.delete(id)
      setTextbooks(textbooks.filter(t => t.id !== id))
      toast.success(`已删除 ${name}`)
    } catch {
      toast.error('删除失败')
    }
  }

  const handleIntegrate = async () => {
    try {
      const { result } = await knowledgeApi.integrate()
      if (!result) {
        toast('知识点不足，无法整合')
        return
      }
      toast.success(`整合完成！压缩率 ${(result.compression_ratio * 100).toFixed(1)}%`)
    } catch {
      toast.error('整合失败')
    }
  }

  return (
    <div className="space-y-6 h-full">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">教材管理</h2>
          <p className="text-sm text-gray-500 mt-1">上传PDF/MD/TXT/DOCX教材，系统自动解析并构建知识图谱</p>
        </div>
        {textbooks.length >= 2 && (
          <button onClick={handleIntegrate} className="btn-primary flex items-center gap-2">
            <Sparkles className="w-4 h-4" />
            跨教材整合
          </button>
        )}
      </div>

      <div
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer
          ${dragOver ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400'}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={e => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={e => { e.preventDefault(); setDragOver(false); handleUpload(e.dataTransfer.files) }}
      >
        <input ref={inputRef} type="file" multiple accept=".pdf,.md,.txt,.docx" className="hidden"
          onChange={e => handleUpload(e.target.files)} />
        {uploading ? (
          <Loader2 className="w-10 h-10 text-primary-500 mx-auto animate-spin" />
        ) : (
          <Upload className="w-10 h-10 text-gray-400 mx-auto" />
        )}
        <p className="mt-3 text-sm text-gray-600">
          {uploading ? '正在上传并解析...' : '拖拽文件到此处或点击上传'}
        </p>
        <p className="text-xs text-gray-400 mt-1">支持 PDF / Markdown / TXT / DOCX</p>
      </div>

      <div className="space-y-3">
        {textbooks.map(tb => (
          <div key={tb.id} className="card flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileText className="w-8 h-8 text-primary-500" />
              <div>
                <div className="font-medium text-gray-900">{tb.filename}</div>
                <div className="text-xs text-gray-500">
                  {tb.format.toUpperCase()} · {tb.chapter_count} 章节
                </div>
              </div>
            </div>
            <button onClick={() => handleDelete(tb.id, tb.filename)}
              className="p-2 text-gray-400 hover:text-red-500 transition-colors">
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        ))}
        {textbooks.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>暂无教材，请上传文件开始</p>
          </div>
        )}
      </div>
    </div>
  )
}

function Sparkles(props: any) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
      <path d="M5 3v4" /><path d="M19 17v4" /><path d="M3 5h4" /><path d="M17 19h4" />
    </svg>
  )
}
