<script setup>
import { Download, Settings } from 'lucide-vue-next';

// Replace your results ref with this
const results = ref({
    type: 'CONSTRUCT',
    triple_count: 8,
    execution_time: 243,
    elements: [


        { data: { id: 'ex:John',         label: 'John',         type: 'uri'     } },
        { data: { id: 'ex:Jane',         label: 'Jane',         type: 'uri'     } },
        { data: { id: 'ex:ACME',         label: 'ACME Corp',    type: 'uri'     } },
        { data: { id: 'foaf:Person',     label: 'Person',       type: 'uri'     } },
        { data: { id: 'foaf:Organization', label: 'Organization', type: 'uri'   } },
        { data: { id: '"John Doe"',      label: 'John Doe',     type: 'literal' } },
        { data: { id: '"30"',            label: '30',           type: 'literal' } },

        { data: { source: 'ex:John',  target: 'foaf:Person',      label: 'rdf:type'   } },
        { data: { source: 'ex:Jane',  target: 'foaf:Person',      label: 'rdf:type'   } },
        { data: { source: 'ex:ACME',  target: 'foaf:Organization', label: 'rdf:type'  } },
        { data: { source: 'ex:John',  target: 'ex:Jane',           label: 'foaf:knows' } },
        { data: { source: 'ex:John',  target: 'ex:ACME',           label: 'foaf:member' } },
        { data: { source: 'ex:John',  target: '"John Doe"',        label: 'foaf:name'  } },
        { data: { source: 'ex:John',  target: '"30"',              label: 'foaf:age'   } },
        { data: { source: 'ex:Jane',  target: 'ex:ACME',           label: 'foaf:member' } },
    ]
})
const error = ref(null)
const running = ref(false)
const history = ref([])

import cytoscape from 'cytoscape'

const constructGraph = ref(null)
let cyInstance = null
watch(
    () => results.value,
    async (val) => {
        if (val?.type !== 'CONSTRUCT') return
        await nextTick()
        if (!constructGraph.value) return

        // destroy previous instance if any
        if (cyInstance) { cyInstance.destroy(); cyInstance = null }

        cyInstance = cytoscape({
            container: constructGraph.value,
            elements:  val.elements,
            style: [
                {
                    selector: 'node[type = "uri"]',
                    style: {
                        'background-color':  '#6366f1',
                        'label':             'data(label)',
                        'color':             '#fff',
                        'font-size':         '10px',
                        'text-valign':       'center',
                        'text-halign':       'center',
                        'width':             '60px',
                        'height':            '60px',
                    }
                },
                {
                    selector: 'node[type = "literal"]',
                    style: {
                        'background-color':  '#f59e0b',
                        'label':             'data(label)',
                        'color':             '#fff',
                        'font-size':         '9px',
                        'text-valign':       'center',
                        'shape':             'rectangle',
                        'width':             '70px',
                        'height':            '30px',
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'label':                  'data(label)',
                        'curve-style':            'bezier',
                        'target-arrow-shape':     'triangle',
                        'font-size':              '8px',
                        'line-color':             '#94a3b8',
                        'target-arrow-color':     '#94a3b8',
                        'text-background-color':  '#ffffff',
                        'text-background-opacity': 1,
                        'text-background-padding': '2px',
                    }
                }
            ],
            layout: { name: 'cose', padding: 30, animate: false }
        })
    },
    { immediate: true }
)
</script>

<template>
    <Card class="w-[50%] h-[89vh]    rounded-xl justify-between  flex flex-col overflow-hidden">

        <!-- Results Header -->
        <CardHeader class="flex flex-row  items-center justify-between    ">


            <CardTitle>Results</CardTitle>
            <!-- Export (only for SELECT) -->
            <div class="flex space-x-2">
                <Button @click="exportResults('json')" size="sm">
                    <Download /> JSON
                </Button>
                <Button @click="exportResults('csv')" variant="outline" size="sm">
                    <Download /> CSV
                </Button>
            </div>
        </CardHeader>

        <!-- Results Body -->
        <CardContent class=" overflow-auto w-full h-full p-2">

            <!-- Empty state -->
            <div v-if="!results && !running && !error"
                class="h-full flex flex-col items-center justify-center text-gray-300">
                <p class="text-4xl mb-3">🔍</p>
                <p class="text-sm font-medium">Run a query to see results</p>
                <p class="text-xs mt-1">Ctrl+Enter to run</p>
            </div>

            <!-- Loading -->
            <div v-if="running" class="h-full flex-col flex items-center justify-center">


                <Settings class=" animate-spin" />
                <p class="text-sm">Executing query...</p>

            </div>

            <!-- Error -->
            <div v-if="error" class="h-full flex-col flex items-center justify-center">
                <p class="text-sm font-semibold text-red-600 mb-1">Query Error</p>
                <p class="text-xs text-red-500 font-mono whitespace-pre-wrap">{{ error }}</p>
            </div>

            <!-- SELECT → Table -->
            <div v-if="results?.type === 'SELECT' && !running">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="text-left text-xs text-gray-400 uppercase tracking-wide border-b ">
                            <th v-for="v in results.vars" :key="v" class="pb-2 pr-4 font-medium">?{{ v }}</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-50">
                        <tr v-for="(row, i) in results.rows" :key="i" class="hover:bg-gray-50">
                            <td v-for="v in results.vars" :key="v" class="py-2 pr-4 text-xs">
                                <span class="font-mono text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded">
                                    {{ row[v] ?? '—' }}
                                </span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- ASK → Boolean -->
            <div v-if="results?.type === 'ASK' && !running" class="h-full ">

                <p class="text-2xl font-bold" :class="results.result == 'TRUE' ? 'text-green-600' : 'text-red-500'">
                    {{ results.result }}
                </p>
                <p class=" text-primary">execution time: {{ results.execution_time }}ms</p>
            </div>

            <!-- CONSTRUCT → Mini Cytoscape Graph -->
            <div v-if="results?.type === 'CONSTRUCT' && !running" class="h-full flex flex-col gap-2">
                <p class="text-xs text-gray-400">{{ results.triple_count }} triples constructed</p>
                <div ref="constructGraph" class="flex-1 rounded-xl border  "></div>
            </div>

        </CardContent>
    </Card>
</template>