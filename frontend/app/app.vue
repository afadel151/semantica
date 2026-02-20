<script setup>
import { onMounted } from 'vue'

onMounted(async () => {
  await nextTick()

  try {
    const { invoke } = await import('@tauri-apps/api/core')
    await invoke('splash_screen')
  } catch (e) {
    console.log('Not in Tauri context')
  }
})
</script>
<template>
  <NuxtLoadingIndicator />
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
