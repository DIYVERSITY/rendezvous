from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class SearchRequest(BaseModel):
    query: str

class SearchResult(BaseModel):
    summary: str
    sources: list

@router.post("/invoke", response_model=SearchResult)
async def search_agent(req: SearchRequest):
    # TODO: implement business logic / external call / coral integration
    # Example: query agent, log action, return result
    return SearchResult(summary="Stubbed summary", sources=["http://test-source.com"])

@router.get("/metadata")
def metadata():
    return {
        "name": "search-agent",
        "version": "0.1",
        "capabilities": ["search"]
    }
