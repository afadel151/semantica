import { ref } from 'vue';

export const useSparqlState = () => {
    // Shared State via useState for safety in Nuxt (SSR/CSR)
    const activeGraphId = useState('sparql_active_graph_id', () => null);

    const query = useState('sparql_query', () => `SELECT ?subject ?predicate ?object
WHERE {
  ?subject ?predicate ?object
}
LIMIT 25`);

    const results = useState('sparql_results', () => null);
    const history = useState('sparql_history', () => []);

    const isRunning = useState('sparql_is_running', () => false);
    const error = useState('sparql_error', () => null);

    return {
        activeGraphId,
        query,
        results,
        history,
        isRunning,
        error
    };
};

export const useSparqlActions = () => {
    const { activeGraphId, query, results, history, isRunning, error } = useSparqlState();
    const config = useRuntimeConfig();
    const apiUrl = config.public.apiBase || 'http://localhost:8000/api/v1'; // Ajustez si nécessaire

    // Initialiser le graphe actif (Prend le premier disponible)
    const initDefaultGraph = async () => {
        try {
            if (activeGraphId.value) return; // Déjà set
            const res = await $fetch(`${apiUrl}/rdf/files`);
            if (res && res.length > 0) {
                activeGraphId.value = res[0].id;
            } else {
                error.value = "Aucun graphe RDF trouvé sur le serveur. Veuillez en uploader un d'abord.";
            }
        } catch (err) {
            console.error("Failed to fetch graphs", err);
            error.value = "Erreur de connexion au serveur pour récupérer les graphes.";
        }
    };

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
        const cleaned = q.replace(/#.*$/gm, '').trim();
        const match = cleaned.match(/\b(SELECT|ASK|CONSTRUCT|DESCRIBE)\b/i);
        return match ? match[1].toUpperCase() : null;
    };

    // Exécuter la requête
    const runQuery = async () => {
        if (!query.value.trim() || isRunning.value) return;

        if (!activeGraphId.value) {
            error.value = "Aucun graphe sélectionné ou disponible pour exécuter la requête.";
            return;
        }

        isRunning.value = true;
        error.value = null;
        results.value = null;

        const type = detectQueryType(query.value) || 'SELECT'; // Fallback
        const endpointMap = {
            'SELECT': 'select',
            'ASK': 'ask',
            'CONSTRUCT': 'construct',
            'DESCRIBE': 'describe'
        };
        const endpoint = endpointMap[type] || 'select';

        const startTime = performance.now();

        try {
            const res = await $fetch(`${apiUrl}/sparql/${endpoint}`, {
                method: 'POST',
                body: {
                    query: query.value,
                    graph_id: activeGraphId.value
                }
            });

            const execution_time = Math.round(performance.now() - startTime);

            // Formatage des résultats pour correspondre au composant RightPanel
            if (type === 'SELECT' || type === 'DESCRIBE') {
                const rawData = res.result || [];
                // On doit deviner les variables.
                const guessVarsMatch = query.value.match(/SELECT\s+(.*?)\s+WHERE/i);
                let vars = [];
                if (guessVarsMatch) {
                    vars = guessVarsMatch[1].trim().split(/\s+/).filter(v => v !== '*').map(v => v.replace('?', ''));
                }

                // Si on a fait un SELECT *, on utilise len(rawData[0])
                if (vars.length === 0 && rawData.length > 0) {
                    vars = rawData[0].map((_, i) => `col${i}`);
                }

                const rows = rawData.map((r) => {
                    let obj = {};
                    vars.forEach((v, i) => obj[v] = r[i]);
                    return obj;
                });

                results.value = {
                    type: 'SELECT',
                    vars: vars,
                    rows: rows,
                    execution_time
                };
            } else if (type === 'ASK') {
                results.value = {
                    type: 'ASK',
                    result: res.result ? 'TRUE' : 'FALSE',
                    execution_time
                };
            } else if (type === 'CONSTRUCT') {
                // CONSTRUCT retourne des triplets. On doit les mapper pour Cytoscape
                const rawData = res.result || []; // form [[s, p, o], ...]
                const elements = [];
                const nodesSet = new Set();

                rawData.forEach((triple) => {
                    const [s, p, o] = triple;
                    if (!s || !p || !o) return;

                    // Source node
                    if (!nodesSet.has(s)) {
                        elements.push({ data: { id: s, label: s.split(/[/#]/).pop() || s, type: 'uri' } });
                        nodesSet.add(s);
                    }
                    // Target node
                    if (!nodesSet.has(o)) {
                        // determine if literal roughly (start with ")
                        const isLiteral = String(o).startsWith('"');
                        elements.push({ data: { id: o, label: o.split(/[/#]/).pop() || o, type: isLiteral ? 'literal' : 'uri' } });
                        nodesSet.add(o);
                    }
                    // Edge
                    elements.push({ data: { source: s, target: o, label: p.split(/[/#]/).pop() || p } });
                });

                results.value = {
                    type: 'CONSTRUCT',
                    triple_count: rawData.length,
                    elements: elements,
                    execution_time
                };
            }

            // Rafraichir l'historique après l'exec
            await fetchHistory();

        } catch (err) {
            console.error("Query Error:", err);
            error.value = err.data?.detail || err.message || "Erreur lors de l'exécution de la requête.";
        } finally {
            isRunning.value = false;
        }
    };

    const clearState = () => {
        query.value = '';
        results.value = null;
        error.value = null;
    };

    const loadFromHistory = (h) => {
        query.value = h.query;
    };

    // Fonction d'export
    const exportResultsFormat = (format) => {
        if (!activeGraphId.value || !query.value) return;
        const url = `${apiUrl}/sparql/export?format=${format}&graph_id=${activeGraphId.value}&query=${encodeURIComponent(query.value)}`;
        window.open(url, '_blank');
    }

    return {
        initDefaultGraph,
        fetchHistory,
        runQuery,
        detectQueryType,
        clearState,
        loadFromHistory,
        exportResultsFormat
    };
};
