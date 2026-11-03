import os
from typing import TypedDict, Annotated, Sequence

from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from src.prompt import SYSTEM_PROMPT
from src.db_tools import search_products, get_order_status, get_customer_purchases
from src.rag_tools import consult_store_policies

# available tools for the agent
TOOLS = [
    search_products,
    get_order_status,
    get_customer_purchases,
    consult_store_policies,
]

DEFAULT_PROVIDER = (os.getenv("LLM_PROVIDER") or "groq").strip().lower()
DEFAULT_MODEL = (
    os.getenv("GROQ_MODEL")
    or os.getenv("LLM_MODEL")
    or "openai/gpt-oss-20b"
).strip() or "openai/gpt-oss-20b"
DEFAULT_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.6"))


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


def _build_llm(model_name: str | None, temperature: float):
    provider = (os.getenv("LLM_PROVIDER") or "groq").strip().lower()

    if provider != "groq":
        raise ValueError("⚠️ Apenas o provedor Groq é suportado neste projeto.")

    from langchain_groq import ChatGroq

    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise ValueError(
            "⚠️ A variável GROQ_API_KEY não foi encontrada no arquivo .env. "
            "Adicione sua chave da Groq para continuar."
        )

    supported_groq_models = ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "qwen/qwen3.8-27b"]
    resolved_model = (model_name or os.getenv("GROQ_MODEL") or os.getenv("LLM_MODEL") or DEFAULT_MODEL).strip() or "openai/gpt-oss-20b"

    candidates = [resolved_model]
    candidates.extend(candidate for candidate in supported_groq_models if candidate not in candidates)

    last_error = None
    for candidate in candidates:
        try:
            return ChatGroq(model=candidate, api_key=groq_key, temperature=temperature)
        except Exception as exc:
            last_error = exc
            if "model_not_found" not in str(exc).lower() and "404" not in str(exc).lower():
                raise

    raise last_error if last_error is not None else RuntimeError("⚠️ Não foi possível inicializar o provedor Groq.")


def build_agent(model_name: str | None = None, temperature: float | None = None):
    resolved_temperature = float(temperature if temperature is not None else os.getenv("LLM_TEMPERATURE", DEFAULT_TEMPERATURE))
    llm = _build_llm(model_name, resolved_temperature)
    llm_with_tools = llm.bind_tools(TOOLS)

    def call_model(state: AgentState):
        messages = state["messages"]
        if not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: AgentState):
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(TOOLS))
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue, ["tools", END])
    workflow.add_edge("tools", "agent")
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)

    return app