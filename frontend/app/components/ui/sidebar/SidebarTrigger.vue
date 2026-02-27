<script setup lang="ts">
import type { HTMLAttributes } from "vue"
import { PanelLeft } from "lucide-vue-next"
import { cn } from "@/lib/utils"
import { Button } from '@/components/ui/button'
import { useSidebar } from "./utils"

const props = defineProps<{
  class?: HTMLAttributes["class"],
  title?: string | unknown,
}>()

const { toggleSidebar } = useSidebar()
</script>

<template>
  <div class="flex items-center">

    <Button
    data-sidebar="trigger"
    data-slot="sidebar-trigger"
    variant="ghost"
    size="icon"
    :class="cn('h-7 w-7', props.class)"
    @click="toggleSidebar"
    >
    <PanelLeft />
    <span class="sr-only">Toggle Sidebar</span>
    
  </Button>
    <p class="text-lg  ml-5 font-bold">{{ title }}</p>
</div>
</template>
