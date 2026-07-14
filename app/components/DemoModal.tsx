'use client';

import { useState, useEffect, useRef } from 'react';

export default function DemoModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [screen, setScreen] = useState(1);
  const [step1, setStep1] = useState(false);
  const [step2, setStep2] = useState(false);
  const [step3, setStep3] = useState(false);
  const [step3Done, setStep3Done] = useState(false);
  const [ctaClicked, setCtaClicked] = useState(false);
  const timersRef = useRef<ReturnType<typeof setTimeout>[]>([]);

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    if (open) document.addEventListener('keydown', handleEsc);
    return () => document.removeEventListener('keydown', handleEsc);
  }, [open, onClose]);

  // Reset state when modal opens
  useEffect(() => {
    if (open) {
      setScreen(1);
      setStep1(false); setStep2(false); setStep3(false); setStep3Done(false);
      setCtaClicked(false);
    }
  }, [open]);

  // Auto-play animation when screen 2 activates
  useEffect(() => {
    if (screen !== 2) return;
    timersRef.current.forEach(clearTimeout);
    timersRef.current = [
      setTimeout(() => setStep1(true), 400),
      setTimeout(() => setStep2(true), 1400),
      setTimeout(() => {
        setStep3(true);
        timersRef.current.push(setTimeout(() => setStep3Done(true), 800));
        timersRef.current.push(setTimeout(() => setScreen(3), 2000));
      }, 2400),
    ];
    return () => timersRef.current.forEach(clearTimeout);
  }, [screen]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
         onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      {/* Close button */}
      <button onClick={onClose}
        className="absolute top-6 right-6 text-white/60 hover:text-white text-3xl leading-none w-10 h-10 flex items-center justify-center rounded-full hover:bg-white/10 transition-colors z-10"
        aria-label="关闭演示">
        ×
      </button>

      {/* Phone frame */}
      <div className="relative w-[390px] h-[844px] max-w-[90vw] max-h-[90vh] bg-[#FAF7F2] rounded-[40px] overflow-hidden shadow-2xl"
           style={{ transform: 'scale(min(1, calc(90vw / 390), calc(90vh / 844)))', transformOrigin: 'center center' }}>

        {/* ====== Screen 1: Input ====== */}
        {screen === 1 && (
          <div className="absolute inset-0 flex flex-col px-7 pt-12 pb-9 animate-[fadeIn_0.4s_ease]">
            <div className="mb-10">
              <h1 className="font-serif text-[26px] text-[#C43A31] font-bold tracking-wide">InvestBrain</h1>
              <p className="text-sm text-[#6B6B6B] mt-2 leading-relaxed font-serif">
                不是替你做决定，<br />是帮你做更好的决定
              </p>
            </div>
            <div className="flex-1 flex flex-col justify-center">
              <p className="text-[13px] text-[#6B6B6B] mb-3 font-medium">你在想什么？</p>
              <textarea
                readOnly
                value="茅台跌到 1400 了，要不要买？"
                className="w-full h-[120px] border-2 border-[#E8E3DA] rounded-2xl bg-white p-4 text-base text-[#2C2C2C] resize-none outline-none leading-relaxed"
              />
              <button
                onClick={() => setScreen(2)}
                className="w-full h-[52px] bg-[#C43A31] text-white rounded-[14px] text-base font-semibold mt-5 hover:bg-[#D95A51] transition-colors active:scale-[0.97]">
                记录这个想法
              </button>
            </div>
          </div>
        )}

        {/* ====== Screen 2: Analyzing ====== */}
        {screen === 2 && (
          <div className="absolute inset-0 flex flex-col px-7 pt-12 pb-9 animate-[fadeIn_0.4s_ease]">
            <div className="text-center mb-12">
              <div className="w-10 h-10 border-[3px] border-[#E8E3DA] border-t-[#C43A31] rounded-full animate-spin mx-auto mb-4" />
              <p className="text-base text-[#2C2C2C] font-medium font-serif">正在分析...</p>
            </div>
            <div className="flex flex-col gap-4">
              <Step visible={step1} check="✓" color="text-[#2D8A56]" label="检索历史行为记忆..." detail="找到 3 条相关记录" />
              <Step visible={step2} check="✓" color="text-[#2D8A56]" label="检测行为偏差模式..." detail="匹配到「锚定偏差」" />
              <Step visible={step3} check={step3Done ? '✓' : '◌'} color={step3Done ? 'text-[#2D8A56]' : 'text-[#B8860B]'}
                label="匹配大师思想..." detail={step3Done ? '已匹配芒格/巴菲特相关观点' : '正在检索芒格/巴菲特观点'} />
            </div>
          </div>
        )}

        {/* ====== Screen 3: Results ====== */}
        {screen === 3 && (
          <div className="absolute inset-0 flex flex-col px-5 pt-8 pb-7 overflow-y-auto animate-[fadeIn_0.4s_ease]">
            <p className="font-serif text-xl text-[#2C2C2C] font-bold">茅台 · 当前价 1400</p>
            <p className="text-sm text-[#C43A31] font-semibold mb-6">分析结果</p>

            <div className="flex flex-col gap-[14px] mb-5">
              {/* Card 1: History */}
              <div className="bg-white border border-[#E8E3DA] rounded-2xl p-[18px] animate-[slideUp_0.5s_ease_backwards_0.1s]">
                <div className="flex items-center gap-2 mb-3 font-serif text-[15px] font-semibold text-[#2C2C2C]">
                  <span className="text-lg">📋</span> 你的历史
                </div>
                <span className="inline-block bg-[#FFF3E0] text-[#E65100] text-xs px-[10px] py-[3px] rounded-full font-semibold mb-[10px]">
                  ⚠️ 你上次在追高中亏损了 8%
                </span>
                <div className="text-[13px] text-[#6B6B6B] leading-relaxed border-l-[3px] border-[#B8860B] pl-3 my-2">
                  · 2025.11 茅台 1850 买入<br />
                  · 3天后跌至 1700（-8%）<br />
                  · 触发原因：大盘杀跌
                </div>
                <div className="text-[13px] bg-[#FFFDE7] rounded-[10px] p-[10px_12px] mt-[10px] leading-relaxed text-[#2C2C2C]">
                  <span className="text-xs text-[#B8860B] font-semibold">🟡 这次和上次有 2 个相似点：</span><br />
                  · 都是从高点回落<br />
                  · 都是大盘下跌中<br /><br />
                  <strong>上次的结果：亏损 8%</strong>
                </div>
              </div>

              {/* Card 2: Pattern */}
              <div className="bg-white border border-[#E8E3DA] rounded-2xl p-[18px] animate-[slideUp_0.5s_ease_backwards_0.25s]">
                <div className="flex items-center gap-2 mb-3 font-serif text-[15px] font-semibold text-[#C43A31]">
                  <span className="text-lg">🧠</span> 你的行为模式
                </div>
                <span className="inline-block bg-[#FDEAEA] text-[#C43A31] text-xs px-[10px] py-[3px] rounded-full font-semibold mb-[10px]">
                  🔴 锚定偏差
                </span>
                <p className="text-[13px] text-[#2C2C2C] leading-relaxed font-serif">
                  "你过度关注 1850 的买入价，现在 1400 看起来像'便宜了 450 块'。但价格低 ≠ 价值低。问问自己：如果不知道 1850 这个数字，1400 值不值得买？"
                </p>
                <p className="text-xs text-[#C43A31] mt-[10px] font-medium">
                  最近 3 个月锚定偏差出现频率：高于平均 40%
                </p>
              </div>

              {/* Card 3: Masters */}
              <div className="bg-white border border-[#E8E3DA] rounded-2xl p-[18px] animate-[slideUp_0.5s_ease_backwards_0.4s]">
                <div className="flex items-center gap-2 mb-3 font-serif text-[15px] font-semibold text-[#2C2C2C]">
                  <span className="text-lg">📖</span> 大师怎么说
                </div>
                <div className="mb-[14px]">
                  <p className="text-[13px] font-semibold text-[#2C2C2C] mb-1">芒格：</p>
                  <p className="text-[13px] text-[#6B6B6B] leading-relaxed font-serif border-l-[3px] border-[#E8E3DA] pl-3">
                    "反过来想。如果现在茅台不是 1400 而是 2000，你会买吗？如果不会——那你现在只是在'抄底'，不是在判断价值。"
                  </p>
                </div>
                <div>
                  <p className="text-[13px] font-semibold text-[#2C2C2C] mb-1">巴菲特：</p>
                  <p className="text-[13px] text-[#6B6B6B] leading-relaxed font-serif border-l-[3px] border-[#E8E3DA] pl-3">
                    "价格是你支付的，价值是你得到的。先算价值，再看价格。"
                  </p>
                </div>
              </div>
            </div>

            <button
              onClick={() => setCtaClicked(true)}
              className={`w-full h-[52px] rounded-[14px] text-base font-semibold border-2 transition-all ${
                ctaClicked
                  ? 'bg-[#E8F5E9] text-[#2D8A56] border-[#2D8A56]'
                  : 'bg-[#F5F0E8] text-[#C43A31] border-[#C43A31] hover:bg-[#FDEAEA] active:scale-[0.97]'
              }`}
              disabled={ctaClicked}>
              {ctaClicked ? '已记录 ✓' : '我先冷静一下'}
            </button>
            <button onClick={() => {
              setScreen(1); setStep1(false); setStep2(false); setStep3(false); setStep3Done(false); setCtaClicked(false);
            }} className="block text-center mt-[14px] text-xs text-[#B0B0B0] underline cursor-pointer">
              重新演示
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function Step({ visible, check, color, label, detail }: {
  visible: boolean; check: string; color: string; label: string; detail: string;
}) {
  return (
    <div className={`bg-white border border-[#E8E3DA] rounded-[14px] p-4 transition-all duration-400 ${
      visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-[10px]'
    }`}>
      <div className="flex items-center gap-2 text-sm font-medium text-[#2C2C2C] mb-1">
        <span className={`font-bold ${color}`}>{check}</span> {label}
      </div>
      <div className="text-xs text-[#6B6B6B] pl-6">{detail}</div>
    </div>
  );
}
