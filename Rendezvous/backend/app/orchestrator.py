
from typing import List, Dict, Any, Optional

from app.models.workflow import Workflow, WorkflowStep
from app.models.event import WorkflowEvent
from datetime import datetime

class Orchestrator:
	def __init__(self):
		# In-memory storage for demo; replace with DB in production
		self.workflows: Dict[str, Workflow] = {}
		self.events: Dict[str, List[WorkflowEvent]] = {}

	def record_event(self, event: WorkflowEvent):
		if event.workflow_id not in self.events:
			self.events[event.workflow_id] = []
		self.events[event.workflow_id].append(event)
		# Optionally update workflow state here

	def get_events(self, workflow_id: str) -> List[WorkflowEvent]:
		return self.events.get(workflow_id, [])

	def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
		return self.workflows.get(workflow_id)

	def create_workflow(self, workflow: Workflow):
		self.workflows[workflow.id] = workflow
		self.events[workflow.id] = []

	def replay_workflow(self, workflow_id: str) -> Workflow:
		# Reconstruct workflow state from events
		events = self.get_events(workflow_id)
		# For now, just return the stored workflow
		return self.get_workflow(workflow_id)

	def recommend(self, workflow_id: str, step_input: dict) -> dict:
		"""
		Call available agents, aggregate their responses, and re-rank options.
		This is a stub; in production, dynamically select and call agents.
		"""
		# Example: call two stub agents and aggregate
		agent_outputs = []
		# TODO: Replace with dynamic agent registry and async calls
		agent_outputs.append({
			"agent": "search-agent",
			"option": "Option A",
			"confidence": 0.7,
			"explanation": "Relevant to query"
		})
		agent_outputs.append({
			"agent": "summarize-agent",
			"option": "Option B",
			"confidence": 0.6,
			"explanation": "Alternative summary"
		})
		# Simple re-ranking by confidence
		ranked = sorted(agent_outputs, key=lambda x: x["confidence"], reverse=True)
		return {"candidates": ranked}
