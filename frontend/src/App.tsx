import { useEffect } from 'react'
import { Toaster } from 'react-hot-toast'
import Sidebar from './components/Sidebar'
import FileUploader from './components/FileUploader'
import KnowledgeGraphView from './components/KnowledgeGraph'
import QAPanel from './components/QAPanel'
import TeacherChat from './components/TeacherChat'
import ArenaPage from './components/ArenaPage'
import { useAppStore } from './stores/useAppStore'
import { textbookApi, knowledgeApi } from './services/api'

export default function App() {
  const { sidebarTab, setTextbooks, setGraph, setKnowledgePoints } = useAppStore()

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const tbs = await textbookApi.list()
      setTextbooks(tbs)
      const graph = await knowledgeApi.getGraph()
      setGraph(graph)
      const kps = await knowledgeApi.getPoints()
      setKnowledgePoints(kps)
    } catch {}
  }

  const renderContent = () => {
    switch (sidebarTab) {
      case 'textbook':
        return <FileUploader onUploaded={loadData} />
      case 'graph':
        return <KnowledgeGraphView />
      case 'qa':
        return <QAPanel />
      case 'teacher':
        return <TeacherChat />
      case 'arena':
        return <ArenaPage />
      default:
        return <FileUploader onUploaded={loadData} />
    }
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Toaster position="top-right" />
      <Sidebar />
      <main className="flex-1 overflow-auto bg-gray-50 p-6">
        <div className="max-w-6xl mx-auto h-full">
          {renderContent()}
        </div>
      </main>
    </div>
  )
}
