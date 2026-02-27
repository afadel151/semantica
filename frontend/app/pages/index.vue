<script setup lang="ts">
import KpiCard from '~/components/dashboard/KpiCard.vue';
import LoadedFilesTable from '~/components/dashboard/LoadedFilesTable.vue';
import type { LoadedFile } from '~/types/loaded_files';
import NamespaceDistDonut from '~/components/dashboard/NamespaceDistDonut.vue';
import TopPredicatesBar from '~/components/dashboard/TopPredicatesBar.vue';
import TripleDistributionPie from '~/components/dashboard/TripleDistributionPie.vue';
import ReasoningEngine from '~/components/dashboard/ReasoningEngine.vue';
import OntologyOverview from '~/components/dashboard/OntologyOverview.vue';
import RecentSparql from '~/components/dashboard/RecentSparql.vue';
import ExportResults from '~/components/dashboard/ExportResults.vue';

definePageMeta({
    title: 'Dashboard',
})

const dataCard = ref({
    totalRevenue: 0,
    newCustomers: 0,
    activeAccount: 0,
    growthRate: 0,
})
onMounted(() => {
    dataCard.value = {
        totalRevenue: 1250.44,
        newCustomers: 1234,
        activeAccount: 45678,
        growthRate: 4.5,
    }
})



const files: LoadedFile[] = [
  {
    name: "my-graph.ttl",
    type: "RDF",
    format: "Turtle",
    triples: 1243,
    uploaded: "today",
  },
  {
    name: "foaf.owl",
    type: "Ontology",
    format: "OWL",
    triples: 89,
    uploaded: "today",
  },
  {
    name: "schema.rdf",
    type: "RDF",
    format: "RDF/XML",
    triples: 542,
    uploaded: "yesterday",
  },
]
</script>


<template>
    <div class="p-6 space-y-4">

        <!-- ROW 1 — KPI Cards -->
        <div class="grid grid-cols-5 gap-4">
            <KpiCard title="Total triples" data="1243" footer="in active graph" />
            <KpiCard title="Subjects" data="340" footer="unique" />
            <KpiCard title="Predicates" data="28" footer="unique" />
            <KpiCard title="Objects" data="890" footer="unique" />
            <KpiCard title="Inferred" data="0" footer="reasoning off" />
        </div>

        <!-- ROW 2 — Charts -->
        <div class="grid grid-cols-3 gap-4">
            
            <TripleDistributionPie />
            <TopPredicatesBar />
            <NamespaceDistDonut />

        </div>

        <!-- ROW 3 — Ontology + Reasoning -->
        <div class="grid grid-cols-2 gap-4">
           <OntologyOverview />

            <ReasoningEngine />
        </div>

        <!-- ROW 4 — Loaded Files -->
            
            <!--replace by shadcn table  -->
            <LoadedFilesTable :data="files" />

        <!-- ROW 5 — SPARQL History + Export -->
        <div class="grid grid-cols-2 gap-4">
            <RecentSparql />

           <ExportResults/>
        </div>

    </div>
</template>
