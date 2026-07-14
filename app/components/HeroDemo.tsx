'use client';

import { useState, useEffect, useRef } from 'react';

const CYCLE = 11000;

export default function HeroDemo() {
  const [phase, setPhase] = useState(0);
  // 0=用户消息 1=思考中 2=历史 3=偏差 4=大师 5=总结
  const timerRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    function run() {
      setPhase(0);
      schedule(1, 1300);
      schedule(2, 2600);
      schedule(3, 4000);
      schedule(4, 5400);
      schedule(5, 6800);
    }
    function schedule(p: number, ms: number) { timerRef.current = setTimeout(() => setPhase(p), ms); }
    run();
    const iv = setInterval(run, CYCLE);
    return () => { clearInterval(iv); if (timerRef.current) clearTimeout(timerRef.current); };
  }, []);

  return (
    <div className="w-[300px] h-[640px] bg-[#F5F2EC] rounded-[36px] overflow-hidden shadow-xl border-[3px] border-[#2C2C2C] relative select-none pointer-events-none"
         style={{ flexShrink: 0 }}>

      {/* 顶部假状态栏 + 对话标题 */}
      <div className="bg-[#F5F2EC] pt-3 pb-2 px-4 border-b border-[#E8E3DA]">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[10px] text-[#9E9E9E]">9:41</span>
          <div className="flex gap-1">
            <div className="w-3 h-3 rounded-full border border-[#2C2C2C]" />
            <div className="w-3 h-3 rounded-full border border-[#2C2C2C]" />
          </div>
        </div>
        <div className="flex items-center gap-2">
          {/* Agent 圆圈 */}
          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#C43A31] to-[#8B2117] flex items-center justify-center shadow-sm">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2"><circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/></svg>
          </div>
          <div>
            <div className="text-[12px] text-[#2C2C2C] font-medium leading-none">AI 助手</div>
            <div className="text-[9px] text-[#9E9E9E]">在线</div>
          </div>
        </div>
      </div>

      {/* 聊天区域 */}
      <div className="h-[calc(100%-72px)] overflow-hidden flex flex-col justify-end px-3 py-3 gap-2.5">

        {/* 用户消息 */}
        <div className={`self-end max-w-[80%] transition-all duration-500 ${phase >= 0 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'}`}>
          <div className="bg-[#C43A31] text-white text-[13px] px-3.5 py-2.5 rounded-2xl rounded-br-md leading-relaxed">
            茅台跌到 1400 了，要不要买？
          </div>
        </div>

        {/* AI 思考中 */}
        {phase >= 1 && phase < 5 && (
          <div className="flex items-start gap-2 self-start max-w-[85%]">
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-[#C43A31] to-[#8B2117] flex-shrink-0 flex items-center justify-center mt-1">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2"><circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/></svg>
            </div>
            <div className="bg-white border border-[#E8E3DA] rounded-2xl rounded-bl-md px-3 py-2.5">
              <div className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[#C43A31] animate-bounce" style={{animationDelay:'0ms'}} />
                <span className="w-1.5 h-1.5 rounded-full bg-[#C43A31] animate-bounce" style={{animationDelay:'150ms'}} />
                <span className="w-1.5 h-1.5 rounded-full bg-[#C43A31] animate-bounce" style={{animationDelay:'300ms'}} />
              </div>
            </div>
          </div>
        )}

        {/* AI: 历史 */}
        {phase >= 2 && (
          <div className="flex items-start gap-2 self-start max-w-[85%] transition-all duration-500 opacity-100 translate-y-0">
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-[#C43A31] to-[#8B2117] flex-shrink-0 flex items-center justify-center mt-1">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2"><circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/></svg>
            </div>
            <div className="bg-white border border-[#E8E3DA] rounded-2xl rounded-bl-md px-3 py-2.5 text-[11px] leading-relaxed">
              <p className="font-semibold text-[#2C2C2C] mb-1.5">📋 检索你的历史记忆</p>
              <span className="inline-block bg-[#FFF3E0] text-[#E65100] text-[9px] px-1.5 py-0.5 rounded-full font-semibold mb-1.5">⚠️ 上次追高亏损 8%</span>
              <p className="text-[#6B6B6B]">2025.11 茅台 1850 买入，3 天后跌至 1700（-8%），与当前情形有 2 个相似点。</p>
            </div>
          </div>
        )}

        {/* AI: 偏差 */}
        {phase >= 3 && (
          <div className="flex items-start gap-2 self-start max-w-[85%] transition-all duration-500 opacity-100 translate-y-0">
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-[#C43A31] to-[#8B2117] flex-shrink-0 flex items-center justify-center mt-1">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2"><circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/></svg>
            </div>
            <div className="bg-white border border-[#E8E3DA] rounded-2xl rounded-bl-md px-3 py-2.5 text-[11px] leading-relaxed">
              <p className="font-semibold text-[#C43A31] mb-1">🧠 检测到：锚定偏差</p>
              <p className="text-[#6B6B6B]">过度关注 1850 买入价，把 1400 当"便宜了 450"。价格低 ≠ 价值低。近 3 月偏差频率高于均值 40%。</p>
            </div>
          </div>
        )}

        {/* AI: 大师 */}
        {phase >= 4 && (
          <div className="flex items-start gap-2 self-start max-w-[85%] transition-all duration-500 opacity-100 translate-y-0">
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-[#C43A31] to-[#8B2117] flex-shrink-0 flex items-center justify-center mt-1">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2"><circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/></svg>
            </div>
            <div className="bg-white border border-[#E8E3DA] rounded-2xl rounded-bl-md px-3 py-2.5 text-[11px] leading-relaxed">
              <p className="font-semibold text-[#2C2C2C] mb-1.5">📖 匹配大师思想</p>
              <div className="border-l-2 border-[#B8860B] pl-2 mb-1">
                <span className="font-semibold">芒格：</span>
                <span className="text-[#6B6B6B] font-serif">"反过来想。如果茅台 2000 你会买吗？不会——那你只是在抄底。"</span>
              </div>
              <div className="border-l-2 border-[#B8860B] pl-2">
                <span className="font-semibold">巴菲特：</span>
                <span className="text-[#6B6B6B] font-serif">"价格是你支付的，价值是你得到的。"</span>
              </div>
            </div>
          </div>
        )}

        {/* AI: 总结 */}
        {phase >= 5 && (
          <div className="flex items-start gap-2 self-start max-w-[85%] transition-all duration-500 opacity-100 translate-y-0">
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-[#C43A31] to-[#8B2117] flex-shrink-0 flex items-center justify-center mt-1">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2"><circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/></svg>
            </div>
            <div className="bg-[#FFFDE7] border border-[#E8D88A] rounded-2xl rounded-bl-md px-3 py-2.5 text-[11px] leading-relaxed">
              <p className="font-semibold text-[#2C2C2C] mb-1">💡 建议</p>
              <p className="text-[#6B6B6B]">上次追高亏了 8%，这次又在锚定历史价。冷静 24 小时，按 checklist 重新评估，别凭感觉下手。</p>
            </div>
          </div>
        )}
      </div>

      {/* 进度点 */}
      <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-1.5">
        <div className={`w-1.5 h-1.5 rounded-full transition-colors ${phase <= 1 ? 'bg-[#C43A31]' : 'bg-[#D0CEC8]'}`} />
        <div className={`w-1.5 h-1.5 rounded-full transition-colors ${phase === 2 || phase === 3 ? 'bg-[#C43A31]' : 'bg-[#D0CEC8]'}`} />
        <div className={`w-1.5 h-1.5 rounded-full transition-colors ${phase >= 4 ? 'bg-[#C43A31]' : 'bg-[#D0CEC8]'}`} />
      </div>
    </div>
  );
}
