<script setup>
import { ref, computed } from 'vue'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { CirclePlus, ChevronUp, ChevronDown, ChevronsUpDown, ChevronLeft, ChevronRight, ChartNoAxesColumn, Eye, Trash } from 'lucide-vue-next'

const props = defineProps({
    ontologies: {
        type: Array,
        default: () => [
            {
                id: 'id1',
                name: 'ontolody.owl',
                format: 'OWL',
                classes: '32',
                properties: '50',
                individuals: '50',
                uploaded: '20-02-2026',
                status: 'active'
            },
            {
                id: 'id2',
                name: 'ontolody.rdfs',
                format: 'RDFS',
                classes: '32',
                properties: '50',
                individuals: '50',
                uploaded: '21-02-2026',
                status: 'inactive'
            },

        ]
    }
})

// sort
const sortKey = ref(null)
const sortOrder = ref('asc')

const columns = [
    { key: 'name', label: 'Name' },
    { key: 'format', label: 'Format' },
    { key: 'classes', label: 'Classes' },
    { key: 'properties', label: 'Properties' },
    { key: 'individuals', label: 'Individuals' },
    { key: 'uploaded', label: 'Uploaded' },
    { key: 'status', label: 'Status' },
]

function toggleSort(key) {
    if (sortKey.value === key) {
        sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
        sortKey.value = key
        sortOrder.value = 'asc'
    }
    currentPage.value = 1
}

const sortedOntologies = computed(() => {
    if (!sortKey.value) return props.ontologies

    return [...props.ontologies].sort((a, b) => {
        const valA = a[sortKey.value]
        const valB = b[sortKey.value]

        if (valA == null) return 1
        if (valB == null) return -1

        const result = typeof valA === 'number'
            ? valA - valB
            : String(valA).localeCompare(String(valB))

        return sortOrder.value === 'asc' ? result : -result
    })
})
// pagination
const pageSize = ref(10)
const currentPage = ref(1)
const pageSizeOptions = [5, 10, 20, 50]

const totalPages = computed(() => Math.max(1, Math.ceil(sortedOntologies.value.length / pageSize.value)))

const paginatedOntologies = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value
    return sortedOntologies.value.slice(start, start + pageSize.value)
})

function goToPage(page) {
    currentPage.value = Math.min(Math.max(1, page), totalPages.value)
}

function onPageSizeChange(e) {
    pageSize.value = Number(e.target.value)
    currentPage.value = 1
}

const visiblePages = computed(() => {
    const total = totalPages.value
    const current = currentPage.value
    const delta = 2
    const pages = []
    for (let i = Math.max(1, current - delta); i <= Math.min(total, current + delta); i++) {
        pages.push(i)
    }
    return pages
})
</script>

<template>
    <div class="rounded-xl p-4 shadow-sm border">
        <div class="flex items-center justify-between mb-3">
            <p class="text-sm font-semibold text-gray-700 dark:text-gray-100">All Ontologies</p>
            <Button>
                <CirclePlus class="mr-1.5 h-4 w-4" />
                Load Ontology
            </Button>
        </div>

        <Table>
            <TableCaption>A list of your recent RDF files.</TableCaption>
            <TableHeader>
                <TableRow>
                    <TableHead v-for="col in columns" :key="col.key"
                        class="cursor-pointer select-none whitespace-nowrap" @click="toggleSort(col.key)">
                        <span class="inline-flex items-center gap-1">
                            {{ col.label }}
                            <ChevronUp v-if="sortKey === col.key && sortOrder === 'asc'"
                                class="h-3.5 w-3.5 text-primary" />
                            <ChevronDown v-else-if="sortKey === col.key && sortOrder === 'desc'"
                                class="h-3.5 w-3.5 text-primary" />
                            <ChevronsUpDown v-else class="h-3.5 w-3.5 text-muted-foreground opacity-50" />
                        </span>
                    </TableHead>
                    <TableHead class="text-right">Actions</TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                <TableRow v-if="paginatedOntologies.length === 0">
                    <TableCell :colspan="columns.length + 1" class="text-center text-muted-foreground py-8">
                        No ontologies loaded yet.
                    </TableCell>
                </TableRow>
                <TableRow v-for="ontology in paginatedOntologies" :key="ontology.id ?? ontology.name">
                    <TableCell v-for="col in columns" :key="col.key">
                        {{ ontology[col.key] ?? '—' }}
                    </TableCell>
                    <TableCell class="text-right  space-x-2 justify-end">
                        <NuxtLink :to="'/ontologies/'+ ontology.id">
                            <Button>
                                <Eye />
                                Show
                            </Button>
                        </NuxtLink>
                        <Button variant="destructive">
                            <Trash />
                            Delete
                        </Button>
                    </TableCell>
                </TableRow>
            </TableBody>
        </Table>

        <div class="flex items-center justify-between mt-3 gap-2 flex-wrap">
            <div class="flex items-center gap-2 text-sm text-muted-foreground">
                <span>Rows per page</span>
                <select :value="pageSize" class="rounded border px-2 py-1 text-sm bg-background"
                    @change="onPageSizeChange">
                    <option v-for="n in pageSizeOptions" :key="n" :value="n">{{ n }}</option>
                </select>
            </div>

            <div class="flex items-center gap-1 text-sm">
                <span class="text-muted-foreground mr-2">
                    {{ sortedOntologies.length === 0 ? '0' : (currentPage - 1) * pageSize + 1 }}–{{ Math.min(currentPage *
                        pageSize, sortedOntologies.length) }}
                    of {{ sortedOntologies.length }}
                </span>

                <Button variant="outline" size="icon" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">
                    <ChevronLeft class="h-4 w-4" />
                </Button>

                <template v-if="visiblePages[0] > 1">
                    <Button variant="outline" size="icon" @click="goToPage(1)">1</Button>
                    <span v-if="visiblePages[0] > 2" class="px-1 text-muted-foreground">…</span>
                </template>

                <Button v-for="page in visiblePages" :key="page"
                    :variant="page === currentPage ? 'secondary' : 'outline'" size="icon" @click="goToPage(page)">
                    {{ page }}
                </Button>

                <template v-if="visiblePages[visiblePages.length - 1] < totalPages">
                    <span v-if="visiblePages[visiblePages.length - 1] < totalPages - 1"
                        class="px-1 text-muted-foreground">…</span>
                    <Button variant="outline" size="icon" @click="goToPage(totalPages)">{{ totalPages }}</Button>
                </template>

                <Button variant="outline" size="icon" :disabled="currentPage === totalPages"
                    @click="goToPage(currentPage + 1)">
                    <ChevronRight class="h-4 w-4" />
                </Button>
            </div>
        </div>
    </div>
</template>