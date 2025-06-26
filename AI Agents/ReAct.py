from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

@tool
def add(a:int,b:int):
    """This is an addition function that adds two numbers together"""

    return a + b

tools = [add]

model = ChatOpenAI(model="gpt-4o").bind_tools(tools)

def model_call(state:AgentState)-> AgentState:
    system_prompt = SystemMessage(content=
                            "You are my AI assistant, please anwser my queries to the best of your ability")

    response = model.invoke([system_prompt]+state["messages"])
    return {"messages":[response]}

def should_continue(state:AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    # print(last_message,'aasss')
    if not last_message.tool_calls:
        return 'end'
    else:
        return 'continue'
    
graph = StateGraph(AgentState)
graph.add_node("our_agent",model_call)

tool_node = ToolNode(tools=tools)
graph.add_node("tools",tool_node)

graph.set_entry_point('our_agent')

graph.add_conditional_edges(
    "our_agent",
    should_continue,
    {
        "continue":"tools",
        "end":END
    }
)

graph.add_edge("tools","our_agent")

app = graph.compile()

res = app.invoke({"messages":[("user","Add 4+9")]})
print(res['messages'][3])
# print(len(res['messages']))