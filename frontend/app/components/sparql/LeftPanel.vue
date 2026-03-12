<script setup>
import { Codemirror } from 'vue-codemirror'
import { oneDark } from '@codemirror/theme-one-dark'
import { keymap } from '@codemirror/view'
import { defaultKeymap } from '@codemirror/commands'
import { ArrowUpToLine, Eraser, Play } from 'lucide-vue-next'
import { mapQueryToVariant } from '~/types/badge_variant';  
import { sparql } from 'codemirror-lang-sparql';
import { useSparqlState, useSparqlActions } from '~/composables/useSparql';

// State from the composable
const { query, history, activeGraphId } = useSparqlState();

// Actions from the composable
const { runQuery, clearState, loadFromHistory, fetchHistory, initDefaultGraph } = useSparqlActions();

onMounted(async () => {
    await initDefaultGraph();
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
  <div class="w-[50%] h-[98vh] overflow-auto flex flex-col gap-3 ">

    <!-- Query Templat  es -->


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