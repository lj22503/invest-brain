"""Investment RAG tools - ask_investment, get_master_view, search_knowledge"""

import json
import re
from pathlib import Path
from typing import Optional, Literal
from mcp.server.fastmcp import FastMCP

from ..knowledge.graph_client import get_graph_client
from ..knowledge.vector_store import get_vector_store
from ..llm import get_deepseek_client

rag_tools = FastMCP("rag-tools")

# Knowledge base roots
_GRAPH_ROOT = Path(__file__).resolve().parents[3] / "data" / "graph"
_INDUSTRY_ROOT = Path(__file__).resolve().parents[3] / "data" / "industry"
_FRAMEWORK_ROOT = Path(__file__).resolve().parents[3] / "data" / "frameworks"


def _search_file_content(file_path: Path, query: str, max_results: int = 3) -> list[dict]:
    """Search within a file for query keywords."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return []

    query_lower = query.lower()
    lines = content.split("\n")
    results = []

    # Search line by line for keyword matches
    for i, line in enumerate(lines):
        if query_lower in line.lower():
            # Clean line for display
            clean_line = line.strip()
            if len(clean_line) > 5:  # Skip very short lines
                results.append({
                    "line_num": i + 1,
                    "content": clean_line[:200],  # Truncate long lines
                    "file": file_path.name,
                })
                if len(results) >= max_results:
                    break

    return results


def _search_industry_knowledge(query: str) -> list[dict]:
    """Search industry knowledge files."""
    results = []

    if not _INDUSTRY_ROOT.exists():
        return results

    query_lower = query.lower()

    # Search JSON files
    for f in _INDUSTRY_ROOT.glob("*.json"):
        if "申万" in f.name:
            try:
                with open(f, encoding="utf-8") as fp:
                    data = json.load(fp)
                # Search categories
                for cat in data.get("categories", []):
                    cat_name = cat.get("name", "").lower()
                    if query_lower in cat_name or query_lower in " ".join(cat.get("sub_industries", [])).lower():
                        results.append({
                            "type": "industry",
                            "id": cat.get("code", ""),
                            "name": cat.get("name", ""),
                            "definition": f"申万行业: {cat.get('name', '')} | 子行业: {', '.join(cat.get('sub_industries', [])[:5])}",
                            "key_indicators": cat.get("key_indicators", []),
                        })
                # Search trigger keywords
                trigger_kw = data.get("trigger_keywords", {})
                for kw, industries in trigger_kw.items():
                    if query_lower in kw.lower():
                        results.append({
                            "type": "industry_keyword",
                            "keyword": kw,
                            "industries": industries,
                            "definition": f"触发词'{kw}'对应行业: {', '.join(industries[:5])}",
                        })
            except Exception:
                pass

    # Search markdown files
    for f in _INDUSTRY_ROOT.glob("*.md"):
        with open(f, encoding="utf-8") as fp:
            content = fp.read()
        if query_lower in content.lower():
            # Extract title
            title = f.stem.replace("_", " ").replace("-", " ")
            results.append({
                "type": "industry",
                "id": f.stem,
                "name": title,
                "definition": content[:500],
            })

    return results[:5]


def _search_framework_knowledge(query: str) -> list[dict]:
    """Search framework knowledge files."""
    results = []

    if not _FRAMEWORK_ROOT.exists():
        return results

    query_lower = query.lower()

    for f in _FRAMEWORK_ROOT.glob("*.md"):
        with open(f, encoding="utf-8") as fp:
            content = fp.read()
        if query_lower in content.lower():
            title = content.split("\n")[0].lstrip("# ").strip() if content.startswith("#") else f.stem
            results.append({
                "type": "framework",
                "id": f.stem,
                "name": title,
                "definition": content[:800],
            })

    return results[:3]


def _llm_synthesize(question: str, context: list) -> str:
    """
    用 DeepSeek 合成 RAG 答案。
    scene: rag_synthesis
    """
    if not context:
        return "抱歉，知识库中暂无相关内容。"

    # 构建上下文文本
    context_texts = []
    for i, ctx in enumerate(context[:5], 1):
        name = ctx.get("name", ctx.get("id", ""))
        view = ctx.get("view", ctx.get("definition", ""))
        quote = ctx.get("quotes", [])
        source = ctx.get("source", "")
        if quote:
            view = f"{view}。代表语录：{quote[0]}"
        if source:
            view = f"{view}（来源：{source}）"
        context_texts.append(f"{i}. 【{name}】{view}")

    context_str = "\n\n".join(context_texts)

    prompt = f"""基于以下大师思想库检索结果，回答用户的问题。

问题：{question}

参考内容：
{context_str}

要求：
1. 综合参考内容，给出有洞察的回答
2. 引用时标注来源
3. 如有必要，可附加1-2个"拷问问题"引导用户深入思考
4. 用简洁、有洞见的中文回复

回答："""

    try:
        client = get_deepseek_client()
        if client is None:
            raise RuntimeError("LLM not available")
        return client.chat_simple(prompt, scene="rag_synthesis")
    except Exception:
        # 降级：简单拼接
        return _fallback_synthesize(question, context)


def _fallback_synthesize(question: str, context: list) -> str:
    """降级合成：简单拼接（LLM 不可用时）"""
    if not context:
        return "抱歉，知识库中暂无相关内容。"

    answer_parts = []
    for i, ctx in enumerate(context[:3], 1):
        name = ctx.get("name", ctx.get("id", ""))
        view = ctx.get("view", ctx.get("definition", ""))
        quote = ctx.get("quotes", [])
        if quote:
            view = f"{view} - {quote[0]}"
        answer_parts.append(f"{i}. {name}：{view}")

    return "根据大师思想库检索结果：\n\n" + "\n\n".join(answer_parts)


@rag_tools.tool()
def ask_investment(question: str) -> dict:
    """
    Ask an investment question and get RAG-augmented answer.

    Args:
        question: Investment question (e.g., "什么是护城河？")

    Returns:
        dict: Answer with source citations from master knowledge base
    """
    graph = get_graph_client()

    # Search concepts and masters by keywords
    keywords = question.replace("？", "").replace("?", "").strip()
    concepts = graph.find_concepts_by_keyword(keywords)
    masters = graph.find_masters_by_keyword(keywords)

    # Also try direct node query
    direct_query = graph.query(name=keywords)

    # Combine results
    all_results = []
    for item in concepts + masters + direct_query:
        if item not in all_results:
            all_results.append(item)

    # Vector search as补充 (lazy load, may fail if ONNX not ready)
    try:
        vs = get_vector_store()
        vector_results = vs.search(keywords, top_k=3)
        for vr in vector_results:
            meta = vr.get("metadata", {})
            all_results.append({
                "id": vr.get("id"),
                "name": meta.get("name", vr.get("id")),
                "type": meta.get("type", "vector"),
                "definition": vr.get("text", ""),
            })
    except Exception:
        pass  # Vector store may not be available or ONNX still downloading

    # Industry knowledge search
    industry_results = _search_industry_knowledge(keywords)
    for ir in industry_results:
        if ir not in all_results:
            all_results.append(ir)

    # Framework knowledge search
    framework_results = _search_framework_knowledge(keywords)
    for fr in framework_results:
        if fr not in all_results:
            all_results.append(fr)

    # Research report search (vector)
    try:
        research_results = vs.search_research(keywords, top_k=5)
        for rr in research_results:
            all_results.append({
                "id": rr.get("id"),
                "name": rr.get("title", rr.get("id")),
                "type": "research_report",
                "definition": rr.get("text", ""),
                "org_name": rr.get("org_name", ""),
                "stock_name": rr.get("stock_name", ""),
                "industry_name": rr.get("industry_name", ""),
                "rating": rr.get("rating", ""),
                "publish_date": rr.get("publish_date", ""),
            })
    except Exception:
        pass  # Research collection may be empty

    # LLM synthesis
    answer = _llm_synthesize(question, all_results)

    # Build source citations
    sources = []
    for item in all_results[:3]:
        sources.append({
            "id": item.get("id"),
            "name": item.get("name", item.get("name_en", "")),
            "type": item.get("type"),
        })

    return {
        "answer": answer,
        "sources": sources,
        "master_views": sources,
    }


@rag_tools.tool()
def get_master_view(master: str, topic: str) -> dict:
    """
    Get a specific master's view on a topic.

    Args:
        master: Master name (e.g., "巴菲特", "芒格", "段永平")
        topic: Topic to query (e.g., "护城河", "安全边际")

    Returns:
        dict: Master's view on the topic with citations
    """
    graph = get_graph_client()

    # Find master by name (support both Chinese and English IDs)
    master_lower = master.lower()
    master_node = None
    for node, data in graph.graph.nodes(data=True):
        if data.get("type") != "InvestmentMaster":
            continue
        if master_lower == node.lower():
            master_node = (node, data)
            break
        if master_lower in data.get("name", "").lower() or master_lower in data.get("name_en", "").lower():
            master_node = (node, data)
            break

    if not master_node:
        return {
            "master": master,
            "topic": topic,
            "view": f"未找到大师 '{master}' 的信息",
            "source": None,
            "related_topics": [],
        }

    master_id, master_data = master_node

    # Find topic concept
    topic_lower = topic.lower()
    concept_node = None
    for node, data in graph.graph.nodes(data=True):
        if data.get("type") != "InvestmentConcept":
            continue
        if topic_lower == node.lower() or topic_lower in data.get("name", "").lower():
            concept_node = (node, data)
            break

    # Get relationships between master and topic
    related = graph.get_related(master_id)
    matching_relations = []
    for rel in related:
        if topic_lower in rel.get("id", "").lower() or topic_lower in rel.get("name", "").lower():
            matching_relations.append(rel)

    # Build view text
    view_parts = []
    if matching_relations:
        for rel in matching_relations:
            desc = rel.get("description", "")
            if desc:
                view_parts.append(desc)
    if not view_parts and concept_node:
        concept_name = concept_node[1].get("name", topic)
        definition = concept_node[1].get("definition", "")
        if definition:
            view_parts.append(f"概念'{concept_name}'的定义：{definition}")
    if not view_parts:
        # Fall back to master's quotes or core principles
        quotes = master_data.get("quotes", [])
        if quotes:
            view_parts.append(f"代表语录：{quotes[0]}")
        core_prins = master_data.get("core_principles", [])
        if core_prins:
            view_parts.append(f"核心理念：{', '.join(core_prins[:3])}")

    view = "；".join(view_parts) if view_parts else "暂无相关信息"

    # Build related topics
    related_topics = [
        {"id": rel.get("id"), "name": rel.get("name", rel.get("id", ""))}
        for rel in related[:5]
    ]

    return {
        "master": master_data.get("name", master),
        "master_id": master_id,
        "topic": topic,
        "view": view,
        "source": f"{master_data.get('name', master)}公开言论和著作",
        "related_topics": related_topics,
    }


@rag_tools.tool()
def search_knowledge(query: str) -> list:
    """
    Search the investment knowledge base.

    Args:
        query: Search query (e.g., "价值投资", "周期")

    Returns:
        list: Matching knowledge entries
    """
    graph = get_graph_client()

    query_lower = query.lower()

    # Search concepts
    concept_results = []
    for node, data in graph.graph.nodes(data=True):
        if data.get("type") == "InvestmentConcept":
            name = data.get("name", "").lower()
            definition = data.get("definition", "").lower()
            origin = data.get("origin", "").lower()
            if query_lower in name or query_lower in definition or query_lower in origin:
                concept_results.append({
                    "id": node,
                    "type": "concept",
                    "name": data.get("name"),
                    "definition": data.get("definition", ""),
                    "origin": data.get("origin", ""),
                })

    # Search masters
    master_results = []
    for node, data in graph.graph.nodes(data=True):
        if data.get("type") == "InvestmentMaster":
            name = data.get("name", "").lower()
            methodology = data.get("methodology", "").lower()
            if query_lower in name or query_lower in methodology:
                master_results.append({
                    "id": node,
                    "type": "master",
                    "name": data.get("name"),
                    "name_en": data.get("name_en", ""),
                    "methodology": data.get("methodology", ""),
                    "core_principles": data.get("core_principles", []),
                })

    # Search relationships
    relation_results = []
    for src, tgt, data in graph.graph.edges(data=True):
        desc = data.get("description", "").lower()
        if query_lower in desc:
            relation_results.append({
                "id": f"{src}-{tgt}",
                "type": "relationship",
                "source": src,
                "target": tgt,
                "relation": data.get("relation"),
                "description": data.get("description"),
            })

    return concept_results + master_results + relation_results


# ======================== 研报工具 ========================

@rag_tools.tool()
def rag_search_reports(
    query: str,
    top_k: int = 5,
) -> dict:
    """搜索券商研报——基于语义向量检索。

    返回最近入库的券商研报摘要，包含机构、股票、行业、评级、盈利预测等信息。

    Args:
        query: 搜索关键词（如"宁德时代 业绩"、"保险 增长"、"半导体"）
        top_k: 返回结果数量，默认5

    Returns:
        {
            "query": str,
            "count": int,
            "results": [
                {
                    "info_code": str,
                    "title": str,
                    "org_name": str,
                    "stock_name": str,
                    "stock_code": str,
                    "industry_name": str,
                    "rating": str,
                    "rating_change": str,
                    "publish_date": str,
                    "text": str,
                    "distance": float,
                }
            ]
        }
    """
    vs = get_vector_store()
    results = vs.search_research(query, top_k=top_k)
    return {
        "query": query,
        "count": len(results),
        "results": results,
    }
