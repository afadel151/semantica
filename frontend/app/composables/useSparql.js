import { useActiveGraphStore } from "~/store/active_graph";

export const useSparqlState = () => {
  const activeGraphStore = useActiveGraphStore();
  const activeGraphId = computed(() => activeGraphStore.getId || null);
  const activeGraphName = computed(() => activeGraphStore.getName || null);

  const query = useState(
    "sparql_query",
    () => `SELECT ?subject ?predicate ?object
WHERE {
  ?subject ?predicate ?object
}
LIMIT 25`,
  );

  const results = useState("sparql_results", () => null);
  const history = useState("sparql_history", () => []);
  const isRunning = useState("sparql_is_running", () => false);
  const error = useState("sparql_error", () => null);

  // Nouvel état : résultat d'une requête UPDATE
  const updateResult = useState("sparql_update_result", () => null);

  // Nouvel état : schéma RDF pour l'autocomplétion
  const schema = useState("sparql_schema", () => ({
    prefixes: {},
    classes: [],
    properties: [],
    subjects: [],
    graph_size: 0,
  }));

  return {
    activeGraphId,
    activeGraphName,
    query,
    results,
    history,
    isRunning,
    error,
    updateResult,
    schema,
  };
};

export const useSparqlActions = () => {
  const { activeGraphId, query, results, history, isRunning, error, updateResult, schema } =
    useSparqlState();
  const config = useRuntimeConfig();
  const apiUrl = config.public.apiBase || "http://localhost:8000/api/v1";

  // ─── Historique ───────────────────────────────────────────────────────────
  const fetchHistory = async () => {
    try {
      const res = await $fetch(`${apiUrl}/sparql/recent`);
      history.value = res;
    } catch (err) {
      console.error("Failed to fetch history", err);
    }
  };

  // ─── Détecter le type de requête ──────────────────────────────────────────
  const detectQueryType = (q) => {
    if (!q) return null;
    const cleaned = q.replace(/#.*$/gm, "").trim();
    const match = cleaned.match(/\b(SELECT|ASK|CONSTRUCT|DESCRIBE|INSERT|DELETE)\b/i);
    return match ? match[1].toUpperCase() : null;
  };

  // ─── Charger le schéma RDF pour l'autocomplétion ─────────────────────────
  const fetchSchema = async (graphId) => {
    if (!graphId) return;
    try {
      const res = await $fetch(`${apiUrl}/sparql/schema?graph_id=${graphId}`);
      schema.value = res;
    } catch (err) {
      console.error("Failed to fetch schema", err);
    }
  };

  // ─── Exécuter requête SELECT / ASK / CONSTRUCT / DESCRIBE ────────────────
  const runQuery = async () => {
    if (!query.value.trim() || isRunning.value) return;

    if (!activeGraphId.value) {
      error.value =
        "⚠️ Aucun graphe actif. Rendez-vous dans Graphs → ouvrez un graphe → cliquez « Set as Active » avant d'exécuter une requête.";
      return;
    }

    const type = detectQueryType(query.value) || "SELECT";

    // Si c'est une requête UPDATE, déléguer à runUpdateQuery
    if (type === "INSERT" || type === "DELETE") {
      await runUpdateQuery(query.value);
      return;
    }

    isRunning.value = true;
    error.value = null;
    results.value = null;
    updateResult.value = null;

    const startTime = performance.now();

    try {
      // ✅ All query types go through the unified /select endpoint
      const res = await $fetch(`${apiUrl}/sparql/select`, {
        method: "POST",
        body: {
          query: query.value,
          graph_id: activeGraphId.value,
        },
      });

      const execution_time = Math.round(performance.now() - startTime);
      const responseType = res.type || type;

      if (responseType === "ASK") {
        results.value = {
          type: "ASK",
          result: res.boolean ? "TRUE" : "FALSE",
          execution_time,
          graph_size: schema.value?.graph_size || 0,
        };

      } else if (responseType === "CONSTRUCT" || responseType === "DESCRIBE") {
        const rawData = res.rows || [];
        const elements = [];
        const nodesSet = new Set();
        rawData.forEach((triple) => {
          const [s, p, o] = triple;
          if (!s || !p || !o) return;
          if (!nodesSet.has(s)) {
            elements.push({ data: { id: s, label: s.split(/[/#]/).pop() || s, type: "uri" } });
            nodesSet.add(s);
          }
          if (!nodesSet.has(o)) {
            const isLiteral = !String(o).startsWith("http") && !String(o).startsWith("urn:");
            elements.push({ data: { id: o, label: o.split(/[/#]/).pop() || o, type: isLiteral ? "literal" : "uri" } });
            nodesSet.add(o);
          }
          elements.push({ data: { source: s, target: o, label: p.split(/[/#]/).pop() || p } });
        });
        results.value = {
          type: responseType,
          triple_count: rawData.length,
          elements,
          rawTriples: rawData,
          graph_ttl: res.graph_ttl || null,
          execution_time,
          graph_size: schema.value?.graph_size || 0,
        };

      } else {
        // SELECT (default)
        const headers = res.headers || [];
        const rows = (res.rows || []).map((r) => {
          const obj = {};
          headers.forEach((h, i) => (obj[h] = r[i] ?? ""));
          return obj;
        });
        results.value = {
          type: "SELECT",
          vars: headers,
          rows,
          execution_time,
          graph_size: schema.value?.graph_size || 0,
        };
      }

      await fetchHistory();
    } catch (err) {
      console.error("Query Error:", err);
      error.value =
        err.data?.detail ||
        err.message ||
        "Erreur lors de l'exécution de la requête.";
    } finally {
      isRunning.value = false;
    }
  };

  // ─── Exécuter requête UPDATE (INSERT/DELETE) ──────────────────────────────
  const runUpdateQuery = async (queryText) => {
    if (!activeGraphId.value) {
      error.value = "⚠️ Aucun graphe actif.";
      return;
    }

    isRunning.value = true;
    error.value = null;
    results.value = null;
    updateResult.value = null;

    try {
      const res = await $fetch(`${apiUrl}/sparql/update`, {
        method: "POST",
        body: {
          query: queryText || query.value,
          graph_id: activeGraphId.value,
        },
      });
      updateResult.value = res;
      // Rafraîchir le schéma après modification du graphe
      await fetchSchema(activeGraphId.value);
      await fetchHistory();
    } catch (err) {
      console.error("UPDATE Error:", err);
      error.value = err.data?.detail || err.message || "Erreur UPDATE.";
    } finally {
      isRunning.value = false;
    }
  };

  // ─── Générer automatiquement une requête UPDATE ───────────────────────────
  const generateUpdate = async (mode) => {
    if (!activeGraphId.value) {
      error.value = "⚠️ Aucun graphe actif.";
      return;
    }
    try {
      const res = await $fetch(`${apiUrl}/sparql/generate-update`, {
        method: "POST",
        body: {
          graph_id: activeGraphId.value,
          mode,
        },
      });
      query.value = res.query;
    } catch (err) {
      console.error("Generate error:", err);
      error.value = err.data?.detail || "Erreur lors de la génération.";
    }
  };

  const clearState = () => {
    query.value = "";
    results.value = null;
    error.value = null;
    updateResult.value = null;
  };

  const loadFromHistory = (h) => {
    query.value = h.query;
  };

  const exportResultsFormat = (format) => {
    if (!activeGraphId.value || !query.value) return;

    if (results.value?.type === "CONSTRUCT") {
      fetch(`${apiUrl}/sparql/export/construct?format=${format}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ triples: results.value.rawTriples }),
      })
        .then((r) => r.blob())
        .then((blob) => {
          const a = document.createElement("a");
          a.href = URL.createObjectURL(blob);
          a.download = `construct.${format}`;
          a.click();
          URL.revokeObjectURL(a.href);
        });
      return;
    }

    const url = `${apiUrl}/sparql/export?format=${format}&graph_id=${activeGraphId.value}&query=${encodeURIComponent(query.value)}`;
    window.open(url, "_blank");
  };

  return {
    fetchHistory,
    fetchSchema,
    runQuery,
    runUpdateQuery,
    generateUpdate,
    detectQueryType,
    clearState,
    loadFromHistory,
    exportResultsFormat,
  };
};
