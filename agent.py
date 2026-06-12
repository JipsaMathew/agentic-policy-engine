from typing import TypedDict, List
import re
from langgraph.graph import StateGraph, END
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from rag_engine import RagEngine
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

@st.cache_resource
def get_llm():
    # Retrieve the key from secrets
    api_key = st.secrets.get("GROQ_API_KEY")
    return ChatGroq(api_key=api_key, model="llama-3.3-70b-versatile", temperature=0.3)

# Use this to get your model instance throughout your app
llm = get_llm()

class AgentState(TypedDict):
    input_question: str
    sub_questions: List[str]
    research_answers: List[str]
    is_valid: bool
    human_approved: bool
    llm_call_count: int

rag_engine = RagEngine("gm.pdf")

# --- Nodes ---
def planning_node(state: AgentState):
    return {"sub_questions": [f"Details on: {state['input_question']}"], "llm_call_count": state.get("llm_call_count", 0) + 1}


def research_node(state: AgentState):
    context = rag_engine.retrieve(state["sub_questions"][0])
    prompt = ChatPromptTemplate.from_template(
        "Answer the question using only this context in exactly two short lines.\n"
        "Context: {context}\nQuestion: {question}"
    )
    response = (prompt | llm).invoke({"context": context, "question": state["input_question"]})

    # Extract raw text and ensure no list artifacts are present
    content = response.content.replace('"', '').strip("[]")

    # Store as a list because AgentState requires it,
    return {"research_answers": [content], "llm_call_count": state.get("llm_call_count", 0) + 1}

def human_approval_node(state: AgentState):
    if state.get("human_approved", False):
        return {"is_valid": True}
    raise ValueError("Human intervention required: Please review research results.")

def is_critical(question: str) -> bool:
    critical_keywords = [r"\bend my lease\b", r"\bearly\b", r"\btermination\b", r"\bpayoff\b", r"\bfraud\b", r"\bcancel\b"]
    return any(re.search(pattern, question.lower()) for pattern in critical_keywords)

def route_after_research(state: AgentState):
    if is_critical(state.get("input_question", "")):
        return "approver"
    return "end"

# --- Workflow ---
workflow = StateGraph(AgentState)
workflow.add_node("planner", planning_node)
workflow.add_node("researcher", research_node)
workflow.add_node("approver", human_approval_node)
workflow.set_entry_point("planner")
workflow.add_edge("planner", "researcher")
workflow.add_conditional_edges("researcher", route_after_research, {"approver": "approver", "end": END})
workflow.add_edge("approver", END)

# Use SqliteSaver for production/cloud environments
# Create the connection
conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)

# Create the saver
memory = SqliteSaver(conn)
agent_app = workflow.compile(checkpointer=memory)