import { useActiveGraphStore } from "~/store/active_graph";

export const useSparqlState = () => {
  // ── Graphe actif : on lit directement le store Pinia (source de vérité) ──
  // Le store est alimenté par la page /rdf/[id].vue via le bouton "Set as Active"
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

  return {
    activeGraphId,
    activeGraphName,
    query,
    results,
    history,
    isRunning,
    error,
  };
};

export const useSparqlActions = () => {
  const { activeGraphId, query, results, history, isRunning, error } =
    useSparqlState();
  const config = useRuntimeConfig();
  const apiUrl = config.public.apiBase || "http://localhost:8000/api/v1";

  // Charger l'historique récent
  const fetchHistory = async () => {
    try {
      const res = await $fetch(`${apiUrl}/sparql/recent`);
      history.value = res;
    } catch (err) {
      console.error("Failed to fetch history", err);
    }
  };

  // Détecter le type de la requête (SELECT, ASK, CONSTRUCT, DESCRIBE)
  const detectQueryType = (q) => {
    if (!q) return null;
    const cleaned = q.replace(/#.*$/gm, "").trim();
    const match = cleaned.match(/\b(SELECT|ASK|CONSTRUCT|DESCRIBE)\b/i);
    return match ? match[1].toUpperCase() : null;
  };

  // Exécuter la requête UNIQUEMENT sur le graphe actif
  const runQuery = async () => {
    if (!query.value.trim() || isRunning.value) return;

    // ── Vérification : graphe actif obligatoire ──────────────────────────────
    if (!activeGraphId.value) {
      error.value =
        "⚠️ Aucun graphe actif. Rendez-vous dans Graphs → ouvrez un graphe → cliquez « Set as Active » avant d'exécuter une requête.";
      return;
    }

    isRunning.value = true;
    error.value = null;
    results.value = null;

    const type = detectQueryType(query.value) || "SELECT";
    const endpointMap = {
      SELECT: "select",
      ASK: "ask",
      CONSTRUCT: "construct",
      DESCRIBE: "describe",
    };
    const endpoint = endpointMap[type] || "select";

    const startTime = performance.now();

    try {
      const res = await $fetch(`${apiUrl}/sparql/${endpoint}`, {
        method: "POST",
        body: {
          query: query.value,
          graph_id: activeGraphId.value, // ← toujours le graphe actif du store
        },
      });

      const execution_time = Math.round(performance.now() - startTime);

      if (type === "SELECT" || type === "DESCRIBE") {
        const rawData = res.result || [];
        const guessVarsMatch = query.value.match(/SELECT\s+(.*?)\s+WHERE/i);
        let vars = [];
        if (guessVarsMatch) {
          vars = guessVarsMatch[1]
            .trim()
            .split(/\s+/)
            .filter((v) => v !== "*")
            .map((v) => v.replace("?", ""));
        }
        if (vars.length === 0 && rawData.length > 0) {
          vars = rawData[0].map((_, i) => `col${i}`);
        }
        const rows = rawData.map((r) => {
          let obj = {};
          vars.forEach((v, i) => (obj[v] = r[i]));
          return obj;
        });
        results.value = { type: "SELECT", vars, rows, execution_time };

      } else if (type === "ASK") {
        results.value = {
          type: "ASK",
          result: res.result ? "TRUE" : "FALSE",
          execution_time,
        };

      } else if (type === "CONSTRUCT") {
        const rawData = res.result || [];
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
            const isLiteral = String(o).startsWith('"');
            elements.push({ data: { id: o, label: o.split(/[/#]/).pop() || o, type: isLiteral ? "literal" : "uri" } });
            nodesSet.add(o);
          }
          elements.push({ data: { source: s, target: o, label: p.split(/[/#]/).pop() || p } });
        });
        results.value = {
          type: "CONSTRUCT",
          triple_count: rawData.length,
          elements,
          rawTriples: rawData,
          execution_time,
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

  const clearState = () => {
    query.value = "";
    results.value = null;
    error.value = null;
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
    runQuery,
    detectQueryType,
    clearState,
    loadFromHistory,
    exportResultsFormat,
  };
};
