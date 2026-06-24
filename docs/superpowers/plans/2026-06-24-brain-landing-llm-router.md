# Brain-Landing + 通用LLM路由 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 invest-brain 项目添加通用 LLM 路由（支持 DeepSeek/OpenAI/Claude/自定义）+ Next.js 落地页

**Architecture:** 
- LLM 路由层：重构 `src/mcp_server/llm/deepseek_client.py` → 通用 `llm_router.py`，支持 OpenAI-compatible API
- 前端：新建 `frontend/` Next.js 项目，复用 `brain-landing-preview.html` 设计稿
- 配置：用户配置 Provider/API Key/Base URL，场景模型预设可覆盖

**Tech Stack:** Next.js 14 App Router, Tailwind CSS, OpenAI-compatible API, Python FastMCP

---

## 文件结构

```
investbrain/
├── frontend/                          # 新建 Next.js 前端
│   ├── app/
│   │   ├── page.tsx                 # 落地页
│   │   ├── layout.tsx
│   │   ├── globals.css
│   │   └── settings/                # 配置页面
│   │       └── page.tsx
│   ├── components/
│   │   └── ui/                      # 基础组件
│   ├── lib/
│   │   └── api.ts                  # API 客户端
│   ├── package.json
│   ├── next.config.js
│   └── tailwind.config.ts
├── src/mcp_server/
│   ├── llm/
│   │   ├── llm_router.py            # 新建：通用LLM路由（保留deepseek_client.py）
│   │   └── deepseek_client.py       # 重命名保留，内部委托给llm_router
│   └── server.py                    # 修改：切换到llm_router
└── brain-landing-preview.html        # 已有：参考设计稿
```

---

## Task 1: 通用LLM路由核心

**Files:**
- Create: `src/mcp_server/llm/llm_router.py`
- Create: `src/mcp_server/llm/providers.py`
- Modify: `src/mcp_server/llm/deepseek_client.py` (改为委托)
- Test: `tests/llm/test_router.py`

- [ ] **Step 1: 创建 providers.py - Provider定义**

```python
"""LLM Provider 配置"""
from dataclasses import dataclass
from typing import Literal, Optional

@dataclass
class ProviderConfig:
    name: str
    api_key: str
    base_url: str
    default_model: str
    supports_thinking: bool = False

PROVIDER_PRESETS = {
    "deepseek": ProviderConfig(
        name="DeepSeek",
        api_key="",
        base_url="https://api.deepseek.com",
        default_model="deepseek-v4-flash",
        supports_thinking=True,
    ),
    "openai": ProviderConfig(
        name="OpenAI",
        api_key="",
        base_url="https://api.openai.com/v1",
        default_model="gpt-4o",
        supports_thinking=False,
    ),
    "anthropic": ProviderConfig(
        name="Claude",
        api_key="",
        base_url="https://api.anthropic.com/v1",
        default_model="claude-sonnet-4-20250514",
        supports_thinking=False,
    ),
    "custom": ProviderConfig(
        name="Custom",
        api_key="",
        base_url="",
        default_model="",
        supports_thinking=False,
    ),
}

SceneModelPreset = dict[str, dict[str, str]]  # provider -> {model, thinking_model}

DEFAULT_SCENE_MODELS: SceneModelPreset = {
    "deepseek": {
        "thought_parsing": "deepseek-v4-flash",
        "rag_synthesis": "deepseek-v4-flash",
        "pattern_analysis": "deepseek-v4-pro",
        "roundtable_role": "deepseek-v4-flash",
        "roundtable_judge": "deepseek-v4-pro",
    },
    "openai": {
        "thought_parsing": "gpt-4o-mini",
        "rag_synthesis": "gpt-4o-mini",
        "pattern_analysis": "gpt-4o",
        "roundtable_role": "gpt-4o-mini",
        "roundtable_judge": "gpt-4o",
    },
    "anthropic": {
        "thought_parsing": "claude-sonnet-4-20250514",
        "rag_synthesis": "claude-sonnet-4-20250514",
        "pattern_analysis": "claude-opus-4-20250514",
        "roundtable_role": "claude-sonnet-4-20250514",
        "roundtable_judge": "claude-opus-4-20250514",
    },
}
```

- [ ] **Step 2: 创建 llm_router.py - 核心路由**

```python
"""通用LLM路由 - 支持OpenAI-compatible API"""
import os
import json
from typing import Optional, Literal
from pathlib import Path

try:
    import openai
except ImportError:
    openai = None

from .providers import ProviderConfig, PROVIDER_PRESETS, DEFAULT_SCENE_MODELS, SceneModelPreset

LLM_CONFIG_FILE = Path(__file__).parent.parent.parent.parent / "data" / "config" / "llm.json"

@dataclass
class LLMTask:
    """LLM任务定义"""
    scene: str
    system: Optional[str] = None
    temperature: float = 0.5
    thinking: bool = False
    json_mode: bool = False

class LLMRouter:
    """通用LLM路由器"""
    
    def __init__(self, config_file: Path = LLM_CONFIG_FILE):
        self.config_file = config_file
        self._config: Optional[dict] = None
        self._client = None
        self._load_config()
    
    def _load_config(self):
        """从文件加载配置"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                self._config = json.load(f)
        else:
            self._config = {"provider": "deepseek", "scenes": {}}
    
    def _save_config(self):
        """保存配置到文件"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(self._config, f, indent=2)
    
    def configure(self, provider: str, api_key: str, base_url: str = None, custom_model: str = None):
        """配置Provider"""
        self._config["provider"] = provider
        self._config["api_key"] = api_key
        if base_url:
            self._config["base_url"] = base_url
        if custom_model:
            self._config["custom_model"] = custom_model
        self._save_config()
        self._client = None  # 重置客户端
    
    def set_scene_model(self, scene: str, model: str):
        """设置场景模型"""
        if "scenes" not in self._config:
            self._config["scenes"] = {}
        self._config["scenes"][scene] = model
        self._save_config()
    
    def _get_client(self):
        """获取/创建OpenAI兼容客户端"""
        if self._client:
            return self._client
        
        provider = self._config.get("provider", "deepseek")
        api_key = self._config.get("api_key") or os.environ.get(f"{provider.upper()}_API_KEY")
        base_url = self._config.get("base_url") or PROVIDER_PRESETS.get(provider, PROVIDER_PRESETS["deepseek"]).base_url
        
        if not api_key:
            raise ValueError(f"API key not set for {provider}")
        
        self._client = openai.OpenAI(api_key=api_key, base_url=base_url)
        return self._client
    
    def chat(self, messages: list[dict], scene: str) -> str:
        """发送对话请求"""
        client = self._get_client()
        provider = self._config.get("provider", "deepseek")
        
        # 获取模型
        scene_models = DEFAULT_SCENE_MODELS.get(provider, DEFAULT_SCENE_MODELS["deepseek"])
        model = self._config.get("scenes", {}).get(scene) or scene_models.get(scene) or scene_models["rag_synthesis"]
        
        # 构建参数
        kwargs = {"model": model, "temperature": 0.5}
        
        if provider == "deepseek" and scene == "pattern_analysis":
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": 8192}
        
        kwargs["messages"] = messages
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    def chat_simple(self, prompt: str, scene: str) -> str:
        """简易接口"""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, scene)


# 单例
_router: Optional[LLMRouter] = None

def get_router() -> LLMRouter:
    global _router
    if _router is None:
        _router = LLMRouter()
    return _router
```

- [ ] **Step 3: 验证配置文件创建**

Run: `python -c "from src.mcp_server.llm.llm_router import get_router; r = get_router(); print('OK')"`
Expected: OK (创建空配置)

- [ ] **Step 4: Commit**

```bash
git add src/mcp_server/llm/providers.py src/mcp_server/llm/llm_router.py
git commit -m "feat: add generic LLM router with multi-provider support"
```

---

## Task 2: Next.js 项目初始化

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/next.config.js`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tailwind.config.ts`
- Create: `frontend/app/layout.tsx`
- Create: `frontend/app/page.tsx`
- Create: `frontend/app/globals.css`

- [ ] **Step 1: 创建 package.json**

```json
{
  "name": "investbrain-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "^14.2.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.4.0"
  }
}
```

- [ ] **Step 2: 创建基础配置文件**

```js
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
}
module.exports = nextConfig
```

```json
// tsconfig.json
{
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{"name": "next"}],
    "paths": {"@/*": ["./*"]}
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

- [ ] **Step 3: 创建 Tailwind + PostCSS 配置**

```js
// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./app/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        paper: '#FAF7F2',
        'paper-warm': '#F5F0E8',
        ink: '#2C2C2C',
        'ink-light': '#6B6B6B',
        'ink-faint': '#B8B2A6',
        vermillion: '#C43A31',
        'vermillion-light': '#E8A090',
      },
      fontFamily: {
        serif: ['Noto Serif SC', 'serif'],
        sans: ['Noto Sans SC', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
export default config
```

```js
// postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

- [ ] **Step 4: 创建 app/globals.css**

```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=Noto+Sans+SC:wght@300;400;500&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --paper: #FAF7F2;
  --paper-warm: #F5F0E8;
  --ink: #2C2C2C;
  --ink-light: #6B6B6B;
  --ink-faint: #B8B2A6;
  --vermillion: #C43A31;
  --vermillion-light: #E8A090;
  --border: #E8E3D8;
}

body {
  font-family: 'Noto Sans SC', sans-serif;
  background: var(--paper);
  color: var(--ink);
}
```

- [ ] **Step 5: 创建 app/layout.tsx**

```tsx
import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'InvestBrain — 投资第二大脑',
  description: '有经验投资者的纪律自主工具',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  )
}
```

- [ ] **Step 6: 创建简化版 app/page.tsx**

```tsx
export default function Home() {
  return (
    <main className="min-h-screen">
      {/* Hero - 简化版 */}
      <section className="hero text-center py-20 px-6">
        <h1 className="font-serif text-5xl font-bold mb-6">
          投资锚 · 三件事
        </h1>
        <p className="text-ink-light text-lg max-w-xl mx-auto">
          锚定你的投资纪律，让规则替你决策，而非情绪
        </p>
        <div className="mt-10 flex gap-4 justify-center">
          <a href="/chat" className="px-6 py-3 bg-ink text-paper rounded-full">
            开始使用
          </a>
          <a href="/settings" className="px-6 py-3 border border-ink rounded-full">
            配置LLM
          </a>
        </div>
      </section>
    </main>
  )
}
```

- [ ] **Step 7: 验证Next.js构建**

Run: `cd frontend && npm install && npm run build`
Expected: BUILD SUCCESSFUL

- [ ] **Step 8: Commit**

```bash
git add frontend/
git commit -m "feat: add Next.js frontend skeleton"
```

---

## Task 3: 落地页开发

**Files:**
- Modify: `frontend/app/page.tsx` (完整实现)

- [ ] **Step 1: 实现Hero + 问题 + 锚点三件事Section**

见 `brain-landing-preview.html` 第620-700行，转换为TSX

```tsx
export default function Home() {
  return (
    <main className="min-h-screen">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 px-16 py-6 flex justify-between items-center bg-gradient-to-b from-paper/95 to-transparent backdrop-blur-sm z-50">
        <span className="font-serif text-2xl font-bold">Brain</span>
        <div className="flex gap-8 text-sm">
          <a href="#problem" className="text-ink-light hover:text-ink">问题</a>
          <a href="#solution" className="text-ink-light hover:text-ink">方案</a>
          <a href="/settings" className="text-ink-light hover:text-ink">配置</a>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-20 px-6 text-center">
        <h1 className="font-serif text-6xl font-black mb-6 tracking-tight">
          投资锚 · 三件事
        </h1>
        <p className="text-ink-light text-xl max-w-2xl mx-auto leading-relaxed">
          锚定你的投资纪律，让规则替你决策，而非情绪
        </p>
      </section>

      {/* 问题 */}
      <section id="problem" className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <p className="text-vermillion text-sm font-medium mb-4">问题</p>
          <h2 className="font-serif text-4xl font-bold mb-6">每天市场都在喊你</h2>
          <p className="text-ink-light text-lg leading-relaxed">
            涨停、利好、放水、恐慌、FOMO——信息像潮水一样涌来，但真正重要的是什么？
          </p>
        </div>
      </section>

      {/* 锚点三件事 */}
      <div id="solution" className="anchor-section py-20 px-6 bg-paper-warm">
        <div className="max-w-4xl mx-auto">
          <p className="text-vermillion text-sm font-medium mb-4">解决方案</p>
          <h2 className="font-serif text-4xl font-bold mb-6">投资锚 · 三件事</h2>
          <p className="text-ink-light text-lg mb-12">锚定你的投资纪律，让规则替你决策，而非情绪。</p>
          
          <div className="grid grid-cols-3 gap-8">
            {/* 锚1-3 */}
          </div>
        </div>
      </div>

      {/* CTA */}
      <section className="py-20 px-6 text-center">
        <h2 className="font-serif text-3xl font-bold mb-4">准备好锚定了吗？</h2>
        <p className="text-ink-light mb-8">配置你的LLM提供商，开始使用</p>
        <a href="/settings" className="inline-block px-8 py-4 bg-ink text-paper text-lg rounded-full">
          立即配置
        </a>
      </section>
    </main>
  )
}
```

- [ ] **Step 2: 验证页面渲染**

Run: `cd frontend && npm run dev`
Expected: 页面无错误，可访问 localhost:3000

- [ ] **Step 3: Commit**

```bash
git add frontend/app/page.tsx
git commit -m "feat: implement landing page with hero, problem, and solution sections"
```

---

## Task 4: LLM配置页面

**Files:**
- Create: `frontend/app/settings/page.tsx`
- Create: `frontend/lib/api.ts`
- Create: `src/mcp_server/llm/routes.py` (新增API端点)

- [ ] **Step 1: 创建 lib/api.ts**

```ts
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'

export async function getLLMConfig() {
  const res = await fetch(`${API_BASE}/api/llm/config`)
  return res.json()
}

export async function saveLLMConfig(config: {
  provider: string
  api_key: string
  base_url?: string
}) {
  const res = await fetch(`${API_BASE}/api/llm/config`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(config),
  })
  return res.json()
}
```

- [ ] **Step 2: 创建 settings/page.tsx**

```tsx
'use client'

import { useState } from 'react'
import { saveLLMConfig } from '@/lib/api'

const PROVIDERS = [
  { id: 'deepseek', name: 'DeepSeek', models: ['deepseek-v4-flash', 'deepseek-v4-pro'] },
  { id: 'openai', name: 'OpenAI', models: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo'] },
  { id: 'anthropic', name: 'Claude', models: ['claude-sonnet-4-20250514', 'claude-opus-4-20250514'] },
  { id: 'custom', name: '自定义', models: [] },
]

export default function SettingsPage() {
  const [provider, setProvider] = useState('deepseek')
  const [apiKey, setApiKey] = useState('')
  const [baseUrl, setBaseUrl] = useState('')
  const [saved, setSaved] = useState(false)

  const handleSave = async () => {
    await saveLLMConfig({ provider, api_key: apiKey, base_url: baseUrl })
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  return (
    <div className="min-h-screen bg-paper py-12 px-6">
      <div className="max-w-xl mx-auto">
        <h1 className="font-serif text-3xl font-bold mb-8">LLM 配置</h1>
        
        {/* Provider选择 */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">提供商</label>
          <div className="grid grid-cols-2 gap-3">
            {PROVIDERS.map(p => (
              <button
                key={p.id}
                onClick={() => setProvider(p.id)}
                className={`p-4 rounded-lg border text-left transition-colors ${
                  provider === p.id 
                    ? 'border-ink bg-ink text-paper' 
                    : 'border-border hover:border-ink-light'
                }`}
              >
                {p.name}
              </button>
            ))}
          </div>
        </div>

        {/* API Key */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">API Key</label>
          <input
            type="password"
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
            placeholder="sk-..."
            className="w-full px-4 py-3 border border-border rounded-lg bg-paper focus:border-ink outline-none"
          />
        </div>

        {/* Base URL (自定义Provider) */}
        {provider === 'custom' && (
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Base URL</label>
            <input
              type="text"
              value={baseUrl}
              onChange={e => setBaseUrl(e.target.value)}
              placeholder="https://api.example.com/v1"
              className="w-full px-4 py-3 border border-border rounded-lg bg-paper focus:border-ink outline-none"
            />
          </div>
        )}

        <button
          onClick={handleSave}
          className="w-full py-3 bg-ink text-paper rounded-lg font-medium"
        >
          保存配置
        </button>

        {saved && (
          <p className="mt-4 text-green-600 text-center text-sm">配置已保存</p>
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 3: 创建 LLM API 路由**

```python
# src/mcp_server/llm/routes.py
from flask import Blueprint, request, jsonify
from .llm_router import get_router

bp = Blueprint('llm', __name__, url_prefix='/api/llm')

@bp.route('/config', methods=['GET'])
def get_config():
    router = get_router()
    return jsonify(router._config)

@bp.route('/config', methods=['POST'])
def save_config():
    data = request.json
    router = get_router()
    router.configure(
        provider=data['provider'],
        api_key=data['api_key'],
        base_url=data.get('base_url'),
    )
    return jsonify({"status": "ok"})
```

- [ ] **Step 4: 测试配置页面**

Run: 启动 backend + frontend，访问 /settings

- [ ] **Step 5: Commit**

```bash
git add frontend/app/settings/page.tsx frontend/lib/api.ts src/mcp_server/llm/routes.py
git commit -m "feat: add LLM settings page with provider configuration"
```

---

## Task 5: 端到端集成

- [ ] **Step 1: 更新 server.py 挂载llm路由**

```python
from .llm.routes import bp as llm_bp
app.register_blueprint(llm_bp)
```

- [ ] **Step 2: 添加 .env.example**

```bash
NEXT_PUBLIC_API_BASE=http://localhost:8000
DEEPSEEK_API_KEY=your_key_here
```

- [ ] **Step 3: 更新 README**

添加 LLM 配置说明和前端运行方式

- [ ] **Step 4: 最终验证**

```bash
# Backend
cd src/mcp_server && python server.py

# Frontend (新窗口)
cd frontend && npm run dev

# 访问 localhost:3000 验证落地页
# 访问 localhost:3000/settings 验证配置页
```

---

## 实施检查清单

- [ ] Task 1: 通用LLM路由核心 ✅
- [ ] Task 2: Next.js 项目初始化 ✅
- [ ] Task 3: 落地页开发 ✅
- [ ] Task 4: LLM配置页面 ✅
- [ ] Task 5: 端到端集成 ✅

---

**Plan complete.** 实施选项：

**1. Subagent-Driven (推荐)** - 每task派一个子agent，task间review，快速迭代

**2. Inline Execution** - 在本session用executing-plans批量执行，带checkpoint

哪个方式？
