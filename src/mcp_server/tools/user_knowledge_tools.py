"""用户知识库 CRUD 工具 — user_knowledge_add/update/delete/list/search"""

import time
from mcp.server.fastmcp import FastMCP

from ..knowledge.vector_store import get_vector_store

# FastMCP 子实例，沿用项目工具组注册模式
user_knowledge_tools = FastMCP("user-knowledge-tools")


@user_knowledge_tools.tool()
def add(
    title: str,
    content: str,
    tags: list[str] = None,
    source_type: str = "insight",
) -> dict:
    """写入用户知识到知识库。

    支持 4 类来源：framework（投资框架）、journal（交易日志）、
    reading_notes（读书笔记）、insight（关键洞察，默认）。

    Args:
        title: 知识标题
        content: 正文内容（将用于语义搜索的 embedding）
        tags: 标签列表，如 ["framework:gold", "strategy:tactical"]
        source_type: 来源类型，可选 framework / journal / reading_notes / insight

    Returns:
        {id, title, status: "added"}
    """
    # 生成唯一 ID：uk_ 前缀 + 秒级时间戳
    knowledge_id = f"uk_{int(time.time())}"

    vs = get_vector_store()
    vs.add_user_knowledge(
        id=knowledge_id,
        title=title,
        content=content,
        tags=tags or [],
        source_type=source_type,
    )

    return {
        "id": knowledge_id,
        "title": title,
        "status": "added",
    }


@user_knowledge_tools.tool()
def update(
    id: str,
    content: str = None,
    title: str = None,
    tags: list[str] = None,
) -> dict:
    """更新已有用户知识条目。

    只传需要修改的字段，未传的字段保持不变。

    Args:
        id: 知识条目 ID（如 uk_1722000000）
        content: 新正文（可选）
        title: 新标题（可选）
        tags: 新标签列表（可选）

    Returns:
        {id, status: "updated", version}
    """
    vs = get_vector_store()
    updated_meta = vs.update_user_knowledge(
        id=id,
        content=content,
        title=title,
        tags=tags,
    )

    # 从 metadata 中推算版本号（updated_at 的 ISO 时间戳作为版本标识）
    version = updated_meta.get("updated_at", str(int(time.time())))

    return {
        "id": id,
        "status": "updated",
        "version": version,
    }


@user_knowledge_tools.tool()
def delete(id: str) -> dict:
    """从知识库中删除指定知识条目。

    Args:
        id: 知识条目 ID（如 uk_1722000000）

    Returns:
        {id, status: "deleted"}
    """
    vs = get_vector_store()
    vs.delete_user_knowledge(id)

    return {
        "id": id,
        "status": "deleted",
    }


@user_knowledge_tools.tool()
def list(
    source_type: str = None,
    tag: str = None,
    limit: int = 50,
) -> dict:
    """列出用户知识条目，可按来源类型或标签筛选。

    Args:
        source_type: 按来源类型过滤（framework / journal / reading_notes / insight）
        tag: 按标签过滤（如 "framework:gold"）
        limit: 返回条目数量上限，默认 50

    Returns:
        {count, items: [{id, title, tags, source_type, created_at}, ...]}
    """
    vs = get_vector_store()
    items = vs.list_user_knowledge(
        source_type=source_type,
        tag=tag,
        limit=limit,
    )

    return {
        "count": len(items),
        "items": items,
    }


@user_knowledge_tools.tool()
def search(query: str, top_k: int = 5) -> dict:
    """语义搜索用户知识库。

    基于向量相似度检索最相关的用户知识条目。

    Args:
        query: 搜索查询文本
        top_k: 返回结果数量，默认 5

    Returns:
        {query, results: [{id, title, snippet, tags, score, source_type, created_at}, ...]}
    """
    vs = get_vector_store()
    results = vs.search_user_knowledge(query, top_k=top_k)

    return {
        "query": query,
        "results": results,
    }
