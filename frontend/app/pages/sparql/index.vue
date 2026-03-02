<script setup lang="ts">
import { Play } from 'lucide-vue-next';
import LeftPanel from '~/components/sparql/LeftPanel.vue';
import RightPanel from '~/components/sparql/RightPanel.vue';



definePageMeta({
    title: "SPARQL Editor",
})
    
</script>

<template>  
   <div class="flex items-start  gap-4 p-6 flex-1 min-h-0">
      <!-- LEFT PANEL -->
      <LeftPanel />

      <!-- RIGHT PANEL -->
      <RightPanel />
    </div>
  
</template>