<script setup lang="ts">
import { ArrowRight, CirclePlay } from 'lucide-vue-next';


</script>

<template>
    <Card class="flex flex-col justify-between">
        <CardHeader>Reasoning Engine</CardHeader>
        <CardContent class="space-y-2">
            <div class="flex justify-between text-sm">
                <span class="text-gray-500">Status</span>
                <span class="font-medium text-red-400">OFF</span>
            </div>
            <div class="flex justify-between text-sm">
                <span class="text-gray-500">Formalism</span>
                <span class="font-medium text-gray-400">—</span>
            </div>
            <div class="flex justify-between text-sm">
                <span class="text-gray-500">Inferred Triples</span>
                <span class="font-medium text-gray-800 dark:text-gray-100">0</span>
            </div>
        </CardContent>
        <CardFooter class="flex items-center justify-end space-x-2">
            <Button>
                <CirclePlay />
                Enable Reasoning
            </Button>
            <NuxtLink to="/reasoning">
                <Button variant="outline">
                    <ArrowRight/>
                    Go to Reasoning 
                    
                </Button>
            </NuxtLink>
        </CardFooter>
    </Card>
</template>