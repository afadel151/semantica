<script setup>
import { ArrowUpToLine } from 'lucide-vue-next'
import { mapQueryToVariant } from '~/types/badge_variant';
import { useSparqlState, useSparqlActions } from '~/composables/useSparql';

const { history } = useSparqlState();
const { loadFromHistory } = useSparqlActions();
</script>

<template>
  <Card class="w-full">
    <CardHeader>
      <CardTitle>Requêtes récentes</CardTitle>
    </CardHeader>
    <CardContent>
      <Table>
        <TableBody>
          <TableRow v-for="h in history.slice(0,5)" :key="h.id || h.query">
            <TableCell>
              <Badge :variant="mapQueryToVariant(h.query_type)">{{ h.query_type }}</Badge>
            </TableCell>
            <TableCell class="max-w-75 truncate" :title="h.query">
              {{ h.query }}
            </TableCell>
            <TableCell class="flex justify-end gap-2">
              <Button variant="outline" @click="loadFromHistory(h)" size="sm">
                <ArrowUpToLine class="w-4 h-4 mr-1" /> Charger
              </Button>
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
      <p v-if="history.length === 0" class="text-xs text-gray-400 text-center py-2">Aucune requête récente</p>
    </CardContent>
  </Card>
</template>
