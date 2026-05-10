import { useState } from 'react'
import { Swords, Trophy, Zap, Target, Crown, Flame, Shield, ChevronRight, Loader2, RotateCcw } from 'lucide-react'
import { arenaApi } from '../services/api'
import { useArenaStore } from '../stores/useArenaStore'
import type { ArenaQuestion, ArenaRound, ArenaOpponent } from '../types'
import toast from 'react-hot-toast'

const OPPONENT_PROFILES: Record<string, { emoji: string; color: string; bgColor: string; avatar?: string }> = {
  wishdel: { emoji: '⚔️', color: 'text-red-600', bgColor: 'bg-red-50', avatar: 'https://neeko-copilot.bytedance.net/api/text_to_image?prompt=anime%20girl%20with%20silver%20hair%20and%20orange%20eyes%20pointing%20finger%20at%20viewer%20with%20red%20headphones%20and%20mechanical%20parts%20cyberpunk%20style&image_size=square' },
  teresia: { emoji: '🗡️', color: 'text-purple-600', bgColor: 'bg-purple-50', avatar: 'https://neeko-copilot.bytedance.net/api/text_to_image?prompt=cute%20anime%20girl%20with%20pink%20hair%20and%20red%20eyes%20making%20heart%20hands%20with%20black%20horns%20chibi%20style&image_size=square' },
}

export default function ArenaPage() {
  const {
    session, setSession, currentQuestion, setCurrentQuestion,
    opponents, setOpponents, currentRoundResult, setCurrentRoundResult,
    isAnswering, setIsAnswering, showResult, setShowResult, reset,
  } = useArenaStore()

  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [starting, setStarting] = useState(false)
  const [initialized, setInitialized] = useState(false)

  const initArena = async () => {
    if (initialized) return
    setInitialized(true)
    try {
      const opps = await arenaApi.getOpponents()
      setOpponents(opps)
    } catch {
      toast.error('加载对手信息失败')
      setInitialized(false)
    }
  }

  const handleStart = async () => {
    setStarting(true)
    try {
      if (!initialized) await initArena()
      const { session: s, question: q } = await arenaApi.start('student')
      setSession(s)
      setCurrentQuestion(q)
      setSelectedAnswer(null)
      setCurrentRoundResult(null)
      setShowResult(false)
    } catch {
      toast.error('创建对局失败')
    }
    setStarting(false)
  }

  const handleAnswer = async () => {
    if (!selectedAnswer || !session || !currentQuestion || isAnswering) return
    setIsAnswering(true)
    try {
      const { round, session: updatedSession, next_question } = await arenaApi.answer(session.id, selectedAnswer)
      setCurrentRoundResult(round)
      setSession(updatedSession)
      setShowResult(true)
      if (next_question) {
        setTimeout(() => {
          setCurrentQuestion(next_question)
          setSelectedAnswer(null)
          setCurrentRoundResult(null)
          setShowResult(false)
        }, 4000)
      }
    } catch {
      toast.error('提交答案失败')
    }
    setIsAnswering(false)
  }

  const handleRestart = () => {
    reset()
    setSelectedAnswer(null)
    setInitialized(false)
    setShowResult(false)
  }

  if (!session) {
    return <ArenaLanding onStart={handleStart} loading={starting} opponents={opponents} onInit={initArena} initialized={initialized} />
  }

  if (session.finished) {
    return <ArenaResult session={session} opponents={opponents} onRestart={handleRestart} />
  }

  return (
    <div className="flex flex-col h-full gap-4">
      <ArenaHeader session={session} opponents={opponents} />

      <div className="flex-1 flex flex-col gap-4 min-h-0">
        {showResult && currentRoundResult ? (
          <RoundResultCard round={currentRoundResult} opponents={opponents} />
        ) : currentQuestion ? (
          <QuestionCard
            question={currentQuestion}
            selectedAnswer={selectedAnswer}
            onSelect={setSelectedAnswer}
            onSubmit={handleAnswer}
            isAnswering={isAnswering}
            roundNum={session.current_round + 1}
          />
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
          </div>
        )}
      </div>
    </div>
  )
}

function ArenaLanding({ onStart, loading, opponents, onInit, initialized }: {
  onStart: () => void; loading: boolean; opponents: ArenaOpponent[]; onInit: () => void; initialized: boolean
}) {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-8">
      <div className="text-center">
        <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center mx-auto mb-4 shadow-lg">
          <Swords className="w-10 h-10 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900">竞学堂</h1>
        <p className="text-gray-500 mt-2 max-w-md">
          基于RAG知识库出题，与两位AI对手展开8轮知识对决
        </p>
      </div>

      <div className="flex gap-6">
        {[
          { id: 'wishdel', name: '维什戴尔', desc: '自信张扬、争强好胜', style: '简洁犀利、喜欢用反问句和挑衅语气', avatar: 'https://neeko-copilot.bytedance.net/api/text_to_image?prompt=anime%20girl%20with%20silver%20hair%20and%20orange%20eyes%20pointing%20finger%20at%20viewer%20with%20red%20headphones%20and%20mechanical%20parts%20cyberpunk%20style&image_size=square', color: 'from-red-500 to-orange-500' },
          { id: 'teresia', name: '特雷西娅', desc: '沉稳冷静、理性分析', style: '温和但暗含讽刺、用优雅方式嘲笑对手', avatar: 'https://neeko-copilot.bytedance.net/api/text_to_image?prompt=cute%20anime%20girl%20with%20pink%20hair%20and%20red%20eyes%20making%20heart%20hands%20with%20black%20horns%20chibi%20style&image_size=square', color: 'from-purple-500 to-pink-500' },
        ].map(opp => (
          <div key={opp.id} className="card w-64 text-center hover:shadow-lg transition-shadow">
            <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${opp.color} flex items-center justify-center mx-auto mb-3 overflow-hidden`}>
              <img src={opp.avatar} alt={opp.name} className="w-full h-full object-cover" />
            </div>
            <h3 className="font-bold text-lg">{opp.name}</h3>
            <p className="text-sm text-gray-500 mt-1">{opp.desc}</p>
            <p className="text-xs text-gray-400 mt-2">{opp.style}</p>
          </div>
        ))}
      </div>

      <div className="flex gap-4 text-sm text-gray-500">
        <div className="flex items-center gap-1"><Target className="w-4 h-4" /> 8轮对决</div>
        <div className="flex items-center gap-1"><Zap className="w-4 h-4" /> RAG智能出题</div>
        <div className="flex items-center gap-1"><Flame className="w-4 h-4" /> 连胜加成</div>
        <div className="flex items-center gap-1"><Crown className="w-4 h-4" /> 积分排名</div>
      </div>

      <button onClick={onStart} disabled={loading} className="btn-primary px-10 py-3 text-lg">
        {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : '开始对战'}
      </button>
    </div>
  )
}

function ArenaHeader({ session, opponents }: { session: any; opponents: ArenaOpponent[] }) {
  const streak = session.streak
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Target className="w-5 h-5 text-indigo-600" />
            <span className="font-bold">第 {session.current_round + 1} / 8 轮</span>
          </div>
          <div className="h-4 w-32 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all"
              style={{ width: `${((session.current_round) / 8) * 100}%` }}
            />
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="flex items-center gap-1.5">
            <Trophy className="w-5 h-5 text-amber-500" />
            <span className="font-bold text-lg text-amber-600">{session.score}</span>
            <span className="text-xs text-gray-400">分</span>
          </div>
          {streak > 0 && (
            <div className="flex items-center gap-1.5 px-2 py-1 bg-orange-50 rounded-full">
              <Flame className="w-4 h-4 text-orange-500" />
              <span className="font-bold text-orange-600">{streak}</span>
              <span className="text-xs text-orange-400">连胜</span>
            </div>
          )}
          <div className="flex items-center gap-1.5 px-2 py-1 bg-gray-50 rounded-full">
            <Crown className="w-4 h-4 text-gray-500" />
            <span className="text-xs text-gray-500">最高连胜 {session.max_streak}</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4 mt-2">
        <span className="text-xs text-gray-400">对手：</span>
        {opponents.map(opp => {
          const profile = OPPONENT_PROFILES[opp.id] || { emoji: '🤖', color: 'text-gray-600', bgColor: 'bg-gray-50' }
          return (
            <span key={opp.id} className={`flex items-center gap-1 text-xs px-2 py-1 rounded-full ${profile.bgColor} ${profile.color}`}>
              {profile.avatar ? (
                <img src={profile.avatar} alt={opp.name} className="w-5 h-5 rounded-full object-cover" />
              ) : (
                <span>{profile.emoji}</span>
              )} {opp.name}
            </span>
          )
        })}
      </div>
    </div>
  )
}

function QuestionCard({ question, selectedAnswer, onSelect, onSubmit, isAnswering, roundNum }: {
  question: ArenaQuestion; selectedAnswer: string | null; onSelect: (a: string) => void
  onSubmit: () => void; isAnswering: boolean; roundNum: number
}) {
  const diffLabel = ['', '基础', '中等', '困难'][question.difficulty] || '基础'
  const diffColor = ['', 'text-green-600 bg-green-50', 'text-amber-600 bg-amber-50', 'text-red-600 bg-red-50'][question.difficulty] || ''

  return (
    <div className="card flex-1 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-gray-500">第{roundNum}题</span>
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${diffColor}`}>{diffLabel}</span>
          {question.knowledge_point_name && (
            <span className="text-xs text-gray-400">知识点: {question.knowledge_point_name}</span>
          )}
        </div>
      </div>

      <h3 className="text-lg font-bold text-gray-900 mb-6">{question.question}</h3>

      <div className="grid grid-cols-1 gap-3 flex-1">
        {question.options.map((opt, i) => {
          const letter = opt[0]
          const isSelected = selectedAnswer === letter
          return (
            <button
              key={i}
              onClick={() => onSelect(letter)}
              className={`flex items-center gap-3 p-4 rounded-xl border-2 text-left transition-all ${
                isSelected
                  ? 'border-indigo-500 bg-indigo-50 shadow-md'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }`}
            >
              <span className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shrink-0 ${
                isSelected ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600'
              }`}>
                {letter}
              </span>
              <span className="flex-1">{opt.slice(2)}</span>
            </button>
          )
        })}
      </div>

      <div className="mt-4 flex justify-end">
        <button
          onClick={onSubmit}
          disabled={!selectedAnswer || isAnswering}
          className="btn-primary px-8"
        >
          {isAnswering ? (
            <span className="flex items-center gap-2"><Loader2 className="w-4 h-4 animate-spin" /> 评判中...</span>
          ) : (
            <span className="flex items-center gap-2">提交答案 <ChevronRight className="w-4 h-4" /></span>
          )}
        </button>
      </div>
    </div>
  )
}

function RoundResultCard({ round, opponents }: { round: ArenaRound; opponents: ArenaOpponent[] }) {
  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-4">
        <span className={`text-2xl ${round.is_correct ? 'text-green-500' : 'text-red-500'}`}>
          {round.is_correct ? '✅' : '❌'}
        </span>
        <div>
          <span className={`font-bold text-lg ${round.is_correct ? 'text-green-600' : 'text-red-600'}`}>
            {round.is_correct ? '回答正确！' : '回答错误'}
          </span>
          <p className="text-sm text-gray-500">{round.feedback}</p>
        </div>
      </div>

      <div className="p-3 bg-gray-50 rounded-lg mb-4 text-sm">
        <div className="font-medium text-gray-700 mb-1">解析</div>
        <div className="text-gray-600">{round.question.explanation}</div>
        <div className="text-xs text-gray-400 mt-1">正确答案: {round.question.correct_answer}</div>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-4">
        {opponents.map(opp => {
          const profile = OPPONENT_PROFILES[opp.id] || { emoji: '🤖', color: 'text-gray-600', bgColor: 'bg-gray-50' }
          const answer = round.opponent_answers[opp.name]
          const comment = round.opponent_comments[opp.name]
          const isCorrect = answer && round.question.correct_answer && answer[0] === round.question.correct_answer[0]

          return (
            <div key={opp.id} className={`p-3 rounded-xl border ${profile.bgColor}`}>
              <div className="flex items-center gap-2 mb-2">
                {profile.avatar ? (
                  <img src={profile.avatar} alt={opp.name} className="w-8 h-8 rounded-full object-cover" />
                ) : (
                  <span className="text-lg">{profile.emoji}</span>
                )}
                <span className={`font-medium ${profile.color}`}>{opp.name}</span>
                <span className="text-xs ml-auto">{answer || '未作答'}</span>
                {isCorrect !== undefined && (
                  <span className={isCorrect ? 'text-green-500' : 'text-red-500'}>
                    {isCorrect ? '✓' : '✗'}
                  </span>
                )}
              </div>
              {comment && (
                <p className="text-xs text-gray-600 italic border-t border-gray-200 pt-2 mt-2">
                  "{comment}"
                </p>
              )}
            </div>
          )
        })}
      </div>

      <div className="text-center text-sm text-gray-400">
        {round.round_num < 8 ? '下一轮即将开始...' : '对局结束！'}
      </div>
    </div>
  )
}

function ArenaResult({ session, opponents, onRestart }: { session: any; opponents: ArenaOpponent[]; onRestart: () => void }) {
  const correctCount = session.rounds.filter((r: ArenaRound) => r.is_correct).length
  const totalRounds = session.rounds.length

  let rank = '新手学者'
  if (session.score >= 150) rank = '知识大师'
  else if (session.score >= 100) rank = '学霸'
  else if (session.score >= 60) rank = '进步学员'

  const opponentScores: Record<string, number> = {}
  for (const opp of opponents) {
    let score = 0
    for (const round of session.rounds) {
      const answer = round.opponent_answers[opp.name]
      if (answer && round.question.correct_answer && answer[0] === round.question.correct_answer[0]) {
        score += 10 * round.question.difficulty
      }
    }
    opponentScores[opp.name] = score
  }

  const rankings = [
    { name: '你', score: session.score, isUser: true, id: 'user' },
    ...opponents.map((opp: ArenaOpponent) => ({
      name: opp.name, score: opponentScores[opp.name] || 0, isUser: false, id: opp.id,
    })),
  ].sort((a, b) => b.score - a.score)

  return (
    <div className="flex flex-col items-center justify-center h-full gap-6">
      <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shadow-lg">
        <Trophy className="w-10 h-10 text-white" />
      </div>

      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900">对局结束</h2>
        <p className="text-lg text-indigo-600 font-medium mt-1">{rank}</p>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="card text-center">
          <div className="text-2xl font-bold text-amber-600">{session.score}</div>
          <div className="text-xs text-gray-500">总积分</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-green-600">{correctCount}/{totalRounds}</div>
          <div className="text-xs text-gray-500">正确率</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-orange-600">{session.max_streak}</div>
          <div className="text-xs text-gray-500">最高连胜</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-purple-600">{session.weak_points.length}</div>
          <div className="text-xs text-gray-500">薄弱点</div>
        </div>
      </div>

      <div className="card w-full max-w-md">
        <h3 className="font-bold mb-3 flex items-center gap-2">
          <Crown className="w-4 h-4 text-amber-500" /> 最终排名
        </h3>
        <div className="space-y-2">
          {rankings.map((r, i) => {
            const medal = ['🥇', '🥈', '🥉'][i]
            const profile = r.id === 'user' ? null : OPPONENT_PROFILES[r.id]
            return (
              <div key={r.id} className={`flex items-center gap-3 p-3 rounded-lg ${r.isUser ? 'bg-indigo-50 border border-indigo-200' : 'bg-gray-50'}`}>
                <span className="text-xl w-8 text-center">{medal || `${i + 1}`}</span>
                {profile && (profile.avatar ? (
                  <img src={profile.avatar} alt={r.name} className="w-8 h-8 rounded-full object-cover" />
                ) : (
                  <span className="text-lg">{profile.emoji}</span>
                ))}
                <span className={`font-medium flex-1 ${r.isUser ? 'text-indigo-700' : ''}`}>{r.name}</span>
                <span className="font-bold text-lg">{r.score}</span>
              </div>
            )
          })}
        </div>
      </div>

      {session.weak_points.length > 0 && (
        <div className="card w-full max-w-md">
          <h3 className="font-bold mb-2 flex items-center gap-2">
            <Shield className="w-4 h-4 text-amber-500" /> 薄弱知识点
          </h3>
          <div className="flex flex-wrap gap-2">
            {[...new Set(session.weak_points)].map((p: any, i: number) => (
              <span key={i} className="px-2 py-1 bg-amber-50 text-amber-700 rounded-full text-xs">{p}</span>
            ))}
          </div>
        </div>
      )}

      <button onClick={onRestart} className="btn-primary px-8 flex items-center gap-2">
        <RotateCcw className="w-4 h-4" /> 再来一局
      </button>
    </div>
  )
}
