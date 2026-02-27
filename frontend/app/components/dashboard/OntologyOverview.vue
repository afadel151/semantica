<script setup lang="ts">
import { ArrowRight } from 'lucide-vue-next';


</script>

<template>
     <Card class="flex flex-col justify-between">
                <CardHeader>Ontology Overview</CardHeader>
                <CardContent class="space-y-2">
                    <div class="flex justify-between text-sm">
                        <span class="text-gray-500">Classes</span>
                        <span class="font-medium text-gray-800 dark:text-gray-100">12</span>
                    </div>
                    <div class="flex justify-between text-sm">
                        <span class="text-gray-500">Object Properties</span>
                        <span class="font-medium text-gray-800 dark:text-gray-100">8</span>
                    </div>
                    <div class="flex justify-between text-sm">
                        <span class="text-gray-500">Data Properties</span>
                        <span class="font-medium text-gray-800 dark:text-gray-100">5</span>
                    </div>
                    <div class="flex justify-between text-sm">
                        <span class="text-gray-500">Individuals</span>
                        <span class="font-medium text-gray-800 dark:text-gray-100">34</span>
                    </div>
                    <div class="flex justify-between text-sm">
                        <span class="text-gray-500">Max Depth</span>
                        <span class="font-medium text-gray-800 dark:text-gray-100">4</span>
                    </div>
                </CardContent>
                <CardFooter  class="flex items-center justify-end space-x-2">                    
                    <NuxtLink to="/ontology">
                        <Button variant="secondary">
                            <ArrowRight/>
                            View Hierarchy 
                        </Button>
                    </NuxtLink>
                </CardFooter>
            </Card>
</template>