export function CombatArena() {
  return (
    <div className="rounded-3xl border border-slate-700 bg-slate-900 p-6 shadow-lg shadow-slate-950/40">
      <h2 className="text-xl font-semibold text-white">竞学堂对抗学习</h2>
      <p className="mt-3 text-slate-400">学生模式与虚拟对手将在后续实现中进行进阶对话、出题与评判。</p>
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl bg-slate-950 p-4">
          <h3 className="text-lg text-white">虚拟对手</h3>
          <p className="mt-2 text-slate-400">林锐 / 苏瑶：固定人格、说话风格与嘲讽强度。</p>
        </div>
        <div className="rounded-2xl bg-slate-950 p-4">
          <h3 className="text-lg text-white">积分与连胜</h3>
          <p className="mt-2 text-slate-400">系统将基于 RAG 答案与知识点映射计算奖励。</p>
        </div>
      </div>
    </div>
  )
}
