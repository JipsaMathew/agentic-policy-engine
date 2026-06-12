from fastapi import FastAPI
from pydantic import BaseModel
from agent import agent_app
from langgraph.checkpoint.memory import MemorySaver

app = FastAPI()

class QueryRequest(BaseModel):
    thread_id: str
    question: str

class ApprovalRequest(BaseModel):
    thread_id: str
    approved: bool


@app.post("/ask")
async def ask(req: QueryRequest):
    # ... initial setup ...
    # Run the graph
    result = agent_app.invoke(initial_state, config=config)

    # Check if we stopped at the approver node
    if is_critical(req.question) and not result.get("human_approved"):
        return {"status": "paused", "message": "Critical query: Awaiting human approval."}

    return {"status": "complete", "result": result["research_answers"]}


@app.post("/start_query")
async def start_query(req: QueryRequest):
    config = {"configurable": {"thread_id": req.thread_id}}
    initial_state = {"input_question": req.question, "sub_questions": [], "research_answers": [],
                     "human_approved": False, "llm_call_count": 0}

    try:
        # Run the agent
        result = agent_app.invoke(initial_state, config=config)
        return {"status": "complete", "result": result["research_answers"]}

    except ValueError as e:
        # Only treat as paused if it specifically mentions HIL
        if "Human intervention required" in str(e):
            return {"status": "paused"}
        raise e

@app.post("/approve")
async def approve(req: ApprovalRequest):
    config = {"configurable": {"thread_id": req.thread_id}}
    agent_app.update_state(config, {"human_approved": req.approved})
    result = agent_app.invoke(None, config=config)
    return {"result": result["research_answers"]}