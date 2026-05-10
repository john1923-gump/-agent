import { create } from 'zustand'
import type { TextbookMeta, KnowledgeGraph, ChatMessage, IntegrationResult, KnowledgePoint } from '../types'

interface AppState {
  textbooks: TextbookMeta[]
  graph: KnowledgeGraph
  knowledgePoints: KnowledgePoint[]
  integrationResult: IntegrationResult | null
  chatHistory: ChatMessage[]
  selectedTextbook: string | null
  sidebarTab: 'textbook' | 'graph' | 'qa' | 'teacher' | 'arena'

  setTextbooks: (t: TextbookMeta[]) => void
  addTextbook: (t: TextbookMeta) => void
  setGraph: (g: KnowledgeGraph) => void
  setKnowledgePoints: (kp: KnowledgePoint[]) => void
  setIntegrationResult: (r: IntegrationResult | null) => void
  addChatMessage: (m: ChatMessage) => void
  clearChat: () => void
  setSelectedTextbook: (id: string | null) => void
  setSidebarTab: (tab: AppState['sidebarTab']) => void
}

export const useAppStore = create<AppState>((set) => ({
  textbooks: [],
  graph: { nodes: [], edges: [] },
  knowledgePoints: [],
  integrationResult: null,
  chatHistory: [],
  selectedTextbook: null,
  sidebarTab: 'textbook',

  setTextbooks: (textbooks) => set({ textbooks }),
  addTextbook: (t) => set((s) => ({ textbooks: [...s.textbooks, t] })),
  setGraph: (graph) => set({ graph }),
  setKnowledgePoints: (knowledgePoints) => set({ knowledgePoints }),
  setIntegrationResult: (integrationResult) => set({ integrationResult }),
  addChatMessage: (m) => set((s) => ({ chatHistory: [...s.chatHistory, m] })),
  clearChat: () => set({ chatHistory: [] }),
  setSelectedTextbook: (selectedTextbook) => set({ selectedTextbook }),
  setSidebarTab: (sidebarTab) => set({ sidebarTab }),
}))
