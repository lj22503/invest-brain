# 知识图谱Schema — 投资助手

## 1. 设计目标

支撑大师思想RAG检索，支持：
- "巴菲特怎么看护城河"
- "段永平的投资原则和巴菲特有什么区别"
- "哪些大师反对加杠杆"
- "价值投资适用于什么市场条件"

---

## 2. 实体类型

### 2.1 投资大师 (InvestmentMaster)

| 属性 | 类型 | 说明 |
|------|------|------|
| id | string | 唯一标识，如 "buffett" |
| name | string | 中文名，如 "沃伦·巴菲特" |
| name_en | string | 英文名，如 "Warren Buffett" |
| era | string | 时代，如 "1950-至今" |
| background | string | 背景简介 |
| core_principles | list[string] | 核心理念列表 |
| methodology | string | 方法论概述 |
| applicable_conditions | list[string] | 适用条件 |
| limitations | list[string] | 局限性 |
| quotes | list[string] | 代表性语录 |

**示例**：
```json
{
  "id": "buffett",
  "name": "沃伦·巴菲特",
  "core_principles": ["护城河", "安全边际", "能力圈", "别人贪婪时恐惧，别人恐惧时贪婪"],
  "limitations": ["不擅长科技股", "对年轻公司判断力弱"]
}
```

---

### 2.2 投资理论 (InvestmentTheory)

| 属性 | 类型 | 说明 |
|------|------|------|
| id | string | 唯一标识，如 "value_investing" |
| name | string | 理论名称 |
| school | string | 所属门派，如 "价值投资" |
| core_logic | string | 核心逻辑 |
| key_concepts | list[string] | 关键概念 |
| relationship_with_others | map | 与其他理论的关系描述 |

---

### 2.3 投资策略 (InvestmentStrategy)

| 属性 | 类型 | 说明 |
|------|------|------|
| id | string | 唯一标识 |
| name | string | 策略名称 |
| trigger_conditions | list[string] | 触发条件 |
| operations | list[string] | 操作方式 |
| risk_boundaries | list[string] | 风险边界 |
| applicable_assets | list[string] | 适用资产 |

---

### 2.4 市场条件 (MarketCondition)

| 属性 | 类型 | 说明 |
|------|------|------|
| id | string | 唯一标识 |
| type | enum | 牛市/熊市/震荡/衰退/复苏 |
| valuation_level | string | 估值水平描述 |
| sentiment | string | 市场情绪描述 |
| indicators | list[string] | 典型指标 |

---

### 2.5 投资概念 (InvestmentConcept)

| 属性 | 类型 | 说明 |
|------|------|------|
| id | string | 唯一标识，如 "moat" |
| name | string | 概念名称 |
| definition | string | 定义 |
| origin | string | 出处/来源 |
| examples | list[string] | 案例 |

---

## 3. 关系类型

### 3.1 继承自 (INHERITED_FROM)

```
大师 -> 继承自 -> 大师
理论 -> 继承自 -> 理论
```

示例：段永平 -> 继承自 -> 巴菲特（段永平深受巴菲特影响）

---

### 3.2 发展自 (DEVELOPED_FROM)

```
概念 -> 发展自 -> 概念
策略 -> 发展自 -> 概念
```

示例：竞争壁垒 -> 发展自 -> 护城河

---

### 3.3 矛盾于 (CONTRADICTS_WITH)

```
理论 <-> 矛盾于 <-> 理论
策略 <-> 矛盾于 <-> 策略
```

示例：价值投资 矛盾于 趋势投资

---

### 3.4 适用于 (APPLICABLE_TO)

```
理论 -> 适用于 -> 市场条件
策略 -> 适用于 -> 资产类型
大师 -> 适用于 -> 市场条件
```

示例：价值投资 -> 适用于 -> 优质蓝筹

---

### 3.5 警示 (WARNS_ABOUT)

```
大师 -> 警示 -> 行为/原则
理论 -> 警示 -> 风险
```

示例：巴菲特 -> 警示 -> 不要加杠杆

---

### 3.6 倡导 (ADVOCATES)

```
大师 -> 倡导 -> 原则/行为
理论 -> 倡导 -> 策略
```

示例：巴菲特 -> 倡导 -> 安全边际

---

### 3.7 擅长 (EXCELS_IN)

```
大师 -> 擅长 -> 投资领域
```

示例：巴菲特 -> 擅长 -> 消费股

---

## 4. 核心实体清单

### 4.1 大师

| ID | 名称 | 核心理念 |
|----|------|----------|
| buffett | 沃伦·巴菲特 | 护城河、安全边际、能力圈、别人贪婪时恐惧 |
| munger | 查理·芒格 | 多元思维模型、好生意、逆向思维 |
| duanyongping | 段永平 | 本分、不懂不投、stop doing list |
| howard_marks | 霍华德·马克斯 | 周期、风险认识、第二层思维 |
| li_lu | 李录 | 文明现代化、价值投资中国化 |

### 4.2 理论

| ID | 名称 | 门派 |
|----|------|------|
| value_investing | 价值投资 | 价值派 |
| growth_investing | 成长投资 | 成长派 |
| trend_investing | 趋势投资 | 趋势派 |
| cycle_theory | 周期理论 | 宏观派 |
| contrarian |逆向投资 | 行为金融 |

### 4.3 核心概念

| ID | 名称 | 来源 |
|----|------|------|
| moat | 护城河 | 巴菲特 |
| margin_of_safety | 安全边际 | 格雷厄姆 |
| circle_of_competence | 能力圈 | 巴菲特 |
| asymmetric_risk | 非对称风险 | 塔勒布 |
| second_level_thinking | 第二层思维 | 霍华德·马克斯 |

### 4.4 策略

| ID | 名称 | 触发条件 |
|----|------|----------|
| value_buy | 价值买入 | PE分位<20%，优质公司 |
| contrarian_buy | 逆向买入 | 市场恐惧，优质资产被错杀 |
| momentum_buy | 趋势买入 | 均线多头排列，成交量放大 |

### 4.5 市场条件

| ID | 类型 | 特征 |
|----|------|------|
| bull_high_valuation | 牛市高估值 | PE分位>80%，情绪亢奋 |
| bear_low_valuation | 熊市低估值 | PE分位<20%，情绪恐慌 |
| market_volatile | 震荡市 | 估值中位，情绪摇摆 |

---

## 5. Cypher Schema (Neo4j)

```cypher
// 节点类型
CREATE CONSTRAINT master_id IF NOT EXISTS
FOR (m:InvestmentMaster) REQUIRE m.id IS UNIQUE;

CREATE CONSTRAINT theory_id IF NOT EXISTS
FOR (t:InvestmentTheory) REQUIRE t.id IS UNIQUE;

CREATE CONSTRAINT concept_id IF NOT EXISTS
FOR (c:InvestmentConcept) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT strategy_id IF NOT EXISTS
FOR (s:InvestmentStrategy) REQUIRE s.id IS UNIQUE;

CREATE CONSTRAINT condition_id IF NOT EXISTS
FOR (c:MarketCondition) REQUIRE c.id IS UNIQUE;
```

---

## 6. 图索引设计

### 6.1 必须创建索引

```cypher
// 向量索引（用于语义检索）
CREATE VECTOR INDEX master_embeddings IF NOT EXISTS
FOR (m:InvestmentMaster) ON (m.embedding)
OPTIONS {indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
}};

// 关键词索引
CREATE INDEX master_name IF NOT EXISTS
FOR (m:InvestmentMaster) ON (m.name);

CREATE INDEX concept_name IF NOT EXISTS
FOR (c:InvestmentConcept) ON (c.name);
```

---

## 7. 与向量检索的配合

- **精确关系查询**：用Cypher查询"巴菲特的学生有哪些"
- **语义相似性**：用向量检索"和护城河概念相关的投资思想"
- **混合查询**：先向量检索相似概念，再图查询概念的关联

---

## 8. 实现建议

| 阶段 | 内容 |
|------|------|
| Phase A | 用NetworkX做内存图+Chroma向量库（轻量） |
| Phase B | 迁移到Neo4j（生产级） |

---

## 9. 验证查询

```cypher
// 查询巴菲特的核心理念
MATCH (m:InvestmentMaster {id: 'buffett'})
RETURN m.core_principles

// 查询哪些大师反对加杠杆
MATCH (m:InvestmentMaster)-[:WARNS_ABOUT]->(w {name: '加杠杆'})
RETURN m.name

// 查询护城河概念的发展脉络
MATCH path = (c:InvestmentConcept {id: 'moat'})<-[:DEVELOPED_FROM*]-(related)
RETURN path
```