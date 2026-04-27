# StayEase_Agent

## Project Structure

```bash
StayEase_Agent/
├── agent/
│   ├── __init__.py
│   ├── graph.py
│   ├── nodes.py
│   ├── state.py
│   └── tools.py
├── routers/
│   ├── __init__.py
│   └── chat.py
├── schemas.py
├── database.py
├── models.py
├── main.py
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── api.md
├── README.md

```

The project structure follows the MVC architectural pattern:

**Agent Layer** (Business Logic): Contains the core logic of the application, including the graph, nodes, state, and tools.

**Routers Layer** (Controller): Contains the API endpoints for the application.

**Schemas Layer** (Model): Contains the data models for the application.




