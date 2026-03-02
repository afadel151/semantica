<script setup lang="ts">
const route = useRoute()
const pageName: string| unknown = route.meta.title
</script>

<template>
    <SidebarProvider >
        <AppSidebar />
        <main class="w-full">
            <!-- <nav class="flex justify-between items-center p-4 w-full border-b"> -->
                <SidebarTrigger :title="pageName"  />
                
                <!-- <ModeToggle /> -->

            <!-- </nav> -->
            <slot />    
        </main>
    </SidebarProvider>
</template>