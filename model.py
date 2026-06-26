from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from typing import Literal
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from Shengchanlu import *
from vector_db import *
import os

class LLM:
    def __init__(self,llm="gemini",model="gemini-2.5-flash"):
    
        self.llm = ChatGoogleGenerativeAI(model= model,google_api_key=os.environ["GEMINI_TOKEN"])
        self.db = Database()

        self.tool_node = ToolNode([
            create_project,
            create_task_for_project,
            get_all_projects,
            get_project_task,
            update_project,
            update_task,
            self.db.search_memory,
            self.db.remember,
        ])
  
        self.llm = self.llm.bind_tools([
            create_project,
            create_task_for_project,
            get_all_projects,
            get_project_task,
            update_project,
            update_task,
            self.db.search_memory,
            self.db.remember
        ]
        )

        
        builder = StateGraph(MessagesState)
        builder.add_node("assistant",self.assistant)
        builder.add_node("tools",self.tool_node)
        builder.add_conditional_edges(
            "assistant",
            tools_condition,
            )
        builder.add_edge("tools", "assistant")
        builder.add_edge(START, "assistant")
        self.graph = builder.compile()

    def assistant(self,state: MessagesState):
        response = self.llm.invoke(state["messages"])
        return {"messages": [response]}


def main():
    model = LLM()
    print(model.graph.invoke({
    "messages": [
        HumanMessage(content="Create a project called AI Agent")
    ]
}))
    
if __name__ == "__main__":
    main()