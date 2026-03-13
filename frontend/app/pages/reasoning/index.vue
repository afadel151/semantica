<script setup lang="ts">
import { Settings, Play, ChevronDown, ChevronUp } from 'lucide-vue-next'
import KpiCard from '~/components/KpiCard.vue'
import { useActiveGraphStore } from '~/store/active_graph'
import { useActiveOntologiesStore } from '~/store/active_ontology'

definePageMeta({ title: 'Reasoning' })

const activeGraphStore = useActiveGraphStore()
const activeOntologiesStore = useActiveOntologiesStore()
const formalism = ref('RDFS')
const running = ref(false)
const error = ref<string | null>(null)
const results = ref<any | null>(null)
const openSubjects = ref<Record<string, boolean>>({})

const formalisms = [
    {
        value: 'RDFS',
        label: 'RDFS',
        description: 'Subclass/subproperty inheritance, domain and range inference. Fast and simple.',
        color: 'bg-blue-50 text-blue-600 border-blue-200',
    },
    {
        value: 'OWL-RL',
        label: 'OWL-RL',
        description: 'Full OWL reasoning: inverse properties, transitivity, sameAs. Most common choice.',
        color: 'bg-indigo-50 text-indigo-600 border-indigo-200',
    },
    {
        value: 'OWL-QL',
        label: 'OWL-QL',
        description: 'Lightweight inference optimized for fast SPARQL querying over large datasets.',
        color: 'bg-amber-50 text-amber-600 border-amber-200',
    },
]

const formalismColor: Record<string, string> = {
    'RDFS': 'bg-blue-50 text-blue-600',
    'OWL-RL': 'bg-indigo-50 text-indigo-600',
    'OWL-QL': 'bg-amber-50 text-amber-600',
}

function toggleSubject(subject: string) {
    openSubjects.value[subject] = !openSubjects.value[subject]
}

watch(formalism, () => {
    results.value = null
    error.value = null
    openSubjects.value = {}
})
const config = useRuntimeConfig()
async function runReasoning() {
    if (!activeGraphStore.id) return

    running.value = true
    error.value = null
    results.value = null
    openSubjects.value = {}

    try {
        const data = await $fetch(`${config.public.apiBase}/reasoning/run`, {
            method: 'POST',
            body: {
                graph_id: activeGraphStore.id,
                ontology_ids: activeOntologiesStore.getOntologiesIds,
                formalism: formalism.value,
            }
        })
        results.value = data
    } catch (err: any) {
        error.value = err?.data?.detail ?? 'Reasoning failed. Check your graph and ontologies.'
    } finally {
        running.value = false
    }
}
</script>

<template>
    <div class="p-2 space-y-6">

        <Card class="flex flex-row px-5 justify-between items-center">
            <div class="flex flex-col gap-0.5">
                <CardTitle>Reasoning Engine</CardTitle>
                <p class="text-sm text-muted-foreground">
                    Apply deductive reasoning to infer new triples
                </p>
            </div>
            <div class="flex items-center gap-2">
                <Badge :variant="activeGraphStore.id ? 'default' : 'destructive'">
                    {{ activeGraphStore.id ? `Graph active` : 'No active graph' }}
                </Badge>
                <Badge variant="secondary">
                    {{ activeOntologiesStore.getOntologiesIds.length }} ontolog{{
                        activeOntologiesStore.getOntologiesIds.length === 1 ? 'y' : 'ies' }}
                </Badge>
            </div>
        </Card>

        <div class="space-y-2">
            <p class="text-xl ml-1">Formalism :</p>
            <div class="grid grid-cols-3 gap-3">
                <Card v-for="f in formalisms" :key="f.value" class="p-4 cursor-pointer transition-all"
                    :class="formalism === f.value ? 'border-primary' : 'border-transparent hover:border-secondary'"
                    @click="formalism = f.value">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-xs font-bold px-2 py-0.5 rounded-full" :class="f.color">
                            {{ f.label }}
                        </span>
                        <span v-if="formalism === f.value" class="w-2 h-2 rounded-full bg-primary"></span>
                    </div>
                    <p class="text-xs text-muted-foreground leading-relaxed">
                        {{ f.description }}
                    </p>
                </Card>
            </div>
        </div>

        <div class="flex items-center gap-3">
            <Button @click="runReasoning" :disabled="running || !activeGraphStore.id" class="flex items-center gap-2">
                <Settings v-if="running" class="w-4 h-4 animate-spin" />
                <Play v-else class="w-4 h-4" />
                {{ running ? 'Running...' : `Run ${formalism} Reasoning` }}
            </Button>
            <p v-if="!activeGraphStore.id" class="text-sm text-destructive">
                Set an active graph first
            </p>
            <p v-else-if="activeOntologiesStore.getOntologiesIds.length === 0" class="text-sm text-muted-foreground">
                No ontologies selected — reasoning runs on graph only
            </p>
        </div>

        <Card v-if="error" class="p-4 border-destructive">
            <p class="text-sm font-semibold text-destructive mb-1">Reasoning Error</p>
            <p class="text-xs font-mono text-destructive/80 whitespace-pre-wrap">{{ error }}</p>
        </Card>

        <template v-if="results && !running">

            <div class="grid grid-cols-4 gap-4">
                <KpiCard title="Original Triples" :data="String(results.original_count)" />
                <KpiCard title="Inferred Triples" :data="String(results.inferred_count)" />
                <KpiCard title="Total Triples" :data="String(results.total_count)" />
                <KpiCard title="Execution Time" :data="`${results.execution_time}ms`" />
            </div>

            <div class="flex items-center justify-between ml-1">
                <div class="flex items-center gap-2">
                    <p class="text-xl">Inferred Triples :</p>
                    <span class="text-xs font-bold px-2 py-0.5 rounded-full" :class="formalismColor[results.formalism]">
                        {{ results.formalism }}
                    </span>
                </div>
                <div class="flex items-center gap-3">
                    <p class="text-sm text-muted-foreground">
                        {{ results.subjects.length }} subjects affected
                    </p>
                    <div class="flex gap-2">
                        <Button size="sm" variant="outline"
                            @click="results.subjects.forEach((g: any) => openSubjects[g.subject] = true)">
                            Expand All
                        </Button>
                        <Button size="sm" variant="outline" @click="openSubjects = {}">
                            Collapse All
                        </Button>
                    </div>
                </div>
            </div>

            <div class="space-y-3">
                <Card v-for="group in results.subjects" :key="group.subject">
                    <Collapsible :open="openSubjects[group.subject]" @update:open="toggleSubject(group.subject)"
                        class="flex w-full flex-col gap-2">
                        <CollapsibleTrigger as-child class="w-full cursor-pointer">
                            <CardHeader class="w-full hover:bg-muted/50 transition-colors rounded-t-xl">
                                <div class="flex w-full justify-between items-center">
                                    <span class="flex items-center gap-3">
                                        <span class="w-2.5 h-2.5 rounded-full bg-indigo-400 shrink-0"></span>
                                        <span class="font-medium text-base">{{ group.prefix_form }}</span>
                                        <span class="text-xs text-muted-foreground font-mono truncate max-w-64">
                                            {{ group.subject }}
                                        </span>
                                    </span>
                                    <div class="flex items-center gap-3">
                                        <Badge variant="secondary">
                                            +{{ group.triples.length }} triple{{ group.triples.length > 1 ? 's' : '' }}
                                        </Badge>
                                        <ChevronDown v-if="!openSubjects[group.subject]"
                                            class="w-4 h-4 text-muted-foreground" />
                                        <ChevronUp v-else class="w-4 h-4 text-muted-foreground" />
                                    </div>
                                </div>
                            </CardHeader>
                        </CollapsibleTrigger>

                        <CollapsibleContent>
                            <CardContent class="pt-0 pb-3">
                                <div class="rounded-lg border border-border overflow-hidden">
                                    <div class="grid grid-cols-3 gap-4 px-4 py-2 bg-muted/50 border-b border-border">
                                        <span class="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                                            Predicate
                                        </span>
                                        <span class="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                                            Object
                                        </span>
                                        <span class="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                                            Type
                                        </span>
                                    </div>
                                    <div v-for="(triple, i) in group.triples" :key="i"
                                        class="grid grid-cols-3 gap-4 px-4 py-2.5 items-center border-b border-border/50 last:border-0 hover:bg-muted/30 transition-colors">
                                        <span class="text-sm font-medium text-chart-1 font-mono truncate">
                                            {{ triple.predicate_label }}
                                        </span>

                                        <span class="text-sm font-mono truncate" :class="triple.object_type === 'literal'
                                            ? 'text-amber-600'
                                            : 'text-foreground'">
                                            {{ triple.object_label }}
                                        </span>

                                        <div>
                                            <Badge v-if="triple.object_type === 'literal'" variant="outline"
                                                class="text-xs text-amber-600 border-amber-200">
                                                literal
                                            </Badge>
                                            <Badge v-else variant="outline"
                                                class="text-xs text-indigo-600 border-indigo-200">
                                                uri
                                            </Badge>
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </CollapsibleContent>
                    </Collapsible>
                </Card>

                <Card v-if="results.subjects.length === 0" class="py-12 text-center">
                    <p class="text-3xl mb-2">🤔</p>
                    <p class="text-sm text-muted-foreground">
                        No new triples inferred with {{ results.formalism }}
                    </p>
                    <p class="text-xs text-muted-foreground mt-1">
                        Try a different formalism or add more ontologies
                    </p>
                </Card>
            </div>

        </template>

        <Card v-if="!results && !running && !error" class="py-16 text-center">
            <p class="text-4xl mb-3">🧠</p>
            <p class="text-base font-medium text-foreground">No reasoning applied yet</p>
            <p class="text-sm text-muted-foreground mt-1">
                Select a formalism above and click Run
            </p>
        </Card>

    </div>
</template>