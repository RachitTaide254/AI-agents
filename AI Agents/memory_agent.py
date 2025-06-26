from typing import TypedDict,List, Union
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
import os
load_dotenv()


class AgentState(TypedDict):
    messages: List[Union[AIMessage,HumanMessage]]
    # messages_ai: List[AIMessage]


llm = ChatOpenAI(model='gpt-4o')
# print(llm)

def process_node(state:AgentState) -> AgentState :
    response = llm.invoke(state["messages"])
    state["messages"].append(AIMessage(content=response.content))
    print(f"\nAI:{response.content}")
    print('current state', state['messages'])
    return state

graph = StateGraph(AgentState)
graph.add_node("process",process_node)
graph.add_edge(START,'process')
graph.add_edge('process', END)

agent = graph.compile()

conversation_history = []

user_input = input("Enter :")
while user_input !='exit':
    conversation_history.append(HumanMessage(content=user_input))

    result = agent.invoke({"messages":conversation_history})

    # print(result['messages'])
    conversation_history = result['messages']
    user_input = input("Enter :")