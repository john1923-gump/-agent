export interface TextbookMeta {
  id: string
  filename: string
  format: string
  chapter_count: number
  upload_time: string
}

export interface Chapter {
  id: string
  textbook_id: string
  textbook_name: string
  title: string
  content: string
  page_start: number
  page_end: number
}

export type KnowledgeType = '概念' | '定理' | '方法' | '现象'

export interface KnowledgePoint {
  id: string
  chapter_id: string
  textbook_id: string
  textbook_name: string
  chapter_title: string
  name: string
  description: string
  type: KnowledgeType
  page: number
}

export interface GraphNode {
  id: string
  label: string
  type: KnowledgeType
  textbook_id: string
  textbook_name: string
  chapter_title: string
  description: string
  frequency: number
  size: number
}

export interface GraphEdge {
  source: string
  target: string
  relation: string
  weight: number
}

export interface KnowledgeGraph {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export interface QAReference {
  textbook_name: string
  chapter_title: string
  page: number
  snippet: string
}

export interface QAResponse {
  answer: string
  references: QAReference[]
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface IntegrationPair {
  kp_a: KnowledgePoint
  kp_b: KnowledgePoint
  similarity: number
  decision: 'merge' | 'keep' | 'remove'
  reason: string
  merged_content?: string
}

export interface IntegrationResult {
  pairs: IntegrationPair[]
  compression_ratio: number
  original_count: number
  final_count: number
  original_text_chars: number
  final_text_chars: number
  merge_count: number
  keep_count: number
  remove_count: number
  integrity_report: {
    status: string
    total_preserved: number
    broken_dependencies: string[]
  }
  coverage_report: Record<string, { original: number; preserved: number; rate: number }>
}

export interface ArenaOpponent {
  id: string
  name: string
  personality: string
  style: string
}

export interface ArenaQuestion {
  id: string
  question: string
  options: string[]
  correct_answer: string
  explanation: string
  knowledge_point_id: string
  knowledge_point_name: string
  difficulty: number
}

export interface ArenaRound {
  round_num: number
  question: ArenaQuestion
  opponent_answers: Record<string, string>
  user_answer: string
  is_correct: boolean
  feedback: string
  opponent_comments: Record<string, string>
}

export interface ArenaSession {
  id: string
  mode: string
  rounds: ArenaRound[]
  current_round: number
  score: number
  streak: number
  max_streak: number
  weak_points: string[]
  finished: boolean
}
