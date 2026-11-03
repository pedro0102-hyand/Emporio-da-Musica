import os
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
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
    consult_store_policies
]

DEFAULT_MODEL = os.getenv("LLM_MODEL", "gemini-3.8-flash").strip() or "gemini-3.8-flash"
DEFAULT_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.6"))

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def build_agent(model_name: str | None = None, temperature: float | None = None):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("⚠️ A variável GEMINI_API_KEY não foi encontrada nas variáveis de ambiente (.env).")

    resolved_model = (model_name or os.getenv("LLM_MODEL") or DEFAULT_MODEL).strip() or "gemini-3.8-flash"
    resolved_temperature = float(temperature if temperature is not None else os.getenv("LLM_TEMPERATURE", DEFAULT_TEMPERATURE))

    try:
        llm = ChatGoogleGenerativeAI(model=resolved_model, api_key=api_key, temperature=resolved_temperature)
    except Exception as exc:
        if resolved_model != "gemini-3.8-flash" and "NOT_FOUND" in str(exc):
            llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", api_key=api_key, temperature=resolved_temperature)
        else:
            raise

    llm_with_tools = llm.bind_tools(TOOLS)

    # Node function to call the model and generate a response
    def call_model(state: AgentState):
        messages = state["messages"]
        if not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    # Function to determine if the agent should continue or end the conversation
    def should_continue(state: AgentState):
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    # Build the workflow graph for the agent
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)      
    workflow.add_node("tools", ToolNode(TOOLS))
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue, ["tools", END])
    workflow.add_edge("tools", "agent")
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app