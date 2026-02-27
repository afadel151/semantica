<script setup lang="ts">
import KpiCard from '~/components/dashboard/KpiCard.vue';
import Badge from '~/components/ui/badge/Badge.vue';




definePageMeta({
    title: "RDF Graphs",
})
</script>

<template>
    <div class="p-6 space-y-6">
        <div class="grid grid-cols-4 gap-4">
            <KpiCard title="Total graphs" data="5" />
            <KpiCard title="Total triples" data="124" />
            <KpiCard title="Total Size" data="50Mb" />
            <KpiCard title="Formats used">
                <div class="space-x-2">
                    <Badge>Turtle</Badge>
                    <Badge>Turtle</Badge>
                    <Badge>Turtle</Badge>
                    <Badge>XML</Badge>
                    <Badge>N-triples</Badge>
                    <Badge>N-triples</Badge>
                </div>
            </KpiCard>
        </div>
    </div>

</template>