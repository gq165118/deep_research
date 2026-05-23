"""状态定义模块：声明多智能体工作流共享的 ResearchState 结构。"""

import operator
from typing import Annotated, List
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage


class ResearchState(TypedDict):
    """LangGraph 中所有节点共享的研究工作流状态。

    它不是单纯的“搜索状态”，而是贯穿意图识别、任务规划、双路检索、
    证据裁判、分析补搜、最终写作和记忆注入的全局状态对象。
    每个节点只读取自己需要的字段，并把新增结果写回这里，供后续节点继续使用。
    """

    # 请求与身份上下文
    query: str  # 用户原始问题
    user_id: str  # 当前用户 ID，用于记忆隔离和个性化上下文
    tenant_id: str  # 当前租户 ID，用于多租户数据隔离
    memory_context: str  # 进入图之前注入的跨会话记忆文本
    messages: Annotated[List[BaseMessage], operator.add]  # 各节点产生的消息记录，LangGraph 会追加合并

    # 意图识别与流程阶段
    intent: str  # Intent Router 输出的路由结果：direct 或 multiagent
    phase: str  # 当前流程阶段标记，主要用于调试和状态展示

    # Planner 输出的研究计划
    plan: str  # 规划节点输出的摘要文本或原始规划内容
    outline: list[dict]  # 报告大纲/章节规划，每项通常包含 section id、标题、描述、检索词等
    sub_questions: list[str]  # Planner 拆出的子问题
    research_questions: list[str]  # 研究问题集合，兼容扩展字段
    search_plan: list[dict]  # 首轮检索计划，Web Scout 和 Local Scout 会据此生成查询
    budget: dict  # 检索预算约束，例如最大轮数、最大来源数、token 或时间预算

    # 双路检索结果
    web_search: str  # Web Scout 对网络检索结果的摘要
    local_rag: str  # Local Scout 对本地知识库检索结果的摘要
    web_evidence: list[dict]  # 网络检索保留下来的结构化证据
    local_evidence: list[dict]  # 本地知识库检索保留下来的结构化证据

    # Evidence Judge 输出
    evidence_pool: list[dict]  # 经过裁判整合后的统一证据池
    deep_dive: str  # Evidence Judge 的综合判断摘要
    audit: str  # 证据审计摘要，兼容扩展字段
    audit_flags: list[dict]  # 低置信度、冲突、证据缺失等审计标记

    # Analyst 输出与反思补搜控制
    analysis: str  # Analyst 的分析摘要
    needs_more_research: bool  # 是否需要进入 Reflect 节点继续补搜
    missing_gaps: list[str]  # 当前证据无法覆盖的信息缺口
    supplementary_queries: list[dict]  # Reflect 根据缺口生成的补充检索计划
    findings: list[dict]  # 绑定证据来源的分析结论
    claim_map: list[dict]  # 结论与 source_id 的映射关系
    source_index: list[dict]  # 最终引用索引，Writer 只能引用这里存在的来源

    # 检索统计与可追踪日志
    web_retrieval_stats: dict  # 网络检索统计，例如查询数、原始结果数、保留数
    local_retrieval_stats: dict  # 本地检索统计，例如查询数、原始结果数、保留数
    web_search_trace: list[dict]  # 每轮网络检索的 query、section、命中和过滤记录
    local_rag_trace: list[dict]  # 每轮本地知识库检索的 query、section、命中和过滤记录

    # 输出内容
    code: str  # 预留给代码生成类节点的输出，目前研究报告主流程中很少使用
    draft: str  # 中间草稿或直接回答内容
    final: str  # 最终返回给用户的答案或研究报告

    # 迭代控制
    iteration: int  # 当前补搜轮次，Reflect 每运行一次会递增
    max_iterations: int  # 最大补搜轮次，用于防止反思补搜死循环


def create_initial_state(
    query: str,
    max_iterations: int,
    user_id: str,
    tenant_id: str,
    memory_context: str = "",
) -> ResearchState:
    return {
        "query": query,
        "user_id": user_id,
        "tenant_id": tenant_id,
        "memory_context": memory_context,
        "messages": [],
        "intent": "",
        "phase": "initialized",
        "plan": "",
        "outline": [],
        "sub_questions": [],
        "research_questions": [],
        "search_plan": [],
        "budget": {},
        "web_search": "",
        "local_rag": "",
        "web_evidence": [],
        "local_evidence": [],
        "evidence_pool": [],
        "deep_dive": "",
        "audit": "",
        "audit_flags": [],
        "analysis": "",
        "needs_more_research": False,
        "missing_gaps": [],
        "supplementary_queries": [],
        "findings": [],
        "claim_map": [],
        "source_index": [],
        "web_retrieval_stats": {},
        "local_retrieval_stats": {},
        "web_search_trace": [],
        "local_rag_trace": [],
        "code": "",
        "draft": "",
        "final": "",
        "iteration": 0,
        "max_iterations": max_iterations,
    }
