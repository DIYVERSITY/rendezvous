
from typing import Any, Dict, List


import requests

class AgentBase:
    name: str = "base-agent"
    version: str = "0.1"
    capabilities: List[str] = []
    url: str = None  # If set, agent is HTTP-based

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "capabilities": self.capabilities,
            "url": self.url
        }

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if self.url:
            # HTTP-based agent: POST to /run endpoint
            resp = requests.post(f"{self.url}/run", json=input_data, timeout=30)
            resp.raise_for_status()
            return resp.json()
        raise NotImplementedError("Local agent logic not implemented.")

class ExampleAgent(AgentBase):
    name = "example-agent"
    version = "0.1"
    capabilities = ["demo"]

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "result": f"Echo: {input_data.get('text', '')}",
            "confidence": 0.5,
            "explanation": "This is a demo agent."
        }


class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, AgentBase] = {}

    def register(self, agent: AgentBase):
        self._agents[agent.name] = agent

    def register_http(self, name: str, url: str, version: str = "0.1", capabilities: List[str] = []):
        agent = AgentBase()
        agent.name = name
        agent.url = url
        agent.version = version
        agent.capabilities = capabilities
        self.register(agent)

    def get(self, name: str) -> AgentBase:
        return self._agents[name]

    def all(self) -> List[AgentBase]:
        return list(self._agents.values())
