# RDF & Ontology Platform — API Reference

A REST API for uploading, managing, and querying RDF graphs and OWL/RDFS ontologies, with SPARQL execution and deductive reasoning support.

**Base path:** `/api/v1`

---

## Table of Contents

- [RDF Graphs](#rdf-graphs)
- [Ontologies](#ontologies)
- [SPARQL](#sparql)
- [Reasoning](#reasoning)
- [Error Responses](#error-responses)

---

## RDF Graphs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/rdf/stats` | Global statistics across all graphs |
| `GET` | `/rdf/files` | List all uploaded graphs |
| `GET` | `/rdf/{file_id}` | Get a graph by ID |
| `GET` | `/rdf/{file_id}/stats` | Per-graph statistics |
| `GET` | `/rdf/{file_id}/elements` | Get all subjects, predicates, and objects |
| `GET` | `/rdf/{file_id}/visualise` | Cytoscape-compatible element list |
| `POST` | `/rdf/upload` | Upload a new RDF graph |
| `DELETE` | `/rdf/{file_id}` | Delete a graph |

### POST `/rdf/upload`

**Request** — `multipart/form-data`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Human-readable label |
| `file` | file | Yes | RDF file (Turtle, N-Triples, RDF/XML, JSON-LD, …) |

**Response**

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique identifier |
| `name` | string | Provided label |
| `format` | string | Detected serialization format |
| `file_name` | string | Original file name |
| `file_size` | integer | Size in bytes |
| `triples_count` | integer | Number of parsed triples |
| `uploaded_at` | datetime | UTC upload timestamp |

### GET `/rdf/{file_id}/visualise`

| Query Param | Type | Default | Description |
|-------------|------|---------|-------------|
| `limit` | integer | `200` | Max triples to include; larger graphs are truncated |

**Response**

```json
{
  "meta": {
    "graph_id": "...",
    "name": "...",
    "node_count": 42,
    "edge_count": 38,
    "truncated": false
  },
  "elements": [ ... ]
}
```

---

## Ontologies

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ontology/stats` | Global statistics across all ontologies |
| `GET` | `/ontology/files` | List all uploaded ontologies |
| `GET` | `/ontology/{onto_id}` | Get an ontology by ID |
| `GET` | `/ontology/{onto_id}/stats` | Per-ontology statistics |
| `GET` | `/ontology/{onto_id}/owl` | OWL detail view (nodes + edges) |
| `GET` | `/ontology/{onto_id}/rdfs` | RDFS detail view (class hierarchy) |
| `POST` | `/ontology/upload` | Upload a new ontology |
| `DELETE` | `/ontology/{onto_id}` | Delete an ontology |

### POST `/ontology/upload`

**Request** — `multipart/form-data`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Human-readable label |
| `file` | file | Yes | Ontology file (OWL/RDF/XML, Turtle, etc.) |

**Response**

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique identifier |
| `format` | string | Detected type: `owl` or `rdfs` |
| `classes_count` | integer | Number of extracted classes |
| `properties_count` | integer | Number of extracted properties |
| `individuals_count` | integer | Number of extracted individuals |
| `uploaded_at` | datetime | UTC upload timestamp |

### GET `/ontology/{onto_id}/owl`

Returns a graph representation with **nodes** and **edges** for interactive visualization. Only available for OWL ontologies.

Each node includes: `id`, `label`, `type`, `comment`, `equivalent_classes`, `disjoint_classes`, `union_of`, `intersection_of`, `object_properties`, `data_properties`, `restrictions`, `individuals`, `individual_count`.

Each edge includes: `source`, `target`, `type` (`subClassOf` | `equivalentClass` | `disjointWith`).

### GET `/ontology/{onto_id}/rdfs`

Returns class hierarchy and namespace declarations. Only available for RDFS ontologies.

Each class includes: `uri`, `label`, `prefix_form`, `comment`, `parents`, `children`, `properties`.

---

## SPARQL

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/sparql/recent` | Last 10 executed queries |
| `GET` | `/sparql/schema` | Prefixes, classes, and properties for autocompletion |
| `GET` | `/sparql/export` | Export SELECT results as JSON, CSV, or XML |
| `POST` | `/sparql/select` | Execute a SELECT query |
| `POST` | `/sparql/ask` | Execute an ASK query |
| `POST` | `/sparql/describe` | Execute a DESCRIBE query |
| `POST` | `/sparql/construct` | Execute a CONSTRUCT query |
| `POST` | `/sparql/update` | Execute an UPDATE query (INSERT / DELETE) |
| `POST` | `/sparql/export/construct` | Export CONSTRUCT triples as a file |
| `POST` | `/sparql/generate-update` | Auto-generate an UPDATE query template |
| `DELETE` | `/sparql/{query_id}` | Delete a history entry |

### Query endpoints (SELECT, ASK, DESCRIBE, CONSTRUCT)

All four share the same request body:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `graph_id` | UUID | Yes | Target graph |
| `query` | string | Yes | SPARQL query string |

- **SELECT / DESCRIBE / CONSTRUCT** — response: `{ "result": [ [...], ... ] }` (array of string arrays)
- **ASK** — response: `{ "result": true | false }`

### POST `/sparql/update`

| Field | Type | Description |
|-------|------|-------------|
| `graph_id` | UUID | Target graph |
| `query` | string | SPARQL UPDATE statement |

**Response**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the update succeeded |
| `execution_time` | integer | Elapsed time in ms |
| `triples_before` | integer | Triple count before the update |
| `triples_after` | integer | Triple count after the update |
| `triples_added` | integer | Net triples inserted |
| `triples_removed` | integer | Net triples deleted |

### GET `/sparql/export`

| Query Param | Type | Required | Description |
|-------------|------|----------|-------------|
| `graph_id` | UUID | Yes | Target graph |
| `query` | string | Yes | URL-encoded SPARQL SELECT query |
| `format` | string | No | `json` (default), `csv`, or `xml` |

Returns a downloadable file.

### POST `/sparql/generate-update`

| Field | Type | Description |
|-------|------|-------------|
| `graph_id` | UUID | Target graph |
| `mode` | string | `insert` → INSERT DATA template, `delete` → DELETE DATA template, other → DELETE WHERE template |

---

## Reasoning

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/reasoning/run` | Apply deductive closure and return inferred triples |

### Supported formalisms

| Value | Description |
|-------|-------------|
| `RDFS` | Standard RDF Schema entailment |
| `OWL-RL` | OWL 2 RL profile rule-based reasoning |
| `RDFS+OWL-RL` | Combined RDFS and OWL-RL entailment |

### POST `/reasoning/run`

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `graph_id` | UUID | Yes | Base RDF graph to reason over |
| `ontology_ids` | UUID[] | No | Ontologies to merge in before reasoning |
| `formalism` | string | Yes | `RDFS`, `OWL-RL`, or `RDFS+OWL-RL` |

**Response**

| Field | Type | Description |
|-------|------|-------------|
| `formalism` | string | Applied formalism |
| `graph_name` | string | Name of the base graph |
| `original_count` | integer | Triples before reasoning |
| `inferred_count` | integer | Newly inferred triples |
| `total_count` | integer | Combined total |
| `execution_time` | float | Duration in milliseconds |
| `subjects` | array | Inferred triples grouped by subject, sorted by count descending |

Each subject group contains `subject`, `label`, `prefix_form`, and a `triples` array. Each triple has `predicate`, `predicate_label`, `object`, `object_label`, and `object_type` (`uri` or `literal`).

---

## Error Responses

All errors return a JSON object with a `detail` field.

| Status | Meaning | Common Causes |
|--------|---------|---------------|
| `400` | Bad Request | Unsupported formalism, wrong ontology type for endpoint |
| `404` | Not Found | Unknown `graph_id`, `onto_id`, or `query_id` |
| `422` | Unprocessable Entity | File could not be parsed as valid RDF |
| `500` | Internal Server Error | Graph failed to load from disk, reasoning engine error |

```json
{ "detail": "Ontology not found." }
```