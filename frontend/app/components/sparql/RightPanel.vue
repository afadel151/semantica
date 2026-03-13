<script setup>
import { Download, Settings, Table2, Share2, ZoomIn, ZoomOut, Maximize2, RefreshCw } from 'lucide-vue-next';
import { useSparqlState, useSparqlActions } from '~/composables/useSparql';

const { results, error, isRunning: running } = useSparqlState();
const { exportResultsFormat } = useSparqlActions();

function exportResults(format) {
    exportResultsFormat(format);
}

import cytoscape from 'cytoscape';

// ─── View mode toggle ────────────────────────────────────────────────────────
const viewMode = ref('table');

watch(() => results.value, (val) => {
    if (val?.type === 'CONSTRUCT') viewMode.value = 'graph';
    else viewMode.value = 'table';
});

const showToggle = computed(() =>
    results.value?.type === 'SELECT' || results.value?.type === 'CONSTRUCT'
);

// ─── Cytoscape ───────────────────────────────────────────────────────────────
const graphContainer = ref(null);
let cyInstance = null;
const graphStats = ref({ nodes: 0, edges: 0 });
const hasCyInstance = ref(false);

// ─── Node type helpers (mirrors backend graph_to_cytoscape) ──────────────────
function getNodeType(val) {
    const s = String(val);
    if (s.startsWith('_:'))                            return 'blank';
    if (s.startsWith('http') || s.startsWith('urn:')) return 'uri';
    return 'literal';
}

function getNodeLabel(val) {
    const s = String(val);
    if (s.startsWith('_:')) return 'blank';
    return s.split(/[/#]/).pop() || s;
}

// ─── Build Cytoscape elements from SELECT rows ────────────────────────────────
function buildSelectElements(rows, vars) {
    const elements = [];
    const nodesSet = new Set();

    const sKey = vars.find(v => /^(subject|s)$/i.test(v));
    const pKey = vars.find(v => /^(predicate|p)$/i.test(v));
    const oKey = vars.find(v => /^(object|o)$/i.test(v));

    const addNode = (id) => {
        if (id == null || nodesSet.has(String(id))) return;
        const strId = String(id);
        elements.push({
            data: { id: strId, label: getNodeLabel(strId), type: getNodeType(strId) }
        });
        nodesSet.add(strId);
    };

    if (sKey && pKey && oKey) {
        rows.forEach((row, i) => {
            const s = row[sKey], p = row[pKey], o = row[oKey];
            if (!s || !p || !o) return;
            addNode(s); addNode(o);
            elements.push({
                data: { id: `e_${i}`, source: String(s), target: String(o), label: getNodeLabel(String(p)) }
            });
        });
    } else {
        rows.forEach((row, ri) => {
            vars.forEach((v, ci) => {
                const val = row[v];
                if (val != null) addNode(val);
                if (ci > 0) {
                    const prev = row[vars[ci - 1]];
                    if (prev != null && val != null)
                        elements.push({ data: { id: `e_${ri}_${ci}`, source: String(prev), target: String(val), label: v } });
                }
            });
        });
    }
    return elements;
}

// ─── Layout selector ─────────────────────────────────────────────────────────
const selectedLayout = ref('cose');
const layouts = [
    { value: 'cose',         label: 'Force-directed' },
    { value: 'circle',       label: 'Circle' },
    { value: 'grid',         label: 'Grid' },
    { value: 'breadthfirst', label: 'Tree' },
    { value: 'concentric',   label: 'Concentric' },
];

function applyLayout()  { cyInstance?.layout({ name: selectedLayout.value, padding: 40, animate: true }).run(); }
function zoomIn()       { cyInstance?.zoom(cyInstance.zoom() * 1.2); }
function zoomOut()      { cyInstance?.zoom(cyInstance.zoom() * 0.8); }
function fit()          { cyInstance?.fit(); }
function refreshGraph() { applyLayout(); }

// ─── initCytoscape — copie exacte de [id].vue ────────────────────────────────
function initCytoscape(elements) {
    if (!graphContainer.value) return;
    if (cyInstance) { cyInstance.destroy(); cyInstance = null; hasCyInstance.value = false; }

    cyInstance = cytoscape({
        container: graphContainer.value,
        elements,
        style: [
            {
                selector: 'node[type = "uri"]',
                style: {
                    'background-color': '#6366f1',
                    'label': 'data(label)',
                    'color': '#fff',
                    'font-size': '10px',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'width': '100px',
                    'height': '100px',
                }
            },
            {
                selector: 'node[type = "literal"]',
                style: {
                    'background-color': '#f59e0b',
                    'label': 'data(label)',
                    'color': '#fff',
                    'font-size': '9px',
                    'text-valign': 'center',
                    'shape': 'rectangle',
                    'width': '90px',
                    'height': '35px',
                }
            },
            {
                selector: 'node[type = "blank"]',
                style: {
                    'background-color': '#94a3b8',
                    'label': 'blank',
                    'color': '#fff',
                    'font-size': '9px',
                    'shape': 'diamond',
                    'width': '40px',
                    'height': '40px',
                }
            },
            {
                selector: 'node:selected',
                style: { 'border-width': 3, 'border-color': '#fff', 'border-opacity': 1 }
            },
            {
                selector: 'edge',
                style: {
                    'label': 'data(label)',
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle',
                    'font-size': '8px',
                    'line-color': '#94a3b8',
                    'target-arrow-color': '#94a3b8',
                    'text-background-color': '#ffffff',
                    'text-background-opacity': 1,
                    'text-background-padding': '2px',
                }
            },
            {
                selector: 'edge:selected',
                style: { 'line-color': '#6366f1', 'target-arrow-color': '#6366f1', 'font-weight': 'bold' }
            }
        ],
        layout: { name: selectedLayout.value, animate: true }
    });

    cyInstance.ready(() => {
        hasCyInstance.value = true;
        graphStats.value = {
            nodes: cyInstance.nodes().length,
            edges: cyInstance.edges().length,
        };
        // CRUCIAL : forcer Cytoscape à recalculer les dimensions après rendu
        cyInstance.resize();
        cyInstance.fit();
    });
}

// ─── Watcher principal ───────────────────────────────────────────────────────
watch(
    [() => results.value, () => viewMode.value, graphContainer],
    async ([val, mode, container]) => {
        await nextTick();
        if (!val || !container) return;

        setTimeout(() => {
            if (mode !== 'graph') {
                if (cyInstance) { cyInstance.destroy(); cyInstance = null; hasCyInstance.value = false; }
                return;
            }
            let elements;
            if (val.type === 'CONSTRUCT') {
                elements = val.elements;
            } else if (val.type === 'SELECT') {
                elements = buildSelectElements(val.rows, val.vars);
            } else {
                return;
            }
            initCytoscape(elements);
        }, 150);
    },
    { immediate: true }
);

onBeforeUnmount(() => {
    if (cyInstance) { cyInstance.destroy(); cyInstance = null; }
});

// ─── Helper URI court ─────────────────────────────────────────────────────────
function shortUri(val) {
    if (!val) return '—';
    return String(val).split(/[/#]/).pop() || String(val);
}
</script>

<template>
    <Card class="w-full h-fit rounded-xl justify-between flex flex-col overflow-hidden">

        <!-- Results Header -->
        <CardHeader class="flex flex-row items-center justify-between gap-2 flex-wrap">
            <CardTitle>Results</CardTitle>

            <div class="flex items-center gap-2 flex-wrap">
                <!-- Toggle Table / Graph -->
                <div v-if="showToggle && !running"
                    class="flex rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden text-xs">
                    <button
                        @click="viewMode = 'table'"
                        :class="[
                            'flex items-center gap-1.5 px-3 py-1.5 transition-colors',
                            viewMode === 'table'
                                ? 'bg-primary text-primary-foreground font-semibold'
                                : 'text-muted-foreground hover:bg-muted'
                        ]"
                    >
                        <Table2 class="w-3.5 h-3.5" /> Table
                    </button>
                    <button
                        @click="viewMode = 'graph'"
                        :class="[
                            'flex items-center gap-1.5 px-3 py-1.5 transition-colors',
                            viewMode === 'graph'
                                ? 'bg-primary text-primary-foreground font-semibold'
                                : 'text-muted-foreground hover:bg-muted'
                        ]"
                    >
                        <Share2 class="w-3.5 h-3.5" /> Graph
                    </button>
                </div>

                <!-- Export buttons -->
                <Button @click="exportResults('json')" size="sm">
                    <Download /> JSON
                </Button>
                <Button @click="exportResults('csv')" variant="outline" size="sm">
                    <Download /> CSV
                </Button>
                <Button @click="exportResults('xml')" variant="outline" size="sm">
                    <Download /> XML
                </Button>
            </div>
        </CardHeader>

        <!-- Results Body -->
        <CardContent class="overflow-auto w-full h-full p-2">

            <!-- Empty state -->
            <div v-if="!results && !running && !error"
                class="h-full flex flex-col items-center justify-center text-gray-300">
                <p class="text-4xl mb-3">🔍</p>
                <p class="text-sm font-medium">Run a query to see results</p>
                <p class="text-xs mt-1">Ctrl+Enter to run</p>
            </div>

            <!-- Loading -->
            <div v-if="running" class="h-full flex-col flex items-center justify-center">
                <Settings class="animate-spin" />
                <p class="text-sm">Executing query...</p>
            </div>

            <!-- Error -->
            <div v-if="error" class="h-full flex-col flex items-center justify-center">
                <p class="text-sm font-semibold text-red-600 mb-1">Query Error</p>
                <p class="text-xs text-red-500 font-mono whitespace-pre-wrap">{{ error }}</p>
            </div>

            <!-- ── SELECT → Table mode ── -->
            <div v-if="results?.type === 'SELECT' && !running && viewMode === 'table'" class="overflow-x-auto w-full">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="text-left text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide border-b border-gray-200 dark:border-gray-800">
                            <th v-for="v in results.vars" :key="v" class="pb-2 pr-4 font-medium whitespace-nowrap">?{{ v }}</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
                        <tr v-for="(row, i) in results.rows" :key="i" class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                            <td v-for="v in results.vars" :key="v" class="py-2 pr-4 text-xs font-mono whitespace-nowrap">
                                <span v-if="row[v] === undefined || row[v] === null" class="text-gray-400 dark:text-gray-600">—</span>
                                <span v-else-if="String(row[v]).startsWith('http') || String(row[v]).startsWith('urn:')" class="text-blue-600 dark:text-blue-400">
                                    &lt;{{ row[v] }}&gt;
                                </span>
                                <span v-else-if="!isNaN(Number(row[v])) && String(row[v]).trim() !== ''" class="text-emerald-600 dark:text-emerald-400">
                                    {{ row[v] }}
                                </span>
                                <span v-else class="text-amber-600 dark:text-amber-400">
                                    "{{ row[v] }}"
                                </span>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <p class="text-xs text-muted-foreground mt-2">{{ results.rows.length }} résultat(s) — {{ results.execution_time }}ms</p>
            </div>

            <!-- ── ASK → Boolean ── -->
            <div v-if="results?.type === 'ASK' && !running" class="h-full">
                <p class="text-2xl font-bold" :class="results.result === 'TRUE' ? 'text-green-600' : 'text-red-500'">
                    {{ results.result }}
                </p>
                <p class="text-primary">execution time: {{ results.execution_time }}ms</p>
            </div>

            <!-- ── CONSTRUCT → Table mode (S / P / O) ── -->
            <div v-if="results?.type === 'CONSTRUCT' && !running && viewMode === 'table'" class="overflow-x-auto w-full">
                <p class="text-xs text-muted-foreground mb-2">{{ results.triple_count }} triplet(s) — {{ results.execution_time }}ms</p>
                <table class="w-full text-sm">
                    <thead>
                        <tr class="text-left text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide border-b border-gray-200 dark:border-gray-800">
                            <th class="pb-2 pr-4 font-medium">Sujet</th>
                            <th class="pb-2 pr-4 font-medium">Prédicat</th>
                            <th class="pb-2 pr-4 font-medium">Objet</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
                        <tr v-for="(triple, i) in results.rawTriples" :key="i" class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                            <td class="py-1.5 pr-4 text-xs font-mono max-w-[220px] truncate">
                                <span class="text-blue-600 dark:text-blue-400" :title="triple[0]">&lt;{{ shortUri(triple[0]) }}&gt;</span>
                            </td>
                            <td class="py-1.5 pr-4 text-xs font-mono max-w-[180px] truncate">
                                <span class="text-violet-600 dark:text-violet-400" :title="triple[1]">{{ shortUri(triple[1]) }}</span>
                            </td>
                            <td class="py-1.5 pr-4 text-xs font-mono max-w-[220px] truncate">
                                <span v-if="String(triple[2]).startsWith('http') || String(triple[2]).startsWith('urn:')"
                                    class="text-blue-600 dark:text-blue-400" :title="triple[2]">&lt;{{ shortUri(triple[2]) }}&gt;</span>
                                <span v-else class="text-amber-600 dark:text-amber-400" :title="triple[2]">"{{ triple[2] }}"</span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- ── SELECT / CONSTRUCT → Graph mode (Cytoscape) ── -->
            <div
                v-if="!running && results && viewMode === 'graph' && (results.type === 'SELECT' || results.type === 'CONSTRUCT')"
                class="flex flex-col gap-2"
                style="min-height: 520px;"
            >
                <!-- Legend -->
                <div class="flex items-center gap-4 px-1 shrink-0">
                    <div class="flex items-center gap-1.5">
                        <span class="w-3 h-3 rounded-full bg-indigo-500 inline-block"></span>
                        <span class="text-xs text-muted-foreground">URI Resource</span>
                    </div>
                    <div class="flex items-center gap-1.5">
                        <span class="w-3 h-3 rounded bg-amber-400 inline-block"></span>
                        <span class="text-xs text-muted-foreground">Literal</span>
                    </div>
                    <div class="flex items-center gap-1.5">
                        <span class="w-3 h-3 rotate-45 bg-slate-400 inline-block"></span>
                        <span class="text-xs text-muted-foreground">Blank Node</span>
                    </div>
                </div>

                <!-- Graph canvas wrapper -->
                <div class="rounded-xl border overflow-hidden relative" style="height: 480px; width: 100%;">

                    <!-- Controls overlay -->
                    <div class="absolute top-2 right-2 z-10 flex items-center gap-2 bg-background/90 backdrop-blur-sm rounded-xl border px-3 py-2 shadow-sm">
                        <template v-if="hasCyInstance">
                            <Badge variant="secondary">{{ graphStats.nodes }} nodes</Badge>
                            <Badge variant="secondary">{{ graphStats.edges }} edges</Badge>
                        </template>
                        <Select v-model="selectedLayout" @update:model-value="applyLayout">
                            <SelectTrigger class="w-[140px] h-7 text-xs">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem v-for="l in layouts" :key="l.value" :value="l.value">
                                    {{ l.label }}
                                </SelectItem>
                            </SelectContent>
                        </Select>
                        <div class="flex gap-1">
                            <Button size="sm" variant="outline" class="h-7 w-7 p-0" @click="zoomIn">
                                <ZoomIn class="w-3.5 h-3.5" />
                            </Button>
                            <Button size="sm" variant="outline" class="h-7 w-7 p-0" @click="zoomOut">
                                <ZoomOut class="w-3.5 h-3.5" />
                            </Button>
                            <Button size="sm" variant="outline" class="h-7 w-7 p-0" @click="fit">
                                <Maximize2 class="w-3.5 h-3.5" />
                            </Button>
                            <Button size="sm" variant="outline" class="h-7 w-7 p-0" @click="refreshGraph">
                                <RefreshCw class="w-3.5 h-3.5" />
                            </Button>
                        </div>
                    </div>

                    <!-- Cytoscape canvas — hauteur explicite obligatoire -->
                    <div ref="graphContainer" style="width: 100%; height: 480px;"></div>

                </div>
            </div>

        </CardContent>
    </Card>
</template>