<script setup lang="ts">
import { Waypoints } from 'lucide-vue-next'
import { useRoute } from 'vue-router'
import KpiCard from '~/components/KpiCard.vue'
import ObjectsTable from '~/components/rdf/ObjectsTable.vue'
import PredicatesTable from '~/components/rdf/PredicatesTable.vue'
import SubjectsTable from '~/components/rdf/SubjectsTable.vue'
import { useActiveGraphStore } from '~/store/active_graph'
import type { GraphFileStats, GraphElements } from '~/types/rdf'

const config = useRuntimeConfig()

const route = useRoute()
const activeGraphState = useActiveGraphStore()
const stats = ref<GraphFileStats>({
    name: '',
    format: '',
    uploaded_at: '',
    subjects_count: 0,
    predicates_count: 0,
    objects_count: 0,
    graph_id: '',
    file_size: 0,
    triples_count: 0
})


const elements = ref<GraphElements>({
    subjects: [],
    predicates: [],
    objects: []
})


async function fetchStats() {
    try {
        const { data, pending, error } = await useFetch<GraphFileStats>(`${config.public.apiBase}/rdf/${route.params.id}/stats`)
        if (error.value) {
            console.error('Error fetching graph stats:', error.value);
            return;
        }
        if (data.value) {
            stats.value = data.value;
        }
    } catch (error) {
        console.error('Failed to fetch graph stats:', error);
    }
}
async function fetchElements() {
    try {
        const { data, pending, error } = await useFetch<GraphElements>(`${config.public.apiBase}/rdf/${route.params.id}/elements`)
        if (error.value) {
            console.error('Error fetching graph elements:', error.value);
            return;
        }
        if (data.value) {
            elements.value = data.value;
        }
    } catch (error) {
        console.error('Failed to fetch graph elements:', error);
    }
}
onMounted(() => {
    fetchStats();
    fetchElements();
});
definePageMeta({
    title: "Graph details",
})


const isActive = ref(false)
function getFormattedDate(dateTimeStr: string): string {
    const date = new Date(dateTimeStr);
    return date.toLocaleDateString('fr-FR'); // French format
}
function toggleActive() { 
    if (isActive.value) {
        activeGraphState.clearGraph();
        isActive.value = false
    }else{
        activeGraphState.setGraph({
            id: stats?.value.graph_id,
            name: stats?.value.name,
        })
        isActive.value = true
    }

}
</script>

<template>
    <div class="p-2 space-y-6">
        <Card class="flex flex-row px-5  justify-between items-center">
            <CardHeader class="w-fit">
                <p class="text-2xl   ">
                    {{ stats?.name || 'undefined name' }}.{{ stats?.format || 'undefined format' }}
                </p>
                <CardDescription class="w-fit">
                    {{ getFormattedDate(stats?.uploaded_at || 'unknown') }}
                </CardDescription>
            </CardHeader>
            <div class="space-x-2 flex items-center">
                <NuxtLink :to="'/visualise/graph/'+ stats?.graph_id">
                    <Button size="sm" variant="outline">
                        <Waypoints />
                        Visualise
                    </Button>
                </NuxtLink>
                <Button size="sm" v-on:click="toggleActive()">
                    {{ isActive ? 'Set as Inactive' : 'Set as Active' }}
                </Button>
                <Badge v-if="isActive" variant="active">
                    Active
                </Badge>
                <Badge v-else variant="inactive">
                    Inactive
                </Badge>
            </div>
        </Card>
        <div class="grid grid-cols-3 gap-4">    
            <KpiCard title="Subjects" :data="stats?.subjects_count ?? 0" />
            <KpiCard title="Predicates" :data="stats?.predicates_count ?? 0" />
            <KpiCard title="Objects" :data="stats?.objects_count ?? 0" />

        </div>
        <div class="flex w-full flex-col  gap-6">
            <Tabs default-value="subjects">
                <TabsList>
                    <TabsTrigger value="subjects">
                        Subjects
                    </TabsTrigger>
                    <TabsTrigger value="predicates">
                        Predicates
                    </TabsTrigger>
                    <TabsTrigger value="objects">
                        Objects
                    </TabsTrigger>
                </TabsList>
                <TabsContent value="subjects">
                    <SubjectsTable :subjects="elements.subjects" />
                </TabsContent>
                <TabsContent value="predicates">
                    <PredicatesTable :predicates="elements.predicates" />
                </TabsContent>
                <TabsContent value="objects">
                    <ObjectsTable :objects="elements.objects" />
                </TabsContent>
            </Tabs>
        </div>
    </div>
</template>