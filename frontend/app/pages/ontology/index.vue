<script setup lang="ts">
import KpiCard from '~/components/KpiCard.vue';
import OntologiesTable from '~/components/ontology/OntologiesTable.vue';

definePageMeta({
    title: "Ontologies",
})
</script>

<template>
    <div class="p-6 space-y-6">
        <div class="grid grid-cols-5 gap-4">
            <KpiCard title="Total Ontologies" data="12"/>
            <KpiCard title="Total Classes" data="100"/>
            <KpiCard title="Total Properties" data="231"/>
            <KpiCard title="Total Individuals" data="410"/>
            <KpiCard title="Formats Used">
                <div class="space-x-2 space-y-1">
                    <Badge>Owl</Badge>
                    <Badge>RDFS</Badge>
                </div>
            </KpiCard>
        </div>
        <OntologiesTable/>
    </div>
</template>