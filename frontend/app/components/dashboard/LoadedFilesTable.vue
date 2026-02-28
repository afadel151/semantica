<script setup lang="ts">
import type { LoadedFile } from '~/types/loaded_files';

defineProps<{
    data: Array<LoadedFile>
}>()

const getBadgeVariant = (type: string) => {
    return type == 'RDF' ? 'primary' : 'secondary'
}

import {
    Table,
    TableBody,
    TableCaption,
    TableCell,
    TableFooter,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'
import { CirclePlus, DiamondPlus, Eye, Trash } from 'lucide-vue-next';

</script>

<template>
    <div class=" rounded-xl p-4 shadow-sm border ">
        <div class="flex items-center justify-between mb-3">
            <p class="text-sm font-semibold text-gray-700 dark:text-gray-100">Loaded Files</p>
            <div class="flex gap-2">
                <Button>
                    <CirclePlus/>
                    Load RDF
                </Button>
                <Button variant="outline">
                    <DiamondPlus />
                    Load Ontology
                </Button>
            </div>
        </div>
        <Table>

            <TableCaption>A list of your recent files.</TableCaption>
            <TableHeader>
                <TableRow>
                    <TableHead>
                        Name
                    </TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Format</TableHead>
                    <TableHead>Triples</TableHead>
                    <TableHead>Uploaded</TableHead>
                    <TableHead class="text-right ">
                        Actions
                    </TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                <TableRow v-for="file in data" :key="file.name">
                    <TableCell class="font-medium">
                        {{ file.name }}
                    </TableCell>
                    <TableCell>
                        <Badge :variant="file.type == 'RDF' ? 'rdf' : 'ontology'">
                            {{ file.type }}
                        </Badge>
                    </TableCell>
                    <TableCell>{{ file.format }}</TableCell>
                    <TableCell>
                        {{ file.triples }}
                    </TableCell>
                    <TableCell> {{ file.uploaded }}</TableCell>
                    <TableCell>
                        <div class="flex items-center space-x-2 justify-end">
                            <Button variant="secondary">
                                <Eye/>
                                Show
                            </Button>
                            <Button variant="destructive">
                                <Trash/>
                                Delete
                            </Button>
                        </div>
                    </TableCell>
                </TableRow>
            </TableBody>

        </Table>
    </div>
</template>
