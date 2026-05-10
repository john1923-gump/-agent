import { create } from 'zustand'
import type { ArenaSession, ArenaQuestion, ArenaRound, ArenaOpponent } from '../types'

interface ArenaState {
  session: ArenaSession | null
  currentQuestion: ArenaQuestion | null
  opponents: ArenaOpponent[]
  currentRoundResult: ArenaRound | null
  isAnswering: boolean
  showResult: boolean
  setSession: (s: ArenaSession | null) => void
  setCurrentQuestion: (q: ArenaQuestion | null) => void
  setOpponents: (o: ArenaOpponent[]) => void
  setCurrentRoundResult: (r: ArenaRound | null) => void
  setIsAnswering: (v: boolean) => void
  setShowResult: (v: boolean) => void
  reset: () => void
}

export const useArenaStore = create<ArenaState>((set) => ({
  session: null,
  currentQuestion: null,
  opponents: [],
  currentRoundResult: null,
  isAnswering: false,
  showResult: false,
  setSession: (session) => set({ session }),
  setCurrentQuestion: (currentQuestion) => set({ currentQuestion }),
  setOpponents: (opponents) => set({ opponents }),
  setCurrentRoundResult: (currentRoundResult) => set({ currentRoundResult }),
  setIsAnswering: (isAnswering) => set({ isAnswering }),
  setShowResult: (showResult) => set({ showResult }),
  reset: () => set({
    session: null,
    currentQuestion: null,
    opponents: [],
    currentRoundResult: null,
    isAnswering: false,
    showResult: false,
  }),
}))
