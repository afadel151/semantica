<script setup lang="ts">

defineProps<{
    title: string,
    data?: string,
    footer?: unknown
}>()
</script>


<template>
    <Card class="@container/card">

        <CardHeader>
            <CardTitle>{{ title }}</CardTitle>
        </CardHeader>
        <CardContent v-if="data"  :class=" data === '0' ? 'text-indigo-500':  'text-slate-800  dark:text-gray-100'" >
            <p class="text-3xl font-semibold">{{ data }}</p>
        </CardContent>
        <CardContent v-else>
            <slot />
        </CardContent>
        <CardFooter class="text-xs text-gray-400 mt-1">{{ footer }}</CardFooter>
        
    </Card>
</template>