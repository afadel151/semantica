<script setup lang="ts">
import KpiCard from '~/components/KpiCard.vue'
import { ChevronsUpDown } from 'lucide-vue-next'

const isActive = ref(false)
function toggleActive() {
    isActive.value = !isActive.value
}

const openStates = ref<Record<string, boolean>>({})
function toggleClass(uri: string) {
    openStates.value[uri] = !openStates.value[uri]
}

const search = ref('')

// Replace with: const { data: onto } = await useFetch(`/api/owl/${route.params.id}`)
const onto = ref({
    name: 'foaf.owl',
    class_count: 3,
    object_property_count: 4,
    data_property_count: 3,
    individual_count: 5,
    classes: [
        {
            uri: 'foaf:Person',
            label: 'Person',
            prefix_form: 'foaf:Person',
            comment: 'A person.',
            parents: ['foaf:Agent'],
            children: [],
            equivalent_classes: ['schema:Person'],
            disjoint_classes: ['foaf:Document'],
            union_of: [],
            intersection_of: [],
            object_properties: [
                { label: 'knows',  range: 'foaf:Person' },
                { label: 'member', range: 'foaf:Organization' },
            ],
            data_properties: [
                { label: 'name', range: 'xsd:string'  },
                { label: 'age',  range: 'xsd:integer' },
            ],
            restrictions: [
                { property: 'foaf:knows', min_cardinality: 1, max_cardinality: null, exact_cardinality: null, some_values_from: null, all_values_from: null },
                { property: 'foaf:age',   min_cardinality: null, max_cardinality: null, exact_cardinality: 1,  some_values_from: null, all_values_from: null },
            ],
            individuals: [
                { uri: 'ex:John', label: 'John' },
                { uri: 'ex:Jane', label: 'Jane' },
            ],
            individual_count: 2,
        },
        {
            uri: 'foaf:Agent',
            label: 'Agent',
            prefix_form: 'foaf:Agent',
            comment: 'An agent (person, group, software, etc.).',
            parents: ['owl:Thing'],
            children: ['foaf:Person', 'foaf:Organization'],
            equivalent_classes: [],
            disjoint_classes: [],
            union_of: ['foaf:Person', 'foaf:Organization'],
            intersection_of: [],
            object_properties: [],
            data_properties: [],
            restrictions: [],
            individuals: [],
            individual_count: 0,
        },
    ]
})

const filteredClasses = computed(() =>
    onto.value.classes.filter(c =>
        c.label.toLowerCase().includes(search.value.toLowerCase()) ||
        c.prefix_form.toLowerCase().includes(search.value.toLowerCase())
    )
)

function restrictionLabel(r: any): string {
    if (r.exact_cardinality !== null) return `exactly ${r.exact_cardinality}`
    const parts = []
    if (r.min_cardinality !== null) parts.push(`min ${r.min_cardinality}`)
    if (r.max_cardinality !== null) parts.push(`max ${r.max_cardinality}`)
    if (r.some_values_from)         parts.push(`some values from ${r.some_values_from}`)
    if (r.all_values_from)          parts.push(`all values from ${r.all_values_from}`)
    return parts.join(', ') || '—'
}
</script>

<template>
    <div class="p-6 space-y-6">

        <Card class="flex flex-row px-5 justify-between items-center">
            <div class="flex flex-col gap-0.5">
                <CardTitle>{{ onto.name }}</CardTitle>
                <p class="text-sm text-muted-foreground">OWL Ontology</p>
            </div>
            <div class="space-x-2 flex items-center">
                <Button size="sm" @click="toggleActive()">
                    {{ isActive ? 'Set as Inactive' : 'Set as Active' }}
                </Button>
                <Badge v-if="isActive" variant="active">Active</Badge>
                <Badge v-else variant="inactive">Inactive</Badge>
            </div>
        </Card>

        <div class="grid grid-cols-4 gap-4">
            <KpiCard title="Classes"           :data="String(onto.class_count)"           />
            <KpiCard title="Object Properties" :data="String(onto.object_property_count)" />
            <KpiCard title="Data Properties"   :data="String(onto.data_property_count)"   />
            <KpiCard title="Individuals"       :data="String(onto.individual_count)"       />
        </div>

        <div class="flex items-center justify-between ml-1">
            <p class="text-xl">Classes :</p>
            <input
                v-model="search"
                placeholder="Search classes..."
                class="text-sm border border-border rounded-lg px-3 py-1.5 w-56 bg-background focus:outline-none focus:ring-2 focus:ring-ring"
            />
        </div>

        <div class="space-y-3">
            <Card v-for="cls in filteredClasses" :key="cls.uri">
                <Collapsible
                    :open="openStates[cls.uri]"
                    @update:open="toggleClass(cls.uri)"
                    class="flex w-full flex-col gap-2"
                >
                    <CollapsibleTrigger as-child class="w-full cursor-pointer">
                        <CardHeader class="w-full hover:bg-muted/50 transition-colors rounded-t-xl">
                            <p class="flex w-full text-lg justify-between items-center">
                                <span class="flex items-center gap-3">
                                    <span class="w-2.5 h-2.5 rounded-full bg-indigo-400 shrink-0"></span>
                                    {{ cls.prefix_form }}
                                    <span class="flex gap-2 text-muted-foreground font-normal text-sm">
                                        <span v-if="cls.children.length">
                                            {{ cls.children.length }} child{{ cls.children.length > 1 ? 'ren' : '' }}
                                        </span>
                                        <span v-if="cls.individual_count">
                                            {{ cls.individual_count }} individual{{ cls.individual_count > 1 ? 's' : '' }}
                                        </span>
                                        <span v-if="cls.restrictions.length">
                                            {{ cls.restrictions.length }} restriction{{ cls.restrictions.length > 1 ? 's' : '' }}
                                        </span>
                                    </span>
                                </span>
                                <ChevronsUpDown class="w-4 h-4 text-muted-foreground" />
                            </p>
                        </CardHeader>
                    </CollapsibleTrigger>

                    <CollapsibleContent>
                        <CardContent class="flex flex-col gap-4 pt-0">
                            <Card class="p-4 flex flex-col gap-5">

                                <div v-if="cls.comment">
                                    <p class="text-lg text-foreground">Comment</p>
                                    <p class="text-sm text-muted-foreground mt-1 italic">{{ cls.comment }}</p>
                                </div>

                                <div class="grid grid-cols-2 gap-x-8 gap-y-3">
                                    <div class="flex gap-2">
                                        <span class="text-base w-28 shrink-0 text-muted-foreground">Parents :</span>
                                        <div class="flex flex-wrap gap-1">
                                            <Badge v-if="cls.parents.length" v-for="p in cls.parents" :key="p" variant="secondary">{{ p }}</Badge>
                                            <span v-else class="text-sm text-muted-foreground">—</span>
                                        </div>
                                    </div>

                                    <div class="flex gap-2">
                                        <span class="text-base w-28 shrink-0 text-muted-foreground">Children :</span>
                                        <div class="flex flex-wrap gap-1">
                                            <Badge v-if="cls.children.length" v-for="c in cls.children" :key="c" variant="secondary">{{ c }}</Badge>
                                            <span v-else class="text-sm text-muted-foreground">—</span>
                                        </div>
                                    </div>

                                    <div class="flex gap-2">
                                        <span class="text-base w-28 shrink-0 text-muted-foreground">Equivalent :</span>
                                        <div class="flex flex-wrap gap-1">
                                            <Badge v-if="cls.equivalent_classes.length" v-for="e in cls.equivalent_classes" :key="e" variant="outline">{{ e }}</Badge>
                                            <span v-else class="text-sm text-muted-foreground">—</span>
                                        </div>
                                    </div>

                                    <div class="flex gap-2">
                                        <span class="text-base w-28 shrink-0 text-muted-foreground">Disjoint :</span>
                                        <div class="flex flex-wrap gap-1">
                                            <Badge v-if="cls.disjoint_classes.length" v-for="d in cls.disjoint_classes" :key="d" variant="destructive">{{ d }}</Badge>
                                            <span v-else class="text-sm text-muted-foreground">—</span>
                                        </div>
                                    </div>

                                    <div class="flex gap-2">
                                        <span class="text-base w-28 shrink-0 text-muted-foreground">Union of :</span>
                                        <div class="flex flex-wrap gap-1">
                                            <Badge v-if="cls.union_of.length" v-for="u in cls.union_of" :key="u" variant="secondary">{{ u }}</Badge>
                                            <span v-else class="text-sm text-muted-foreground">—</span>
                                        </div>
                                    </div>

                                    <div class="flex gap-2">
                                        <span class="text-base w-28 shrink-0 text-muted-foreground">Intersection :</span>
                                        <div class="flex flex-wrap gap-1">
                                            <Badge v-if="cls.intersection_of.length" v-for="i in cls.intersection_of" :key="i" variant="secondary">{{ i }}</Badge>
                                            <span v-else class="text-sm text-muted-foreground">—</span>
                                        </div>
                                    </div>
                                </div>

                                <div v-if="cls.object_properties.length">
                                    <p class="text-lg text-foreground mb-2">Object Properties</p>
                                    <div class="space-y-1.5">
                                        <div
                                            v-for="p in cls.object_properties" :key="p.label"
                                            class="flex items-center gap-2 bg-secondary rounded-lg px-3 py-1.5"
                                        >
                                            <span class="text-chart-1 font-medium text-sm">{{ p.label }}</span>
                                            <span class="text-primary">→</span>
                                            <span class="text-sm text-foreground font-mono">{{ p.range ?? '—' }}</span>
                                        </div>
                                    </div>
                                </div>

                                <div v-if="cls.data_properties.length">
                                    <p class="text-lg text-foreground mb-2">Data Properties</p>
                                    <div class="space-y-1.5">
                                        <div
                                            v-for="p in cls.data_properties" :key="p.label"
                                            class="flex items-center gap-2 bg-secondary rounded-lg px-3 py-1.5"
                                        >
                                            <span class="text-chart-2 font-medium text-sm">{{ p.label }}</span>
                                            <span class="text-primary">→</span>
                                            <span class="text-sm font-mono text-muted-foreground">{{ p.range ?? 'xsd:string' }}</span>
                                        </div>
                                    </div>
                                </div>

                                <div v-if="cls.restrictions.length">
                                    <p class="text-lg text-foreground mb-2">Restrictions</p>
                                    <div class="space-y-1.5">
                                        <div
                                            v-for="(r, i) in cls.restrictions" :key="i"
                                            class="flex items-center gap-2 bg-secondary rounded-lg px-3 py-1.5"
                                        >
                                            <span class="text-chart-4 font-medium text-sm">{{ r.property }}</span>
                                            <span class="text-primary">·</span>
                                            <span class="text-sm text-muted-foreground">{{ restrictionLabel(r) }}</span>
                                        </div>
                                    </div>
                                </div>

                                <div v-if="cls.individuals.length">
                                    <p class="text-lg text-foreground mb-2">
                                        Individuals
                                        <span class="text-sm text-muted-foreground font-normal ml-1">({{ cls.individual_count }})</span>
                                    </p>
                                    <div class="flex flex-wrap gap-1.5">
                                        <Badge
                                            v-for="ind in cls.individuals" :key="ind.uri"
                                            variant="secondary"
                                        >
                                            {{ ind.label }}
                                        </Badge>
                                    </div>
                                </div>

                                <p
                                    v-if="!cls.object_properties.length && !cls.data_properties.length && !cls.restrictions.length && !cls.individuals.length"
                                    class="text-sm text-muted-foreground italic"
                                >
                                    No properties, restrictions or individuals defined for this class.
                                </p>

                            </Card>
                        </CardContent>
                    </CollapsibleContent>
                </Collapsible>
            </Card>

            <Card v-if="filteredClasses.length === 0" class="py-12 text-center">
                <p class="text-3xl mb-2">🔍</p>
                <p class="text-sm text-muted-foreground">No classes match your search</p>
            </Card>
        </div>
    </div>
</template>