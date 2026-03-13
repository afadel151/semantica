# Semantica

> Desktop application for managing semantic web knowledge bases.

Semantica is a cross-platform desktop application that lets you upload, explore, query, and reason over RDF graphs and OWL/RDFS ontologies — all from a local GUI, with no external triplestore required.

> **Status:** Beta — core features are working but the API and data models may still change.

---

## Features

- **RDF Graph management** — upload Turtle, N-Triples, RDF/XML, and JSON-LD files; browse subjects, predicates, and objects; visualize graphs interactively
- **Ontology exploration** — parse OWL and RDFS ontologies; inspect class hierarchies, properties, restrictions, and individuals
- **SPARQL editor** — run SELECT, ASK, DESCRIBE, CONSTRUCT, and UPDATE queries with autocompletion; export results as JSON, CSV, or XML
- **Deductive reasoning** — apply RDFS, OWL-RL, or combined RDFS+OWL-RL closure and inspect inferred triples
- **Local-first** — everything runs on your machine; data is stored in a local SQLite database

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Desktop shell | [Tauri](https://tauri.app/) (Rust) |
| Frontend | [Vue.js](https://vuejs.org/) / [Nuxt](https://nuxt.com/) |
| Backend | [FastAPI](https://fastapi.tiangolo.com/) (Python) |
| Database | [SQLite](https://www.sqlite.org/) via [SQLModel](https://sqlmodel.tiangolo.com/) |

---

## Getting Started

### Prerequisites

See [docs/PRE-REQUISITES.md](docs/PRE-REQUISITES.md) for the full list of required runtimes and tools.

### Setup

```bash
git clone https://github.com/your-username/semantica.git
cd semantica
```

Then follow [docs/SETUP.md](docs/SETUP.md) to configure the backend and frontend.

### Development

See [docs/DEV.md](docs/DEV.md) to run the app in development mode.

### Build

See [docs/BUILD.md](docs/BUILD.md) to produce a distributable desktop binary.

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/PRE-REQUISITES.md](docs/PRE-REQUISITES.md) | Required runtimes, tools, and system dependencies |
| [docs/SETUP.md](docs/SETUP.md) | Installation and configuration instructions |
| [docs/DEV.md](docs/DEV.md) | Running the app locally in development mode |
| [docs/BUILD.md](docs/BUILD.md) | Building a production desktop binary with Tauri |
| [docs/API.md](docs/API.md) | REST API reference (endpoints, request/response schemas) |
| [docs/MODELS.md](docs/MODELS.md) | Database model reference (tables, columns, relationships) |

---
