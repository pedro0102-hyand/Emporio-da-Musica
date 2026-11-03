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

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def build_agent(model_name: str = "gemini-1.5-flash", temperature: float = 0.6):
   
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("⚠️ A variável GEMINI_API_KEY não foi encontrada nas variáveis de ambiente (.env).")

   # build the LLM with tools
    llm = ChatGoogleGenerativeAI(model = model_name, api_key = api_key, temperature = temperature)
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