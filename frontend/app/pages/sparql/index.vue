<script setup lang="ts">
import LeftPanel from '~/components/sparql/LeftPanel.vue';
import RightPanel from '~/components/sparql/RightPanel.vue';
import RecentQueries from '~/components/sparql/RecentQueries.vue';

definePageMeta({
    title: "SPARQL Editor",
})
</script>

<template>
  <div class="flex flex-col gap-5 p-2 flex-1 w-full h-full min-h-0">
    <!-- 1. Éditeur de requête -->
    <LeftPanel />

    <!-- 2. Résultats de la requête -->
    <RightPanel />

    <!-- 3. Requêtes récentes -->
    <RecentQueries />
  </div>
</template>