
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.memory import memory_manager

from app.orchestrator import Orchestrator
from app.models.event import WorkflowEvent
from app.models.workflow import Workflow
from app.agents.agent_base import AgentRegistry
from pydantic import BaseModel
from typing import Dict, Any
import os


router = APIRouter()
orchestrator = Orchestrator()
agent_registry = AgentRegistry()

# Register HTTP agents from environment variables
if os.getenv("AGENT_FIRECRAWL_URL"):
    agent_registry.register_http(
        name="firecrawl-agent",
        url=os.getenv("AGENT_FIRECRAWL_URL"),
        version="0.1",
        capabilities=["search", "crawl"]
    )
if os.getenv("AGENT_INTERFACE_URL"):
    agent_registry.register_http(
        name="interface-agent",
        url=os.getenv("AGENT_INTERFACE_URL"),
        version="0.1",
        capabilities=["interface"]
    )
if os.getenv("AGENT_ODR_URL"):
    agent_registry.register_http(
        name="odr-agent",
        url=os.getenv("AGENT_ODR_URL"),
        version="0.1",
        capabilities=["research"]
    )

router = APIRouter()


# --- Orchestrator Endpoints ---

class EventIn(BaseModel):
    workflow_id: str
    event_type: str
    step_id: str = None
    agent_id: str = None
    user_id: str = None
    payload: Dict[str, Any] = {}

@router.post("/workflow/{workflow_id}/event")
def record_event(workflow_id: str, event: EventIn):
    event_obj = WorkflowEvent(**event.dict())
    orchestrator.record_event(event_obj)
    return {"status": "ok"}

@router.get("/workflow/{workflow_id}/events")
def get_events(workflow_id: str):
    return orchestrator.get_events(workflow_id)

@router.get("/workflow/{workflow_id}/graph")
def get_workflow_graph(workflow_id: str):
    wf = orchestrator.get_workflow(workflow_id)
    if not wf:
        return {"error": "Workflow not found"}
    return wf

# --- WebSocket for Real-Time Updates ---
active_connections = {}

@router.websocket("/ws/workflow/{workflow_id}")
async def websocket_endpoint(websocket: WebSocket, workflow_id: str):
    await websocket.accept()
    if workflow_id not in active_connections:
        active_connections[workflow_id] = []
    active_connections[workflow_id].append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo for now; in real use, push updates on event
            await websocket.send_text(f"Received: {data}")
    except WebSocketDisconnect:
        active_connections[workflow_id].remove(websocket)



# --- Agent info and invoke endpoints for frontend ---
@router.get("/agents")
def list_agents():
    return [a.metadata() for a in agent_registry.all()]

class AgentInvokeIn(BaseModel):
    input: Dict[str, Any]

@router.post("/agents/{agent_name}/invoke")
def invoke_agent(agent_name: str, req: AgentInvokeIn):
    agent = agent_registry.get(agent_name)
    return agent.run(req.input)


# (Removed: legacy mock workflow endpoint. Use /workflow/{workflow_id}/graph instead.)