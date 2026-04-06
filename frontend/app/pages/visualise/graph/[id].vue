<script setup lang="ts">
const route = useRoute()

import cytoscape from 'cytoscape'
import { Maximize2, RefreshCw, Settings, ZoomIn, ZoomOut } from 'lucide-vue-next'
import type { GraphMeta, VisualisationData } from '~/types/visualise'
const cyContainer = ref(null)
const loading = ref(false)
const error = ref<string | null>(null)
const graphMeta = ref<GraphMeta>({
    node_count:0,
    edge_count: 0,
    graph_id:'',
    name:'',
    truncated:false
})
let cyInstance: any = null

const selectedLayout = ref('cose')
const layouts = [
    { value: 'cose', label: 'Force-directed' },
    { value: 'circle', label: 'Circle' },
    { value: 'grid', label: 'Grid' },
    { value: 'breadthfirst', label: 'Tree' },
    { value: 'concentric', label: 'Concentric' },
]
const selectedNode = ref<any>(null)
const config = useRuntimeConfig()
async function loadGraph() {

    loading.value = true
    error.value = null
    selectedNode.value = null

    try {
        const { data, pending, error } = await useFetch<VisualisationData>(`${config.public.apiBase}/rdf/${route.params.id}/visualise`)
        if (data.value && data.value) {
            await nextTick()
            initCytoscape(data.value['elements'])
            console.log(data.value)
            graphMeta.value = data.value.meta
        }


    } catch (err: any) {
        error.value = err?.data?.detail ?? 'Failed to load graph'
    } finally {
        loading.value = false
    }
}

function initCytoscape(elements: any[]) {
    if (!cyContainer.value) return
    if (cyInstance) { cyInstance.destroy(); cyInstance = null }
    cyInstance = cytoscape({
        container: cyContainer.value,
        elements: elements,
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
                selector: 'node[type = "statement"]',
                style: {
                    'background-color': '#FFD700',
                    'label': 'data(label)',
                    'color': '#000',
                    'font-size': '10px',
                    'shape': 'diamond',
                    'width': '60px',
                    'height': '60px',
                }
            },
            {
                selector: 'node:selected',
                style: {
                    'border-width': 3,
                    'border-color': '#fff',
                    'border-opacity': 1,
                }
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
                selector: 'edge[type = "star_internal"]',
                style: {
                    'line-style': 'dashed',
                    'width': 2,
                    'opacity': 0.6
                }
            },
            {
                selector: 'edge:selected',
                style: {
                    'line-color': '#6366f1',
                    'target-arrow-color': '#6366f1',
                    'font-weight': 'bold',
                }
            }
        ],
        layout: { name: selectedLayout.value, animate: true }
    })

    // Click node → show detail panel
    // cyInstance.on('tap', 'node', (evt: any) => {
    //     selectedNode.value = evt.target.data()
    // })

    // // Click background → deselect
    // cyInstance.on('tap', (evt: any) => {
    //     if (evt.target === cyInstance) selectedNode.value = null
    // })
}

function applyLayout() {
    if (!cyInstance) return
    cyInstance.layout({ name: selectedLayout.value, padding: 40, animate: true }).run()
}

function zoomIn() { cyInstance?.zoom(cyInstance.zoom() * 1.2) }
function zoomOut() { cyInstance?.zoom(cyInstance.zoom() * 0.8) }
function fit() { cyInstance?.fit() }

onMounted(() => {
    loadGraph();
})
onBeforeUnmount(() => { cyInstance?.destroy() })
</script>


<template>
    <div class="p-2 relative space-y-2 h-full flex flex-col">

        <!-- HEADER -->


        <Card class="flex absolute flex-row  z-10 right-5 top-1 p-5  items-center gap-3">
            <!-- Stats -->
            <div v-if="graphMeta" class="flex gap-2">
                <Badge variant="secondary">{{ graphMeta.node_count }} nodes</Badge>
                <Badge variant="secondary">{{ graphMeta.edge_count }} edges</Badge>
                <Badge v-if="graphMeta.truncated" variant="outline" class="text-amber-600">
                    ⚠ Truncated to 200 triples
                </Badge>
            </div>

            <!-- Layout selector -->
            <Select v-model="selectedLayout" v-on:update:model-value="(value ) => {
                applyLayout()
            }"  >
                <SelectTrigger class="w-[180px]">
                    <SelectValue   />
                </SelectTrigger>
                <SelectContent>
                    <SelectItem v-for="l in layouts" :key="l.value" :value="l.value">
                        {{ l.label }}
                    </SelectItem>
                </SelectContent>
            </Select>

            <!-- Controls -->
            <div class="flex gap-1">
                <Button size="sm" variant="outline" @click="zoomIn">
                    <ZoomIn class="w-4 h-4" />
                </Button>
                <Button size="sm" variant="outline" @click="zoomOut">
                    <ZoomOut class="w-4 h-4" />
                </Button>
                <Button size="sm" variant="outline" @click="fit">
                    <Maximize2 class="w-4 h-4" />
                </Button>
                <Button size="sm" variant="outline" @click="loadGraph">
                    <RefreshCw class="w-4 h-4" />
                </Button>
            </div>
        </Card>

        <!-- LEGEND -->
        <div class="flex items-center gap-4 px-1 shrink-0">
            <div class="flex items-center gap-1.5">
                <span class="w-3 h-3 rounded-full bg-indigo-500"></span>
                <span class="text-xs text-muted-foreground">URI Resource</span>
            </div>
            <div class="flex items-center gap-1.5">
                <span class="w-3 h-3 rounded bg-amber-400"></span>
                <span class="text-xs text-muted-foreground">Literal</span>
            </div>
            <div class="flex items-center gap-1.5">
                <span class="w-3 h-3 rotate-45 bg-slate-400 inline-block"></span>
                <span class="text-xs text-muted-foreground">Blank Node</span>
            </div>
            <div class="flex items-center gap-1.5">
                <span class="w-3 h-3 rotate-45 bg-yellow-400 inline-block"></span>
                <span class="text-xs text-muted-foreground">Nested Statement</span>
            </div>
        </div>

        <!-- MAIN AREA -->
        <div class="flex gap-4 flex-1 min-h-0">

            <!-- CYTOSCAPE CANVAS -->
            <Card class="flex-1 overflow-hidden h-[91vh] relative">

                <!-- Loading overlay -->
                <div v-if="loading"
                    class="absolute inset-0 flex flex-col items-center justify-center bg-background/80 z-10">
                    <Settings class="w-8 h-8 animate-spin text-muted-foreground mb-2" />
                    <p class="text-sm text-muted-foreground">Loading graph...</p>
                </div>

                <!-- Error -->
                <div v-else-if="error" class="absolute inset-0 flex flex-col items-center justify-center z-10">
                    <p class="text-3xl mb-2">⚠️</p>
                    <p class="text-sm font-medium text-destructive">{{ error }}</p>
                    <Button size="sm" class="mt-3" @click="loadGraph">Retry</Button>
                </div>

                <!-- No active graph -->


                <!-- Graph canvas -->
                <div ref="cyContainer" class=" h-full" />
            </Card>

            <!-- NODE DETAIL PANEL -->


        </div>
    </div>
</template>