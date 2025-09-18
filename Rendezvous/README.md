# Rendezvous: 

## 1. File Structure
/project-root/
│
├── frontend/            # All UI/UX (Next.js, React, static assets, styles)
│   ├── components/      # React components, mind map, agent controls, etc.
│   ├── pages/           # Next.js page routes
│   ├── services/        # API helpers, websocket clients
│   └── public/          # Static assets
│
├── backend/             # Orchestrator, infra, persistence, FastAPI integrations
│   ├── app/             # Core orchestrator logic, services (FastAPI app here)
│   ├── db/              # Models, data access (MongoDB, Postgres, Redis etc.)
│   ├── infra/           # Docker, deployment, scripts
│   ├── api/             # Endpoints for agent orchestration, workflow mgmt.
│   └── utils/           # Shared backend helpers & tools
│
├── agents/              # All Coral agent logic, registration, protocol adapters
│   ├── coral/           # Coral agent SDK/client, protocol registration logic
│   ├── registry/        # Agent metadata/tasks, registration scripts
│   ├── fastapi_agents/  # Individual FastAPI services run as coralized agents
│   └── templates/       # Agent skeletons, common adapters
│
├── scripts/             # Global utility scripts, CLI tools
├── docs/                # Architectural docs, API specs, onboarding
├── .env                 # Root environment variables
├── README.md
└── LICENSE


## 2. Integration/Implementation Guidelines
### frontend/
Use for all user-facing features: workflow visualization, status, agent logs/history, live controls for interject/pause.

Connect via REST/WebSocket to backend for workflow status and to agents (if you expose direct endpoints).

### backend/
Houses the API orchestrator (FastAPI), connects UI to agent workflow, logs sessions, coordinates state.

Manage all things infrastructure here: database, auth, deployment scripts.

FastAPI endpoints serve:

Workflow initiation and management

Persisting/retrieving logs and workflow records

Proxying agent/status info to the UI

### agents/
Everything “agent-side” and protocol-specific (Coral SDK/adapter).

Register agents in the Coral registry, define agent messaging logic, and where appropriate, launch coralized FastAPI agent services.

Use coral/ for protocol core code, fastapi_agents/ for service implementations, and registry/ for registration/metadata handling.



## 3. Next Steps to Build
Initiate Next.js in /frontend/ and start stubbing UI.

Build core orchestrator API and FastAPI entrypoint in backend/.

Start with a search-agent and summarize-agent in agents/fastapi_agents/.

Scaffold workflows in /backend/app, register/test agents via /agents/registry/.

Use Docker Compose (in /backend/infra/) to spin everything up for local dev.

A. Coral Protocol Setup
Deploy or connect to a running Coral MPC instance (locally or in cloud).

Use the Coral UI for agent registry and workflow monitoring during dev.

Familiarize with agent registration and session/workflow creation via the Coral API.

B. Agent (FastAPI) Best Practices
Each agent is a Python FastAPI microservice:

/metadata endpoint (GET): agent’s capabilities, description, version.

/invoke endpoint (POST): receives tasks (e.g., search, summarize), returns results as JSON.

Modularize agent logic for easy enhancement and independent debugging.

Add agent healthcheck endpoints for MCP readiness checks.

C. Frontend (Next.js) Best Practices
Structure pages as views (sessions, workflow detail, logs, mind map, registry).

Use services/helpers for Coral API and agent registry calls.

Implement WebSocket/live polling for agent and workflow updates.

Design modular React components for mind map nodes, agent status, and workflow controls.

Provide user actions for:

Starting workflows

Pausing/stepping workflows

Viewing and sending feedback at any node/step

D. Orchestration & Dev Flow
Use Docker Compose for local development with Coral, frontend, agents, and DB.

Use environment variables for all service endpoints and secrets.

Maintain a scripts/ folder for local setup, agent registration, and database resets.

4. Coding/Development Guidelines
Modularity: Keep agents, orchestrator, and frontend logic loosely coupled for independent testing and scaling.

Observability: Log all decisions, messages, and workflow states (use Mongo/Redis/Postgres as needed).

Security: Use API authentication (tokens/DIDs) for agent calls. Secure the registry UI for admin-only actions.

Documentation: Document each agent’s API, expected input/output, and registration steps (put docs in /docs).

Testing: Unit test each agent endpoint. Add smoke tests for end-to-end workflow execution in dev.

## Tech Stack
* Coral Protocol SDK & CLI
* FastAPI (Python)
* Next.js (Typescript)
* D3.js
* HTTPx/requests (agent backend calls)
* MongoDB/Redis (persistence, optional)
* Docker Compose
* Firecrawler

# Key Milestones to Track (see earlier roadmap)
Coral protocol up and basic agents registered

Get prompt → agent workflow → UI visualization working end-to-end

Mind map and user interjection implemented

Agent negotiation and consensus demoed with audit logs