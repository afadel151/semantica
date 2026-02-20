<script setup lang="ts">

</script>

<template>
    <SidebarProvider >
        <AppSidebar />
        <main class="w-full">
            <nav class="flex justify-between items-center p-4 w-full border-b">
                <SidebarTrigger />
                <ModeToggle />

            </nav>
            <slot />
        </main>
    </SidebarProvider>
</template>