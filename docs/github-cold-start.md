# InvestBrain GitHub 开源冷启动方案

> 日期：2026-07-16
> 任务：D1
> 类型：渠道策略 + 传播物料

---

## 一、渠道策略

### 1.1 目标用户画像与渠道匹配

| 渠道 | 核心用户 | 调性 | 首发优先级 |
|------|---------|------|:---:|
| **GitHub** | Persona 小李（程序员/产品经理，开源爱好者） | 技术导向、Show HN 风格 | **P0** |
| **V2EX** | 技术社区的中文投资者，对工具类项目接受度高 | 分享贴 + 实用主义叙事 | **P0** |
| **即刻** | 产品经理/早期采用者，社区传播力强 | "我做了一个..."个人叙事 | **P1** |
| **掘金** | 前端/全栈开发者，对 MCP 架构感兴趣 | 技术深度文（D2 博文转发） | **P1** |
| **知乎** | 泛投资群体，长尾流量 | "如何用AI辅助投资决策"问答 | **P2** |
| **雪球** | Persona 老王（价值投资者） | 产品介绍帖，强调"不是投顾" | **P2** |
| **Product Hunt** | 国际开发者社区，出海曝光 | 英文 launch | **P2** |

### 1.2 首发顺序

```
Week 1: GitHub（README 优化 + Demo） → V2EX（分享帖）
Week 2: 即刻（个人叙事贴） → 掘金（技术文转发）
Week 3: 收集反馈，迭代 README，准备 Product Hunt
```

---

## 二、各渠道文案方向

### 2.1 GitHub README — "5分钟快速体验"章节

**目标**：让开发者在 5 分钟内跑起来并看到价值。

**要点**：
- 一条命令启动（`pip install -r requirements.txt && python server.py`）
- 一个完整的示例对话（录屏 GIF 或文字示例）
- "为什么用 MCP" 一句话说明
- 明确的下一步（Star / Issue / 贡献指南）

### 2.2 V2EX 分享帖

**定位**：技术社区的项目分享，诚实透明。

**叙事框架**：
1. 我在投资中反复犯同样的错误（追高、恐慌卖出）
2. 我决定用 AI 做一个"纪律锚点"而不是"选股工具"
3. 用 MCP 架构让 AI Agent 可以调用投资分析工具
4. 开源在 GitHub，欢迎大家试用和提意见

**标签**：#分享创造 #投资 #AI #开源

### 2.3 即刻动态

**定位**：个人叙事 + 产品展示，轻量传播。

**叙事框架**：
1. "我做了一个投资纪律工具，名字叫 InvestBrain"
2. 一张 Dashboard 截图或 Demo GIF
3. "不是帮人选股，是帮人管住自己"
4. GitHub 链接 + Star 引导

### 2.4 掘金技术文

**定位**：深度技术文章，展示 MCP 架构价值。

**要点**：
- 标题："如何用 MCP 协议打造你的投资第二大脑"
- 展示 Claude Code / Cursor 调用 InvestBrain MCP Server 的完整流程
- 代码示例 + 架构图
- 与 D2 任务协同（此文可作为 D2 MCP 技术博文的渠道版本）

---

## 三、GitHub 项目优化清单

### 3.1 README 必做项

- [x] 项目定位一句话（已有："有经验投资者的纪律自主工具"）
- [ ] "5分钟快速体验"章节（**本次新增**）
- [ ] Demo GIF 嵌入（A1 交付的录屏，390×844）
- [ ] 安装步骤精简为 3 步
- [ ] 示例对话展示核心价值
- [ ] Star / Fork 徽章
- [ ] 贡献指南链接

### 3.2 社区运营物料

- [ ] Issue 模板：Bug Report / Feature Request
- [ ] `awesome-investbrain` 社区用例收集 Issue（置顶）
- [ ] CONTRIBUTING.md 贡献指南
- [ ] 项目 Logo（可选，后续迭代）

### 3.3 SEO 优化

- [ ] 仓库 Topics 标签：`investment` `mcp-server` `ai-agent` `rag` `python` `deepseek` `quantitative-analysis`
- [ ] 仓库 Description：`AI-powered investment discipline tool — your second brain for better decisions. MCP Server × RAG × Behavior Pattern Mining.`
- [ ] 社交预览图（Open Graph image）

---

## 四、传播节奏与 KPI

### 4.1 首周目标（Week 1）

| 指标 | 目标 |
|------|:---:|
| GitHub Stars | 50+ |
| V2EX 帖子回复 | 20+ |
| 即刻点赞/转发 | 30+ |
| Issue 提交 | 3+ |
| Fork | 10+ |

### 4.2 首月目标（Month 1）

| 指标 | 目标 |
|------|:---:|
| GitHub Stars | 200+ |
| 社区贡献者 PR | 5+ |
| awesome-investbrain 用例收集 | 10+ |
| 外部文章/视频提及 | 3+ |

---

## 五、决策确认

### 5.1 渠道首发顺序

**推荐**：GitHub + V2EX 同步首发（Week 1），即刻跟进（Week 2）。

理由：GitHub 是项目主页，增强后可直接承载所有渠道流量；V2EX 是中文技术社区最高效的冷启动渠道；即刻覆盖产品经理群体的二次传播。

### 5.2 文案核心叙事

**统一叙事线**（所有渠道复用）：
> "我做了一个投资纪律工具。不是帮人选股，是帮人管住自己。开源，MCP 架构，你的 AI Agent 可以直接调用。"
