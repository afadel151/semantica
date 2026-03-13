<script setup>
import { Codemirror } from 'vue-codemirror'
import { oneDark } from '@codemirror/theme-one-dark'
import { keymap } from '@codemirror/view'
import { defaultKeymap } from '@codemirror/commands'
import { ArrowUpToLine, Eraser, Play, CircleDot, TriangleAlert } from 'lucide-vue-next'
import { mapQueryToVariant } from '~/types/badge_variant';
import { sparql } from 'codemirror-lang-sparql';
import { useSparqlState, useSparqlActions } from '~/composables/useSparql';

// State from the composable
const { query, history, activeGraphId, activeGraphName } = useSparqlState();

// Actions from the composable
const { runQuery, clearState, loadFromHistory, fetchHistory } = useSparqlActions();

onMounted(async () => {
    await fetchHistory();
});

const extensions = [
  sparql(),
  keymap.of([
    ...defaultKeymap,
    { key: 'Ctrl-Enter', run: () => { runQuery(); return true } }
  ])
]

const detectedType = computed(() => {
  if (!query.value) return null

  const cleaned = query.value
    .replace(/#.*$/gm, '')       // remove comments
    .trim()

  const match = cleaned.match(/\b(SELECT|ASK|CONSTRUCT|DESCRIBE)\b/i)

  return match ? match[1].toUpperCase() : null
})

function clearEditor() { clearState(); }


</script>

<template>
  <div class="w-full h-fit overflow-auto flex flex-col gap-3">

    <!-- Active Graph Indicator -->
    <div v-if="activeGraphId"
        class="flex items-center gap-2 px-3 py-2 rounded-lg bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 text-sm">
        <CircleDot class="w-3.5 h-3.5 text-green-500 flex-shrink-0" />
        <span class="text-green-700 dark:text-green-300 font-medium truncate">
            Graphe actif : {{ activeGraphName }}
        </span>
    </div>
    <div v-else
        class="flex items-center gap-2 px-3 py-2 rounded-lg bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 text-sm">
        <TriangleAlert class="w-3.5 h-3.5 text-amber-500 flex-shrink-0" />
        <span class="text-amber-700 dark:text-amber-300">
            Aucun graphe actif —
            <NuxtLink to="/rdf" class="underline font-medium">Activer un graphe</NuxtLink>
        </span>
    </div>

    <!-- CodeMirror Editor -->
    <Card class="flex-1 flex flex-col h-[60%] ">
      <CardHeader class="flex justify-between items-center">
        <CardTitle>Query Editor</CardTitle>
        <div class="flex items-center gap-2">
          <Badge v-if="detectedType" :variant="detectedType === 'SELECT' ? 'select' :
            detectedType === 'ASK' ? 'ask' :
              detectedType === 'CONSTRUCT' ? 'construct' : 'secondary'">
            {{ detectedType ?? 'UNKNOWN' }}
          </Badge>
          <Button @click="clearEditor" variant="outline" size="sm">
            <Eraser class="w-3 h-3 mr-1" /> Clear
          </Button>
          <Button @click="runQuery" size="sm">
            <Play class="w-3 h-3 mr-1" /> Run
          </Button>
        </div>
      </CardHeader>
      <CardContent class="flex-1 overflow-auto">
        <Codemirror v-model="query" :extensions="extensions" class="h-full text-sm" />
      </CardContent>
    </Card>

    <!-- Query History -->
    <Card class="h-[40%] ">
      <CardHeader>
        <CardTitle>Recent Queries</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableBody>
            <TableRow v-for="h in history.slice(0,3)" :key="h.id || h.query">
              <TableCell>
                <Badge :variant="mapQueryToVariant(h.query_type)">{{ h.query_type }}</Badge>
              </TableCell>
              <TableCell class="max-w-75 truncate" :title="h.query">
                {{ h.query }}
              </TableCell>
              <TableCell class="flex justify-end gap-2">
                <Button variant="outline" @click="loadFromHistory(h)" size="sm">
                  <ArrowUpToLine class="w-4 h-4 mr-1" /> Load
                </Button>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
        <p v-if="history.length === 0" class="text-xs text-gray-400 text-center py-2">No queries yet</p>
      </CardContent>
    </Card>

  </div>
</template>