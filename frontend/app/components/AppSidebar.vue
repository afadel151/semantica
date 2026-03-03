<script setup lang="ts">
import { Brain, Calendar, ChevronRight, Home, Inbox, Play, Scale, Search, Settings, Workflow } from 'lucide-vue-next'
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/components/ui/sidebar'

const router = useRouter()
// Menu items.  
const items = [
  {
    title: 'Dashboard',
    url: '/',
    icon: Home,
  },
  {
    title: 'Graphs',
    url: '/rdf',
    icon: Workflow,
  },
  {
    title: 'Ontologies',
    url: '/ontology',
    icon: Scale,
  },
  {
    title: 'SPARQL',
    url: '/sparql',
    icon: Play,
  },
  {
    title: 'Reasoning',
    url: '/reasoning',
    icon: Brain,
  },
]
</script>

<template>
  <Sidebar variant="floating" collapsible="icon">
    <SidebarContent>
      <SidebarGroup>
        <SidebarGroupLabel>Application</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in items" :key="item.title">
              <SidebarMenuButton as-child>
                <NuxtLink :to="item.url" 
                class="sidebar-link"
                active-class="bg-secondary"
                exact-active-class="bg-secondary"
                >
                  <component :is="item.icon" />
                  <span>{{ item.title }}</span>
                </NuxtLink>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
      <SidebarGroup>
        <SidebarGroupContent>
          <SidebarGroupLabel>Active graph and ontologies</SidebarGroupLabel>
          <SidebarMenuItem>
              <SidebarMenuButton>
                <Workflow />
                Active Graph
              </SidebarMenuButton>
              <SidebarMenuSub>
                <SidebarMenuSubItem>
                  <SidebarMenuSubButton as-child>
                    <a class="flex items-center justify-between w-full" href="#">
                      <span>file.rdf</span>
                      <span class="h-2 w-2 rounded-full bg-green-400 ml-2"></span>
                    </a>
                  </SidebarMenuSubButton>
                </SidebarMenuSubItem>
              </SidebarMenuSub>
          </SidebarMenuItem>
          <Collapsible as-child class="group/collapsible">
            <SidebarMenuItem>
              <CollapsibleTrigger as-child>
                <SidebarMenuButton>
                  <Scale/>
                  <span>Active Ontologies</span>
                  <ChevronRight
                    class="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />
                </SidebarMenuButton>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <SidebarMenuSub>
                  <SidebarMenuSubItem >
                    <SidebarMenuSubButton as-child>
                      <a class="flex items-center justify-between w-full" href="#">
                        <span>file.owl</span>
                        <span class="h-2 w-2 rounded-full bg-green-400 ml-2"></span>
                      </a>
                    </SidebarMenuSubButton>
                  </SidebarMenuSubItem>
                </SidebarMenuSub>
                <SidebarMenuSub>
                  <SidebarMenuSubItem >
                    <SidebarMenuSubButton as-child>
                      <a class="flex items-center justify-between w-full" href="#">
                        <span>file3.owl</span>
                        <span class="h-2 w-2 rounded-full bg-green-400 ml-2"></span>
                      </a>
                    </SidebarMenuSubButton>
                  </SidebarMenuSubItem>
                </SidebarMenuSub>
              </CollapsibleContent>
            </SidebarMenuItem>

          </Collapsible>
          
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>
  </Sidebar>
</template>
