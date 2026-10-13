# AI Incident Investigation Agent

An AI-powered backend service that investigates simulated production incidents using **Claude, FastAPI, Python, and tool calling**.

The agent analyzes service logs, metrics, deployment history, and health checks to identify likely root causes, distinguish evidence from speculation, and recommend remediation actions.

## Features

- **AI-powered incident investigation:** Uses Claude to analyze service incidents and generate investigation reports.
- **Agentic tool calling:** Claude dynamically selects diagnostic tools based on the incident description.
- **Structured responses:** Returns validated JSON reports using Pydantic.
- **Multiple incident scenarios:** Supports simulated checkout and authentication-service failures.
- **Bounded execution:** Limits the number of agent iterations to prevent indefinite tool-calling loops.
- **Automated testing:** Includes 11 pytest tests covering API behavior, agent execution, error handling, and simulated incidents.

## Tech Stack

- **Python** — Backend development
- **FastAPI** — REST API
- **Anthropic Claude API** — AI investigation and tool selection
- **Pydantic** — Request and response validation
- **pytest** — Automated testing
- **HTTPX / FastAPI TestClient** — API testing

## Architecture

```text
Client
   |
   v
FastAPI POST /investigate
   |
   v
Claude Investigation Agent
   |
   +----> search_logs()
   |
   +----> get_metric()
   |
   +----> get_recent_deployments()
   |
   +----> get_service_health()
   |
   v
Simulated Infrastructure Data
   |
   v
Claude analyzes diagnostic results
   |
   v
Structured IncidentReport (JSON)
```

The investigation workflow:

1. A client submits a service name and incident description.
2. FastAPI validates the request using Pydantic.
3. Claude selects diagnostic tools to investigate the incident.
4. Python executes the selected tools against simulated infrastructure data.
5. Tool results are returned to Claude for analysis.
6. Claude produces a structured incident report.
7. FastAPI validates and returns the report as JSON.

The agent can make multiple rounds of tool calls, up to a configured maximum of five iterations.

## Project Structure

```text
claude-incident-agent/
├── app/
│   ├── data/
│   │   ├── deployments.json
│   │   ├── logs.json
│   │   └── metrics.json
│   ├── __init__.py
│   ├── agent.py
│   ├── main.py
│   ├── models.py
│   └── tools.py
├── tests/
│   ├── test_agent.py
│   ├── test_auth_scenario.py
│   └── test_main.py
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/JosephTseng1/claude-incident-agent.git
cd claude-incident-agent
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn anthropic python-dotenv pytest httpx
```

### 4. Configure your Claude API key

Create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=your_api_key_here
```

Never commit your real API key to GitHub.

### 5. Start the API

```bash
uvicorn app.main:app --reload
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

## API Endpoints

### GET `/health`

Checks whether the API is running.

Example response:

```json
{
  "status": "ok"
}
```

### POST `/investigate`

Investigates a service incident using Claude and diagnostic tools.

Example request:

```json
{
  "service": "checkout",
  "description": "Checkout is returning HTTP 500 errors after a recent deployment."
}
```

Example response (abbreviated):

```json
{
  "severity": "high",
  "likely_root_cause": "A deployment reduced the database connection pool from 50 to 10, likely causing connection pool exhaustion.",
  "evidence": [
    "Checkout service health is unhealthy.",
    "Error rate is 18%.",
    "Logs report database connection pool exhaustion.",
    "Deployment v2.4.1 reduced the connection pool size."
  ],
  "recommended_actions": [
    "Roll back the deployment or restore the connection pool configuration.",
    "Monitor checkout error rates and connection pool utilization.",
    "Add deployment safeguards for connection pool configuration changes."
  ]
}
```

Responses are generated dynamically, so the exact wording may vary.

## Simulated Incident Scenarios

### Scenario 1: Checkout Service — Database Connection Pool Exhaustion

The checkout service experiences elevated HTTP 500 errors.

Simulated evidence includes:

- Database connection pool exhaustion errors
- 18% request error rate
- High database pool utilization
- Deployment `v2.4.1`, which reduced the connection pool from 50 to 10

The agent can use this evidence to identify a likely deployment-related database connection pool issue.

### Scenario 2: Authentication Service — Request Timeouts

The authentication service experiences login failures and elevated latency.

Simulated evidence includes:

- Authentication request timeout errors
- 12% request error rate
- Recent deployment `v1.8.0`
- A configuration change reducing the upstream authentication timeout from 5 seconds to 1 second

The agent can investigate the service and identify the timeout configuration as a likely contributor to the incident.

## Running Tests

Run the complete automated test suite:

```bash
python -m pytest -v
```

The project currently includes **11 passing tests**, covering:

- API health checks
- Successful incident investigations
- Request validation
- API error handling
- Claude tool-calling execution
- Invalid JSON handling
- Maximum investigation iteration limits
- Authentication-service logs, metrics, deployments, and health checks

Tests mock Claude API interactions where necessary, allowing automated tests to run without consuming Claude API credits.

## Design Decisions

**Separation of concerns:** FastAPI handles HTTP requests, the agent coordinates Claude tool calling, diagnostic tools retrieve infrastructure data, and Pydantic validates responses.

**Extensible diagnostic data:** Service-specific logs, metrics, and deployment information are stored in JSON files. New simulated services can be added without rewriting the investigation loop.

**Evidence-based analysis:** The agent is instructed to investigate using diagnostic evidence rather than rely solely on the incident description.

**Controlled execution:** A maximum-iteration limit prevents the agent from requesting diagnostic tools indefinitely.

## Limitations and Future Improvements

This is a portfolio demonstration using **simulated infrastructure data**, not a production monitoring integration.

Potential improvements include:

- Integration with real observability platforms
- Automatic discovery of available metric names
- Incident investigation history and persistence
- More comprehensive tool error handling
- Authentication and rate limiting for the API
- Deployment to a cloud hosting platform

## Repository

[GitHub — AI Incident Investigation Agent](https://github.com/JosephTseng1/claude-incident-agent)