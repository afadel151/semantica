# Database Models

Built with [SQLModel](https://sqlmodel.tiangolo.com/). The schema is organized around two core resources — **RDF Graphs** and **Ontologies** — with SPARQL history and reasoning results on top.

---

## Table of Contents

- [Ontology Models](#ontology-models)
- [RDF Graph Models](#rdf-graph-models)
- [SPARQL Models](#sparql-models)
- [Reasoning Models](#reasoning-models)
- [Junction Tables](#junction-tables)
- [Entity Relationship Overview](#entity-relationship-overview)

---

## Ontology Models

### `ontologies`

Stores uploaded OWL or RDFS ontology files.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID (PK) | Unique identifier |
| `name` | string | Human-readable label |
| `format` | string | Detected type: `owl` or `rdfs` |
| `file_name` | string | Original file name |
| `file_path` | string | Absolute path to stored file |
| `file_size` | integer | File size in bytes |
| `classes_count` | integer | Number of extracted classes (default `0`) |
| `properties_count` | integer | Number of extracted properties (default `0`) |
| `individuals_count` | integer | Number of extracted individuals (default `0`) |
| `uploaded_at` | datetime | UTC upload timestamp |

**Relationships**

- `classes` → list of `Class` (cascade delete)
- `properties` → list of `Property` (cascade delete)
- `individuals` → list of `Individual` (cascade delete)
- `sparql_queries` → list of `SparqlHistory` via `query_ontologies`

---

### `classes`

A class extracted from an ontology.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID (PK) | Unique identifier |
| `ontology_id` | UUID (FK → `ontologies.id`) | Parent ontology |
| `uri` | string | Full class URI |
| `label` | string? | `rdfs:label` value |
| `prefix_form` | string? | Prefixed QName (e.g. `owl:Thing`) |
| `parent_uri` | string? | URI of the parent class via `rdfs:subClassOf` |
| `children_count` | integer | Number of direct subclasses (default `0`) |
| `is_abstract` | boolean | Whether the class is abstract (default `false`) |
| `depth` | integer | Depth in the class hierarchy (default `0`) |

---

### `properties`

A property extracted from an ontology.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID (PK) | Unique identifier |
| `ontology_id` | UUID (FK → `ontologies.id`) | Parent ontology |
| `uri` | string | Full property URI |
| `label` | string? | `rdfs:label` value |
| `prefix_form` | string? | Prefixed QName |
| `type` | string? | `owl:ObjectProperty` or `owl:DatatypeProperty` |
| `domain` | string? | Domain class QName |
| `range` | string? | Range class or datatype QName |

---

### `individuals`

A named instance extracted from an ontology.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID (PK) | Unique identifier |
| `ontology_id` | UUID (FK → `ontologies.id`) | Parent ontology |
| `uri` | string | Full individual URI |
| `label` | string? | `rdfs:label` value |
| `prefix_form` | string? | Prefixed QName |
| `rdf_type` | string? | Class this individual belongs to |
| `property_count` | integer | Number of asserted properties (default `0`) |

---

## RDF Graph Models

### `graphs`

Stores uploaded RDF graph files.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID (PK) | Unique identifier |
| `name` | string | Human-readable label |
| `format` | string | Serialization format (e.g. `turtle`, `xml`) |
| `file_name` | string | Original file name |
| `file_path` | string | Absolute path to stored file |
| `file_size` | integer | File size in bytes |
| `triples_count` | integer | Total number of triples (default `0`) |
| `uploaded_at` | datetime | UTC upload timestamp |

**Relationships**

- `subjects` → list of `Subject` (cascade delete)
- `predicates` → list of `Predicate` (cascade delete)
- `objects` → list of `Object` (cascade delete)
- `sparql_history` → list of `SparqlHistory` (cascade delete)

---

### `subjects`

A subject URI found in a graph.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID (PK) | Unique identifier |
| `graph_id` | UUID (FK → `graphs.id`) | Parent graph |
| `uri` | string | Full subject URI |
| `prefix_form` | string? | Prefixed QName |
| `rdf_type` | string? | Value of `rdf:type` for this subject |
| `predicate_count` | integer | Number of predicates used by this subject (default `0`) |

---

### `predicates`

A predicate URI found in a graph.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID (PK) | Unique identifier |
| `graph_id` | UUID (FK → `graphs.id`) | Parent graph |
| `uri` | string | Full predicate URI |
| `prefix_form` | string? | Prefixed QName |
| `usage_count` | integer | Number of times this predicate appears (default `0`) |
| `domain` | string? | Inferred or declared domain |
| `range` | string? | Inferred or declared range |

---

### `objects`

An object value found in a graph (URI or literal).

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID (PK) | Unique identifier |
| `graph_id` | UUID (FK → `graphs.id`) | Parent graph |
| `value` | string | The object value (URI or literal string) |
| `kind` | string | `uri` or `literal` |
| `prefix_form` | string? | Prefixed QName (URI objects only) |
| `datatype` | string? | XSD datatype URI (literal objects only) |
| `language` | string? | Language tag (e.g. `en`, `fr`) |
| `referenced_by` | integer | Number of triples referencing this object (default `0`) |

---

## SPARQL Models

### `sparql_history`

A record of every executed SPARQL query.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID (PK) | Unique identifier |
| `query` | string | The full SPARQL query string |
| `query_type` | string | `SELECT`, `ASK`, `CONSTRUCT`, `DESCRIBE`, `INSERT`, or `DELETE` |
| `graph_id` | UUID (FK → `graphs.id`) | Graph the query ran against |
| `executed_at` | datetime | UTC execution timestamp |

**Relationships**

- `graph` → `Graph`
- `ontologies` → list of `Ontology` via `query_ontologies`

---

### Request / Response Schemas (non-table)

| Model | Description |
|-------|-------------|
| `SparqlQueryRequest` | `{ query: str, graph_id: UUID }` — body for SELECT / ASK / DESCRIBE / CONSTRUCT |
| `SparqlUpdateRequest` | `{ query: str, graph_id: UUID }` — body for UPDATE |
| `ConstructExportRequest` | `{ triples: list[list[str]] }` — body for CONSTRUCT export |
| `GenerateUpdateRequest` | `{ graph_id: UUID, mode: str }` — body for auto-generating UPDATE templates |

---

## Reasoning Models

### `reasoning_results`

Stores the outcome of a reasoning run.

| Column | Type | Description |
|--------|------|-------------|
| `id` | integer (PK) | Auto-incremented identifier |
| `graph_id` | integer? (FK → `graphs.id`) | Graph that was reasoned over |
| `ontology_id` | integer? (FK → `ontologies.id`) | Ontology used during reasoning |
| `reasoner` | string | Reasoner used: `pellet`, `hermit`, or `owlrl` |
| `inferred_triples` | integer | Number of triples inferred (default `0`) |
| `executed_at` | datetime | UTC execution timestamp |

---

## Junction Tables

### `query_ontologies`

Links SPARQL queries to the ontologies they reference.

| Column | Type | Description |
|--------|------|-------------|
| `query_id` | UUID (PK, FK → `sparql_history.id`) | Related query |
| `ontology_id` | UUID (PK, FK → `ontologies.id`) | Related ontology |

---

## Entity Relationship Overview

```
ontologies ──< classes
           ──< properties
           ──< individuals
           ──< query_ontologies >── sparql_history

graphs ──< subjects
       ──< predicates
       ──< objects
       ──< sparql_history

reasoning_results >── graphs
                  >── ontologies
```