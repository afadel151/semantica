<script setup>
import { Codemirror } from 'vue-codemirror'
import { oneDark } from '@codemirror/theme-one-dark'
import { keymap } from '@codemirror/view'
import { defaultKeymap } from '@codemirror/commands'
import { autocompletion, CompletionContext } from '@codemirror/autocomplete'
import { Eraser, Play, CircleDot, TriangleAlert, Star } from 'lucide-vue-next'
import { sparql } from 'codemirror-lang-sparql';
import { useSparqlState, useSparqlActions } from '~/composables/useSparql';

// ─── État ─────────────────────────────────────────────────────────────────────
const { query, activeGraphId, activeGraphName, schema } = useSparqlState();
const { runQuery, clearState, fetchHistory, fetchSchema } = useSparqlActions();

// ─── Mots-clés SPARQL ─────────────────────────────────────────────────────────
const SPARQL_KEYWORDS = [
  'SELECT','DISTINCT','REDUCED','WHERE','FILTER','OPTIONAL','UNION','GRAPH',
  'PREFIX','BASE','FROM','NAMED','ORDER','BY','ASC','DESC','LIMIT','OFFSET',
  'GROUP','HAVING','BIND','VALUES','AS','IN','NOT','EXISTS','MINUS','SERVICE',
  'SILENT','CONSTRUCT','DESCRIBE','ASK','INSERT','DELETE','DATA','LOAD','CLEAR',
  'DROP','CREATE','ADD','MOVE','COPY','WITH','USING','DEFAULT','ALL','NAMED',
  'OPTIONAL','UNION','MINUS','GRAPH','SERVICE','BIND','UNDEF','TRUE','FALSE',
  // Fonctions
  'STR','LANG','LANGMATCHES','DATATYPE','BOUND','IRI','URI','BNODE','RAND',
  'ABS','CEIL','FLOOR','ROUND','CONCAT','STRLEN','SUBSTR','UCASE','LCASE',
  'ENCODE_FOR_URI','CONTAINS','STRSTARTS','STRENDS','STRBEFORE','STRAFTER',
  'YEAR','MONTH','DAY','HOURS','MINUTES','SECONDS','TIMEZONE','TZ','NOW',
  'UUID','STRUUID','MD5','SHA1','SHA256','SHA384','SHA512','COALESCE',
  'IF','STRLANG','STRDT','SAMETERM','ISIRI','ISURI','ISBLANK','ISLITERAL',
  'ISNUMERIC','REGEX','SUBSTR','REPLACE','COUNT','SUM','MIN','MAX','AVG',
  'SAMPLE','GROUP_CONCAT','SEPARATOR',
  // RDF-star
  '<<','>>','ASSERTED','OCCURRENCES',
];

// ─── Source d'autocomplétion ────────────────────────────────────────────────
function sparqlCompletionSource(context) {
  const word = context.matchBefore(/[\w:<>?!]+/);
  if (!word || (word.from === word.to && !context.explicit)) return null;

  const options = [];

  for (const kw of SPARQL_KEYWORDS) {
    if (kw.toLowerCase().startsWith(word.text.toLowerCase())) {
      options.push({ label: kw, type: 'keyword', boost: 3 });
    }
  }

  const s = schema.value;

  for (const [prefix] of Object.entries(s.prefixes || {})) {
    if (prefix && `${prefix}:`.startsWith(word.text)) {
      options.push({ label: `${prefix}:`, type: 'namespace', info: s.prefixes[prefix], boost: 2 });
    }
  }

  for (const cls of s.classes || []) {
    const short = cls.split(/[/#]/).pop();
    if (short && short.toLowerCase().startsWith(word.text.toLowerCase())) {
      options.push({ label: short, detail: shortenURI(cls), type: 'class', boost: 1 });
    }
    if (cls.toLowerCase().startsWith(word.text.toLowerCase())) {
      options.push({ label: cls, type: 'class' });
    }
  }

  for (const prop of s.properties || []) {
    const short = prop.split(/[/#]/).pop();
    if (short && short.toLowerCase().startsWith(word.text.toLowerCase())) {
      options.push({ label: short, detail: shortenURI(prop), type: 'property', boost: 1 });
    }
  }

  return { from: word.from, options };
}

function shortenURI(uri) {
  return uri.split(/[/#]/).pop() || uri;
}

// ─── Chargement au montage ────────────────────────────────────────────────────
onMounted(async () => {
  await fetchHistory();
  if (activeGraphId.value) {
    await fetchSchema(activeGraphId.value);
  }
});

watch(activeGraphId, async (id) => {
  if (id) await fetchSchema(id);
});

// ─── Extensions CodeMirror ────────────────────────────────────────────────────
const extensions = computed(() => [
  sparql(),
  autocompletion({ override: [sparqlCompletionSource] }),
  keymap.of([
    ...defaultKeymap,
    { key: 'Ctrl-Enter', run: () => { runQuery(); return true } }
  ])
]);

// ─── Type détecté ────────────────────────────────────────────────────────────
const detectedType = computed(() => {
  if (!query.value) return null;
  const cleaned = query.value.replace(/#.*$/gm, '').trim();
  const match = cleaned.match(/\b(SELECT|ASK|CONSTRUCT|DESCRIBE|INSERT|DELETE|UPDATE)\b/i);
  return match ? match[1].toUpperCase() : null;
});

const hasRdfStar = computed(() => /<</.test(query.value || ''));

const badgeVariant = computed(() => {
  const t = detectedType.value;
  if (t === 'SELECT') return 'select';
  if (t === 'ASK') return 'ask';
  if (t === 'CONSTRUCT') return 'construct';
  if (t === 'INSERT') return 'default';
  if (t === 'DELETE') return 'destructive';
  if (t === 'UPDATE') return 'secondary';
  return 'secondary';
});

function clearEditor() { clearState(); }
</script>

<template>
  <div class="w-full flex flex-col gap-3">

    <!-- Indicateur graphe actif -->
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

    <!-- Éditeur CodeMirror (Hauteur réduite et sans historique ni auto-générateur) -->
    <Card class="flex flex-col h-[450px]">
      <CardHeader class="flex flex-row justify-between items-center py-3">
        <CardTitle>Query Editor</CardTitle>
        <div class="flex items-center gap-2 flex-wrap">
          <!-- Badge type de requête -->
          <Badge v-if="detectedType" :variant="badgeVariant">
            {{ detectedType }}
          </Badge>
          <!-- Badge RDF-star -->
          <Badge v-if="hasRdfStar" variant="secondary" class="flex items-center gap-1">
            <Star class="w-3 h-3 text-yellow-500" /> RDF-star
          </Badge>
          <Button @click="clearEditor" variant="outline" size="sm">
            <Eraser class="w-3 h-3 mr-1" /> Vider
          </Button>
          <Button @click="runQuery" size="sm">
            <Play class="w-3 h-3 mr-1" />
            <span v-if="detectedType === 'INSERT' || detectedType === 'DELETE' || detectedType === 'UPDATE'">Exécuter UPDATE</span>
            <span v-else>Exécuter</span>
          </Button>
        </div>
      </CardHeader>

      <CardContent class="flex-1 overflow-auto mt-0 p-0 border-t border-gray-100 dark:border-gray-800">
        <Codemirror v-model="query" :extensions="extensions" class="h-full text-sm" />
      </CardContent>
    </Card>

    <!-- Aide autocomplétion -->
    <div class="flex items-center gap-2 text-xs text-muted-foreground px-1">
      <span class="px-1.5 py-0.5 rounded bg-muted font-mono text-[10px]">Ctrl+Space</span>
      <span>Autocomplétion (mots-clés, préfixes, classes, propriétés)</span>
      <span class="px-1.5 py-0.5 rounded bg-muted font-mono text-[10px]">Ctrl+Enter</span>
      <span>Exécuter</span>
    </div>

  </div>
</template>