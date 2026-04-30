from typing import Literal, Sequence,Annotated
from typing_extensions import TypedDict
from langgraph.graph import START, StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver


class SupervisorState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next: str # next action agent


@tool
def check_system_state(component: str) -> str:
    """Check the current system state relevant to the specified component."""
    # Placeholder implementation; in a real system, this would query the actual state.
    status = {"database": "normal", "server": "load over", "api": "normal"}  # Possible values: "operational", "degraded", "down"
    return SupervisorState(messages=[], next="agent_manager")

@tool
def get_product_info(product_name: str) -> str:
    """Fetch product information from the database."""
    products = {"basic" : "Basic Product: A simple product with essential features.",
                "premium" : "Premium Product: An advanced product with additional features and support."
    }

    return products.get(product_name, "Product not found.")

@tool
def query_invoice(order_id: str) -> str:
    """Query invoice details for a given order ID."""
    invoices = {"12345": "Invoice 12345: $100, due in 30 days.",
                "67890": "Invoice 67890: $250, due in 15 days."}

    return invoices.get(order_id, "Invoice not found.")

def tech_agent_node(state):

    last_message = state["messages"][-1].content

    if "database" in last_message or "server" in last_message:
        result = check_system_state.invoke({"component": "database"})
        response = f"[Tech support] system state: {result}"
    else:
        response = "[Tech support] Please specify which component you want to check (e.g., database, server, api)."

    return {"messages": [AIMessage(content=response)]}

def sales_agent_node(state):

    last_message = state["messages"][-1].content

    product = None

    if product in ["basic","premium"]:
       if product in last_message:
           result = get_product_info.invoke({"product_name": product})
           return {"messages": [AIMessage(content=f"[sales consultant]  {result}")]}

    return {"messages": [AIMessage(content="[sales consultant] We have two products: basic and premium. Which one are you interested in?")]}

def billing_agent_node(state):

    return {"messages": [AIMessage(content="[Invoice] Please provide your order ID to query the invoice details.")]}

def supervisor_node(state):
    
    last_message = state["messages"][-1].content

    tech_keywords = ["error", "bug", "system", "database", "server", "api", "issue", "problem", "fail", "slow"]
    sales_keywords = ["price", "cost", "product", "feature", "buy", "purchase", "upgrade", "downgrade"]
    billing_keywords = ["invoice", "bill", "payment", "due", "charge", "refund"]

    if any(keyword in last_message for keyword in tech_keywords):
        next_agent = "tech_support"
    elif any(keyword in last_message for keyword in sales_keywords):
        next_agent = "sales"
    elif any(keyword in last_message for keyword in billing_keywords):
        next_agent = "billing"
    else:
        next_agent = "sales"

    return {"next": next_agent}

def route_after_supervisor(state) -> Literal["tech_support", "sales", "billing"]:
    return state["next"]

workflow = StateGraph(SupervisorState)

workflow.add_state("supervisor", supervisor_node)
workflow.add_state("tech_support", tech_agent_node)
workflow.add_state("sales", sales_agent_node)
workflow.add_state("billing", billing_agent_node)


workflow.add_edge(START, "supervisor")
workflow.add_conditional_edges("supervisor", route_after_supervisor,{
    "tech_support": "tech_support",
    "sales": "sales",
    "billing": "billing"
})

workflow.add_edge("tech_support", END)
workflow.add_edge("sales", END)
workflow.add_edge("billing", END)

memory = MemorySaver()
app = workflow.compile(
    checkpoint = memory,
    interrupt_before = ["supervisor"],
)

test_cases = [
    "Hi, I'm having an issue with my database connection.",
    "I want to know the price of your premium product.",
    "Can you help me with my invoice? My order ID is 12345."
]

for query in test_cases:
    print(f"User query: {query}")
    config = {"configurable": {"thread_id": "user_123"}}
    result = app.invoke({"messages": [HumanMessage(content=query)], "next": ""}, config=config)
    for msg in result["messages"]:
        if isinstance(msg, AIMessage):
            print(f"Agent response: {msg.content}")
    print("-" * 50)


