<script setup>
// Affiche les métriques de performance après exécution d'une requête SPARQL
import { Clock, Database, Rows, Zap } from 'lucide-vue-next';
import { useSparqlState } from '~/composables/useSparql';

const { results, updateResult } = useSparqlState();

const metrics = computed(() => {
    const r = results.value;
    const u = updateResult.value;

    if (!r && !u) return null;

    if (u) {
        return {
            execution_time: u.execution_time ?? 0,
            result_count: null,
            graph_size: u.graph_size ?? 0,
            triples_added: u.triples_added ?? 0,
            triples_removed: u.triples_removed ?? 0,
            type: 'UPDATE',
        };
    }

    let result_count = null;
    if (r.type === 'SELECT') result_count = r.rows?.length ?? 0;
    else if (r.type === 'CONSTRUCT') result_count = r.triple_count ?? 0;
    else if (r.type === 'ASK') result_count = null;

    return {
        execution_time: r.execution_time ?? 0,
        result_count,
        graph_size: r.graph_size ?? 0,
        triples_added: null,
        triples_removed: null,
        type: r.type,
    };
});

const speedClass = computed(() => {
    if (!metrics.value) return '';
    const t = metrics.value.execution_time;
    if (t < 100) return 'text-emerald-600 dark:text-emerald-400';
    if (t < 1000) return 'text-amber-600 dark:text-amber-400';
    return 'text-red-600 dark:text-red-400';
});

const speedLabel = computed(() => {
    if (!metrics.value) return '';
    const t = metrics.value.execution_time;
    if (t < 100) return 'Rapide';
    if (t < 1000) return 'Modéré';
    return 'Lent';
});
</script>

<template>
    <div v-if="metrics"
        class="flex flex-wrap items-center gap-3 px-3 py-2 rounded-lg border border-dashed border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50 text-xs">

        <!-- Vitesse globale -->
        <div class="flex items-center gap-1.5">
            <Zap class="w-3.5 h-3.5" :class="speedClass" />
            <span class="font-semibold" :class="speedClass">{{ speedLabel }}</span>
        </div>

        <span class="w-px h-4 bg-gray-200 dark:bg-gray-700" />

        <!-- Temps d'exécution -->
        <div class="flex items-center gap-1.5 text-muted-foreground">
            <Clock class="w-3.5 h-3.5" />
            <span>Temps : <strong :class="speedClass">{{ metrics.execution_time }} ms</strong></span>
        </div>

        <!-- Nombre de résultats (SELECT / CONSTRUCT) -->
        <div v-if="metrics.result_count !== null" class="flex items-center gap-1.5 text-muted-foreground">
            <Rows class="w-3.5 h-3.5" />
            <span>Résultats : <strong class="text-foreground">{{ metrics.result_count }}</strong></span>
        </div>

        <!-- Taille du graphe -->
        <div v-if="metrics.graph_size > 0" class="flex items-center gap-1.5 text-muted-foreground">
            <Database class="w-3.5 h-3.5" />
            <span>Graphe : <strong class="text-foreground">{{ metrics.graph_size }} triplets</strong></span>
        </div>

        <!-- UPDATE stats -->
        <template v-if="metrics.type === 'UPDATE'">
            <span class="w-px h-4 bg-gray-200 dark:bg-gray-700" />
            <span class="text-emerald-600 dark:text-emerald-400 font-medium">
                +{{ metrics.triples_added }} ajoutés
            </span>
            <span class="text-red-500 font-medium">
                -{{ metrics.triples_removed }} supprimés
            </span>
        </template>
    </div>
</template>
