from .agent_base import AgentBase
from typing import Dict, Any

class CandidateAgent(AgentBase):
    name = "candidate-agent"
    version = "0.1"
    capabilities = ["candidate-generation"]

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Example: generate two candidate options
        query = input_data.get("query", "")
        return {
            "candidates": [
                {"option": f"Option 1 for {query}", "confidence": 0.8, "explanation": "First candidate."},
                {"option": f"Option 2 for {query}", "confidence": 0.6, "explanation": "Second candidate."}
            ]
        }