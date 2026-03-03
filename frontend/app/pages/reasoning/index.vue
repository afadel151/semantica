<script setup lang="ts">
import { Settings, Play, ChevronDown, ChevronUp } from 'lucide-vue-next'
import KpiCard from '~/components/KpiCard.vue'


const formalism      = ref('RDFS')
const running        = ref(false)
const error          = ref<string | null>(null)
const results        = ref<any | null>(null)
const openSubjects   = ref<Record<string, boolean>>({})

const formalisms = [
    {
        value:       'RDFS',
        label:       'RDFS',
        description: 'Subclass/subproperty inheritance, domain and range inference. Fast and simple.',
        color:       'bg-blue-50 text-blue-600 border-blue-200',
    },  
    {
        value:       'OWL-RL',
        label:       'OWL-RL',
        description: 'Full OWL reasoning: inverse properties, transitivity, sameAs. Most common choice.',
        color:       'bg-indigo-50 text-indigo-600 border-indigo-200',
    },
    {
        value:       'OWL-EL',
        label:       'OWL-EL',
        description: 'Optimized for large ontologies with existential restrictions (e.g. biomedical).',
        color:       'bg-emerald-50 text-emerald-600 border-emerald-200',
    },
    {
        value:       'OWL-QL',
        label:       'OWL-QL',
        description: 'Lightweight inference optimized for fast SPARQL querying over large datasets.',
        color:       'bg-amber-50 text-amber-600 border-amber-200',
    },
]

function toggleSubject(subject: string) {
    openSubjects.value[subject] = !openSubjects.value[subject]
}

async function runReasoning() {
    // if (!store.activeGraphId) return
    // running.value = true
    // error.value   = null
    // results.value = null

    // try {
    //     const data = await $fetch('http://localhost:8000/api/reasoning/run', {
    //         method: 'POST',
    //         body: {
    //             graph_id:     store.activeGraphId,
    //             ontology_ids: store.activeOntologyIds,
    //             formalism:    formalism.value,
    //         }
    //     })
    //     results.value = data
    // } catch (err: any) {
    //     error.value = err?.data?.detail ?? 'Reasoning failed'
    // } finally {
    //     running.value = false
    // }
}

const formalismColor: Record<string, string> = {
    'RDFS':   'bg-blue-50 text-blue-600',
    'OWL-RL': 'bg-indigo-50 text-indigo-600',
    'OWL-EL': 'bg-emerald-50 text-emerald-600',
    'OWL-QL': 'bg-amber-50 text-amber-600',
}
</script>

<template>
    <div class="p-6 space-y-6">

        <!-- HEADER -->
        <Card class="flex flex-row px-5 justify-between items-center">
            <div class="flex flex-col gap-0.5">
                <CardTitle>Reasoning Engine</CardTitle>
                <p class="text-sm text-muted-foreground">
                    Apply deductive reasoning to infer new triples
                </p>
            </div>
            <!-- Active context -->
            <div class="flex items-center gap-2">
                <Badge>
                    Active graph
                </Badge>
                <Badge variant="secondary">
                    3 ontologies
                </Badge>
            </div>
        </Card>

        <!-- FORMALISM SELECTOR -->
        <div class="space-y-2">
            <p class="text-xl ml-1">Formalism :</p>
            <div class="grid grid-cols-4 gap-3">
                <Card
                    v-for="f in formalisms" :key="f.value"
                    class="p-4 cursor-pointer transition-all "
                    :class="formalism === f.value ? 'border-primary' : 'border-transparent hover:border-secondary   '"
                    @click="formalism = f.value"
                >
                    <div class="flex items-center justify-between mb-2">
                        <span
                            class="text-xs font-bold px-2 py-0.5 rounded-full"
                            :class="f.color"
                        >
                            {{ f.label }}
                        </span>
                        <!-- selected indicator -->
                        <span
                            v-if="formalism === f.value"
                            class="w-2 h-2 rounded-full bg-primary"
                        ></span>
                    </div>
                    <p class="text-xs text-muted-foreground leading-relaxed">
                        {{ f.description }}
                    </p>
                </Card>
            </div>
        </div>

        <!-- RUN BUTTON -->
        <div class="flex items-center gap-3">
            <Button
                @click="runReasoning"
                
                class="flex items-center gap-2"
            >
                <Settings v-if="running" class="w-4 h-4 animate-spin" />
                <Play v-else class="w-4 h-4" />
                {{ running ? 'Running...' : `Run ${formalism} Reasoning` }}
            </Button>
            <p class="text-sm text-muted-foreground">
                Set an active graph first
            </p>
        </div>

        <!-- ERROR -->
        <Card v-if="error" class="p-4 border-destructive">
            <p class="text-sm font-semibold text-destructive mb-1">Reasoning Error</p>
            <p class="text-xs font-mono text-destructive/80 whitespace-pre-wrap">{{ error }}</p>
        </Card>

        <!-- RESULTS -->
        <template v-if="results && !running">

            <!-- KPI CARDS -->
            <div class="grid grid-cols-4 gap-4">
                <KpiCard
                    title="Original Triples"
                    :data="String(results.original_count)"
                />
                <KpiCard
                    title="Inferred Triples"
                    :data="String(results.inferred_count)"
                />
                <KpiCard
                    title="Total Triples"
                    :data="String(results.total_count)"
                />
                <KpiCard
                    title="Execution Time"
                    :data="`${results.execution_time}ms`"
                />
            </div>

            <!-- INFERRED TRIPLES HEADER -->
            <div class="flex items-center justify-between ml-1">
                <div class="flex items-center gap-2">
                    <p class="text-xl">Inferred Triples :</p>
                    <Badge :class="formalismColor[results.formalism]">
                        {{ results.formalism }}
                    </Badge>
                </div>
                <p class="text-sm text-muted-foreground">
                    {{ results.subjects.length }} subjects affected
                </p>
            </div>

            <!-- GROUPED BY SUBJECT -->
            <div class="space-y-3">
                <Card
                    v-for="group in results.subjects"
                    :key="group.subject"
                >
                    <Collapsible
                        :open="openSubjects[group.subject]"
                        @update:open="toggleSubject(group.subject)"
                        class="flex w-full flex-col gap-2"
                    >
                        <!-- Subject Header -->
                        <CollapsibleTrigger as-child class="w-full cursor-pointer">
                            <CardHeader class="w-full hover:bg-muted/50 transition-colors rounded-t-xl">
                                <p class="flex w-full text-base justify-between items-center">
                                    <span class="flex items-center gap-3">
                                        <span class="w-2 h-2 rounded-full bg-indigo-400 shrink-0"></span>
                                        <span class="font-medium">{{ group.prefix_form }}</span>
                                        <span class="text-sm text-muted-foreground font-normal">
                                            {{ group.triples.length }} new triple{{ group.triples.length > 1 ? 's' : '' }}
                                        </span>
                                    </span>
                                    <ChevronDown
                                        v-if="!openSubjects[group.subject]"
                                        class="w-4 h-4 text-muted-foreground"
                                    />
                                    <ChevronUp v-else class="w-4 h-4 text-muted-foreground" />
                                </p>
                            </CardHeader>
                        </CollapsibleTrigger>

                        <!-- Inferred triples for this subject -->
                        <CollapsibleContent>
                            <CardContent class="pt-0">
                                <Card class="p-3 flex flex-col gap-2">
                                    <div
                                        v-for="(triple, i) in group.triples"
                                        :key="i"
                                        class="flex items-center gap-2 bg-secondary rounded-lg px-3 py-1.5"
                                    >
                                        <!-- Predicate -->
                                        <span class="text-chart-1 font-medium text-sm">
                                            {{ triple.predicate_label }}
                                        </span>
                                        <span class="text-primary">→</span>
                                        <!-- Object -->
                                        <span
                                            class="text-sm font-mono"
                                            :class="triple.object_type === 'literal'
                                                ? 'text-amber-600'
                                                : 'text-foreground'"
                                        >
                                            {{ triple.object_label }}
                                        </span>
                                        <!-- Literal badge -->
                                        <Badge
                                            v-if="triple.object_type === 'literal'"
                                            variant="secondary"
                                            class="text-xs ml-auto"
                                        >
                                            literal
                                        </Badge>
                                    </div>
                                </Card>
                            </CardContent>
                        </CollapsibleContent>
                    </Collapsible>
                </Card>

                <!-- No inferred triples -->
                <Card v-if="results.subjects.length === 0" class="py-12 text-center">
                    <p class="text-3xl mb-2">🤔</p>
                    <p class="text-sm text-muted-foreground">
                        No new triples were inferred with {{ results.formalism }}
                    </p>
                    <p class="text-xs text-muted-foreground mt-1">
                        Try a different formalism or load more ontologies
                    </p>
                </Card>
            </div>

        </template>

        <!-- EMPTY STATE — before first run -->
        <Card v-if="!results && !running && !error" class="py-16 text-center">
            <p class="text-4xl mb-3">🧠</p>
            <p class="text-base font-medium text-foreground">No reasoning applied yet</p>
            <p class="text-sm text-muted-foreground mt-1">
                Select a formalism above and click Run
            </p>
        </Card>

    </div>
</template>
