<script setup>
import { Codemirror } from 'vue-codemirror'
import { oneDark } from '@codemirror/theme-one-dark'
import { keymap } from '@codemirror/view'
import { defaultKeymap } from '@codemirror/commands'
import { ArrowUpToLine, Eraser, Play } from 'lucide-vue-next'
import { mapQueryToVariant } from '~/types/badge_variant';  
import { sparql } from 'codemirror-lang-sparql';




const query = ref(`SELECT ?subject ?predicate ?object
WHERE {
  ?subject ?predicate ?object
}
LIMIT 25`)


// query, query_type, graph_name, ontoligies(names), executed_at
const history = ref([
  {
    query: `SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10`,
    query_type: 'SELECT',
    graph_name: 'default',
    ontologies: ['ontology1.owl', 'ontology2.owl'],
    executed_at: '2024-06-20 14:30:00',
    row_count: 10,
  },
  {
    query: `ASK { ?s a <http://example.com/SomeClass> }`,
    query_type: 'ASK',
    graph_name: 'default',
    ontologies: ['ontology1.owl'],
    executed_at: '2024-06-19 10:15:00',
    result: true,
  },
  {
    query: `CONSTRUCT { ?s a <http://example.com/SomeClass> } WHERE { ?s a <http://example.com/SomeClass> }`,
    query_type: 'CONSTRUCT',
    graph_name: 'default',
    ontologies: ['ontology1.owl'],
    executed_at: '2024-06-19 10:15:00',
    row_count: 5,
  }
])

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

function clearEditor() { query.value = ''; results.value = null; error.value = null }
function loadFromHistory(h) { query.value = h.query }

</script>

<template>
  <div class="w-[50%] h-[89vh] overflow-auto flex flex-col gap-3 ">

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
            <TableRow v-for="query in history" :key="query.query">
              <TableCell>
                <Badge :variant="mapQueryToVariant(query.query_type)">{{ query.query_type }}</Badge>
              </TableCell>
              <TableCell class="max-w-75 truncate">
                {{ query.query }}
              </TableCell>
              <TableCell class="flex justify-end ">
                <Button variant="outline" @click="loadFromHistory(query)">
                  <ArrowUpToLine />
                  Load
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