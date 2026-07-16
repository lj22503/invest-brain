# MCP + InvestBrain = 你的投资 AI Agent

> 用 MCP 协议让你的 AI 编程助手变成投资纪律教练
>
> 作者：InvestBrain 团队
> 日期：2026-07-16
> 预计阅读：8 分钟

---

## 一、什么是 MCP，为什么它改变了游戏规则？

MCP（Model Context Protocol）是 Anthropic 推出的开放协议，让 AI 模型可以安全地调用外部工具和数据源。类比一下：

| 类比 | 说明 |
|------|------|
| **USB-C 协议** | 统一了设备连接标准，一根线搞定充电+数据传输+视频输出 |
| **MCP 协议** | 统一了 AI 工具连接标准，一个协议让任何 AI 客户端调用任何工具 |

之前，如果你想用 AI 分析投资数据，你需要：
1. 把数据手动复制粘贴给 ChatGPT
2. 每次对话都重新描述上下文
3. AI 对你一无所知，从头开始理解

有了 MCP，你只需要：
1. AI 直接调用你的投资工具（RAG 知识库、行为模式分析、提醒系统）
2. AI 记住你的投资历史和偏好
3. 像和真人投资教练对话一样自然

---

## 二、InvestBrain MCP Server 能做什么？

InvestBrain 是一个专为个人投资者设计的 MCP Server，包含 35+ 个工具，覆盖四大能力：

| 能力 | 工具示例 | 一句话说明 |
|------|---------|-----------|
| **投资 RAG** | `rag_ask_investment` | 检索 16 位大师思想，回答投资问题 |
| **想法记录** | `thought_record_thought` | 一句话记录投资想法，自动解析+关联历史 |
| **行为模式** | `memory_get_behavior_patterns` | 自动检测追高、恐慌卖出等 5 种偏差 |
| **提醒系统** | `reminder_set_reminder` | 价格/时间/条件监控，支持多渠道推送 |

---

## 三、5 分钟上手指南

### 3.1 安装

```bash
git clone https://github.com/lj22503/invest-brain.git
cd invest-brain/src/mcp_server
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY
```

### 3.2 配置 Claude Desktop

编辑 `claude_desktop_config.json`（Windows: `%APPDATA%\Claude\claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "investbrain": {
      "command": "python",
      "args": [
        "D:\\path\\to\\invest-brain\\src\\mcp_server\\server.py"
      ]
    }
  }
}
```

重启 Claude Desktop，在对话输入框下方会看到 🔌 图标，点击可以看到 InvestBrain 的工具列表。

### 3.3 配置 Cursor

在 Cursor 中，编辑 `.cursor/mcp.json`：

```json
{
  "mcpServers": {
    "investbrain": {
      "command": "python",
      "args": ["src/mcp_server/server.py"]
    }
  }
}
```

---

## 四、实战：用 Claude 分析你的投资行为

以下是一个完整的对话示例，展示 InvestBrain 如何在真实场景中发挥作用。

### 场景：我最近频繁交易，想看看自己有什么问题

**你**：帮我分析一下我最近的投资行为，看看有没有什么规律。

**Claude**（调用 `memory_get_behavior_patterns()`）：
> 根据你的行为记录，我检测到以下模式：
>
> 1. **追高倾向（严重度：高）**：过去 3 个月，你在股价上涨 5% 后买入的概率是 72%，而这些买入中 65% 在一周内亏损。典型案例：6月15日宁德时代涨停后追入，次日回调 4.2%。
>
> 2. **过早止盈（严重度：中）**：你平均在盈利 8% 时卖出，而这些股票后续继续上涨的平均幅度是 23%。典型案例：贵州茅台在盈利 7% 时卖出，后续 2 个月又涨了 18%。
>
> 3. **情绪化交易（严重度：低）**：周五下午的交易频率是平日的 2.3 倍，可能与周末前的心态有关。
>
> 建议：在下一次追高冲动时，设定一个 24 小时冷静期。

---

**你**：巴菲特会怎么看我的追高问题？

**Claude**（调用 `rag_get_master_view(master="巴菲特", topic="追高")`）：
> 巴菲特的核心原则是"在别人恐惧时贪婪，在别人贪婪时恐惧"。
>
> 关于你的追高行为，巴菲特会说：
>
> > "股市是一个把钱从不耐烦的人转移到耐心的人身上的机器。你在股价上涨 5% 后买入，本质上是让短期情绪而不是长期价值驱动你的决策。"
>
> 他的建议是：在买入前问自己"我愿意持有这家公司 10 年吗？"如果答案是否定的，10 分钟也不要持有。

---

**你**：帮我设定一个提醒，如果我想查某只股票的价格超过 3 次，就提醒我先看一遍行为报告再做决定。

**Claude**（调用 `reminder_set_reminder`）：
> 已设定条件提醒：
> - 条件：24 小时内查询同一股票超过 3 次
> - 动作：展示该股票的行为模式报告 + 推送飞书通知
> - 原因：高频查询通常是冲动交易的前兆

---

## 五、技术架构一览

```
┌─────────────────────────────────────────────────┐
│                  AI 客户端                        │
│   Claude Desktop / Cursor / Continue / ...       │
└─────────────────┬───────────────────────────────┘
                  │  MCP Protocol (stdio)
┌─────────────────▼───────────────────────────────┐
│              InvestBrain MCP Server               │
│                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ RAG 引擎  │ │ 记忆系统 │ │ 行为模式挖掘     │ │
│  │          │ │          │ │                  │ │
│  │ GraphRAG │ │ SQLite   │ │ PatternDetector  │ │
│  │ Chroma   │ │ 向量检索 │ │ 5种偏差检测      │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ 提醒系统 │ │ 数据源   │ │ 本地模型兜底     │ │
│  │          │ │          │ │                  │ │
│  │ 多渠道   │ │ AKShare  │ │ ONNX Qwen2-0.5B  │ │
│  │ 条件触发 │ │ Tushare  │ │ 离线可用         │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
└─────────────────────────────────────────────────┘
```

### 为什么选择 MCP 架构？

| 对比维度 | 传统 SaaS | MCP Server |
|---------|-----------|------------|
| 数据隐私 | 数据上传到云端 | 数据留在本地 |
| 可定制性 | 封闭功能集 | 任意 AI 客户端可调用 |
| 成本 | 月费 $30-50 | 免费开源 |
| 集成 | 独立应用 | 嵌入你已有的 AI 工作流 |
| 可扩展 | 等厂商更新 | 自己写 MCP Tool |

---

## 六、进阶：用 Python 脚本直接调用

如果你不想用 AI 客户端，也可以直接用 Python 脚本调用：

```python
import subprocess
import json

def call_mcp_tool(tool_name: str, arguments: dict) -> dict:
    """通过 MCP stdio 协议调用 InvestBrain 工具"""
    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        },
        "id": 1
    }

    proc = subprocess.run(
        ["python", "src/mcp_server/server.py"],
        input=json.dumps(request),
        capture_output=True,
        text=True
    )
    return json.loads(proc.stdout)

# 问一个投资问题
result = call_mcp_tool("rag_ask_investment", {
    "question": "什么是安全边际？为什么它很重要？"
})
print(result["answer"])

# 记录一个投资想法
call_mcp_tool("thought_record_thought", {
    "text": "腾讯跌到300了，PE不到15，考虑建仓"
})
```

---

## 七、下一步

1. **Clone 项目**：[github.com/lj22503/invest-brain](https://github.com/lj22503/invest-brain)
2. **配置 Claude Desktop**：按照上面的 JSON 配置，5 分钟搞定
3. **开始对话**：直接在 Claude 中说"帮我分析一下我的投资行为"
4. **分享你的用例**：在 [社区用例 Issue](https://github.com/lj22503/invest-brain/issues) 中告诉我们你是怎么用的

---

## 附录：MCP 生态资源

| 资源 | 链接 |
|------|------|
| MCP 官方文档 | [modelcontextprotocol.io](https://modelcontextprotocol.io) |
| MCP Server 列表 | [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) |
| InvestBrain 源码 | [github.com/lj22503/invest-brain](https://github.com/lj22503/invest-brain) |
| 更多 MCP 工具 | [mcp.so](https://mcp.so) |
