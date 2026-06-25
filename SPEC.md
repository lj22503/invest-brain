# InvestBrain 网站 SPEC

## 项目概述

**目标**：为 InvestBrain 建设 Agent-Friendly 的完整营销网站
**技术栈**：Next.js 14 + Tailwind CSS + Vercel 部署
**页面数量**：4 个（首页 / About / 功能 / FAQ）

---

## 页面结构

### 1. 首页 `/`
基于现有 `brain-landing-preview.html` 改写，保持现有文案结构。

**内容区块：**
- Hero：标题"锚定最重要的事，不被市场吹走"
- 问题陈述：市场噪音（4 个引述卡片）
- 解决方案：投资锚三件事（记下来 / 映照 / 提醒）
- 对比：有锚 vs 无锚表格
- 四大核心能力入口（对应功能页锚点）
- 差异化定位（镜子 + 纪律锚点）
- 数据展示（16 位大师 / 多模型 AI / 本地存储）
- CTA

**数字修正：**
- 大师数量：16 位（移除"35 个智能工具"表述，改为"多模型 AI 引擎"）
- LLM：多 Provider 支持（DeepSeek / OpenAI / Anthropic）

**Schema.org：** Product + Organization

### 2. About `/about`
展开现有落地页的定位内容。

**内容区块：**
- 品牌故事：我们发现的问题（投资者知行合一难）
- 核心定位：不是投顾，不给建议，是镜子 + 纪律锚点
- 产品原则：不交易、不收费投顾、数据本地存储
- 支持的 AI 模型（多 Provider 说明）

### 3. 功能 `/features`
4 个功能详细介绍，每个功能独立区块。

**内容：**
- 想法记录（thought_record）：一句话输入，AI 解析标的/价格/指标，生成结构化卡片
- 大师思想库（rag_ask_investment）：16 位投资大师思想，随时对照
- 行为模式报告（pattern_get_report）：发现追高、止损过早等重复偏差
- 条件提醒（reminder_set）：价格/条件触发，不被情绪牵着走

**交互：** 各功能卡片有展开详情，关联大师思想库可跳转。

### 4. FAQ `/faq`
基于用户指定的 4 类问题。

**问题覆盖：**
- 如何使用（基本操作流程）
- 安全保障（数据本地存储、不上传、不做交易）
- 最佳使用案例（典型场景描述）
- 联系我们（反馈/需求渠道）

---

## SEO / Agent-Friendly 规范

### 必须实现
- [x] 所有页面 HTML 语义化（H1/H2/H3 层级清晰）
- [x] Schema.org JSON-LD（Product）— layout.tsx 内联
- [x] `/llms.txt` 根目录文件 — public/llms.txt
- [x] `robots.txt` 不屏蔽主流 AI 爬虫 — public/robots.txt
- [x] 核心内容纯 HTML，无 JS 依赖（Next.js SSR 输出 HTML）

### 推荐实现
- [x] Open Graph meta — layout.tsx 内置
- [ ] `Accept: text/markdown` 内容协商
- [ ] FAQPage Schema.org
- [ ] 页面加载速度优化（Next.js Image / Font 优化）

---

## 产出标准

1. ✅ 4 个页面通过 `next build` 编译成功
2. 待验证：所有页面 Lighthouse 基本检查
3. 待验证：Schema.org Rich Results Test
4. ✅ `/llms.txt` 已生成

## 完成记录

- 2026-06-25：完成 4 个页面（首页 / About / 功能 / FAQ）+ llms.txt + robots.txt
- 数字修正：16 位大师（原 17），多模型 AI（原只写 DeepSeek）
