<script setup>
import { Download, Settings } from 'lucide-vue-next';
import { useSparqlState, useSparqlActions } from '~/composables/useSparql';

const { results, error, isRunning: running } = useSparqlState();
const { exportResultsFormat } = useSparqlActions();

function exportResults(format) {
    exportResultsFormat(format);
}

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
    <Card class="w-[50%] h-[98vh]    rounded-xl justify-between  flex flex-col overflow-hidden">

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
            <div v-if="results?.type === 'SELECT' && !running" class="overflow-x-auto w-full">
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
                <div ref="constructGraph" class="flex-1 rounded-xl   "></div>
            </div>

        </CardContent>
    </Card>
</template>