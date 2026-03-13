<script setup>
import { Play, Plus, Trash2, Loader2, Wand2 } from 'lucide-vue-next';
import { useSparqlState, useSparqlActions } from '~/composables/useSparql';

const { activeGraphId, query, isRunning, updateResult } = useSparqlState();
const { generateUpdate, runUpdateQuery } = useSparqlActions();

const mode = ref('insert');

const manualSubject = ref('');
const manualPredicate = ref('');
const manualObject = ref('');
const isObjectLiteral = ref(true);

const isGenerating = ref(false);
const isExecuting = ref(false);
const successMessage = ref('');
const errorMessage = ref('');

async function handleAutoGenerate() {
    isGenerating.value = true;
    successMessage.value = '';
    errorMessage.value = '';
    try {
        await generateUpdate(mode.value);
    } catch (e) {
        errorMessage.value = 'Génération échouée';
    } finally {
        isGenerating.value = false;
    }
}

function buildManualQuery() {
    const s = manualSubject.value.trim();
    const p = manualPredicate.value.trim();
    const o = manualObject.value.trim();

    if (!s || !p || !o) return;

    const sStr = s.startsWith('http') || s.startsWith('urn:') ? `<${s}>` : s;
    const pStr = p.startsWith('http') || p.startsWith('urn:') ? `<${p}>` : p;
    const oStr = isObjectLiteral.value
        ? `"${o}"`
        : o.startsWith('http') || o.startsWith('urn:') ? `<${o}>` : o;

    if (mode.value === 'insert') {
        query.value = `INSERT DATA {\n  ${sStr} ${pStr} ${oStr} .\n}`;
    } else {
        query.value = `DELETE DATA {\n  ${sStr} ${pStr} ${oStr} .\n}`;
    }
}

async function handleExecute() {
    if (!query.value.trim() || !activeGraphId.value) return;
    isExecuting.value = true;
    successMessage.value = '';
    errorMessage.value = '';
    try {
        await runUpdateQuery(query.value);
        if (updateResult.value?.success) {
            successMessage.value = `✅ ${updateResult.value.triples_added} triplet(s) ajouté(s), ${updateResult.value.triples_removed} supprimé(s)`;
        }
    } catch (e) {
        errorMessage.value = 'Erreur lors de l\'exécution';
    } finally {
        isExecuting.value = false;
    }
}

watchEffect(() => {
    if (updateResult.value?.success) {
        successMessage.value = `✅ Succès — +${updateResult.value.triples_added} / -${updateResult.value.triples_removed} triplets`;
    }
});
</script>

<template>
    <div class="space-y-4 w-full">
        <!-- Avertissement si pas de graphe -->
        <div v-if="!activeGraphId"
            class="text-xs text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 rounded-lg px-3 py-2">
            ⚠️ Aucun graphe actif — les UPDATE nécessitent un graphe actif.
        </div>

        <!-- Sélecteur de mode -->
        <div class="flex gap-2">
            <button
                @click="mode = 'insert'"
                :class="[
                    'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors',
                    mode === 'insert'
                        ? 'bg-emerald-500 text-white border-emerald-500'
                        : 'border-gray-200 dark:border-gray-700 text-muted-foreground hover:bg-muted'
                ]"
            >
                <Plus class="w-3 h-3" /> INSERT
            </button>
            <button
                @click="mode = 'delete'"
                :class="[
                    'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors',
                    mode === 'delete'
                        ? 'bg-red-500 text-white border-red-500'
                        : 'border-gray-200 dark:border-gray-700 text-muted-foreground hover:bg-muted'
                ]"
            >
                <Trash2 class="w-3 h-3" /> DELETE
            </button>
        </div>

        <!-- Formulaire manuel -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-2">
            <div class="flex flex-col gap-1">
                <label class="text-xs font-medium text-muted-foreground">Sujet (URI)</label>
                <input
                    v-model="manualSubject"
                    type="text"
                    placeholder="ex: http://example.org/Alice"
                    class="w-full px-2 py-1.5 text-xs rounded-md border border-gray-200 dark:border-gray-700 bg-background focus:outline-none focus:ring-1 focus:ring-primary font-mono"
                />
            </div>
            <div class="flex flex-col gap-1">
                <label class="text-xs font-medium text-muted-foreground">Prédicat (URI)</label>
                <input
                    v-model="manualPredicate"
                    type="text"
                    placeholder="ex: foaf:name"
                    class="w-full px-2 py-1.5 text-xs rounded-md border border-gray-200 dark:border-gray-700 bg-background focus:outline-none focus:ring-1 focus:ring-primary font-mono"
                />
            </div>
            <div class="flex flex-col gap-1">
                <div class="flex items-center justify-between">
                    <label class="text-xs font-medium text-muted-foreground">Objet</label>
                    <label class="flex items-center gap-1.5 text-[10px] text-muted-foreground cursor-pointer">
                        <input type="checkbox" v-model="isObjectLiteral" class="accent-primary" />
                        Littéral
                    </label>
                </div>
                <input
                    v-model="manualObject"
                    type="text"
                    :placeholder="isObjectLiteral ? 'ex: Alice' : 'ex: http://example/P'"
                    class="w-full px-2 py-1.5 text-xs rounded-md border border-gray-200 dark:border-gray-700 bg-background focus:outline-none focus:ring-1 focus:ring-primary font-mono"
                />
            </div>
        </div>

        <!-- Boutons d'action -->
        <div class="flex flex-wrap gap-2">
            <Button
                size="sm"
                variant="outline"
                class="text-xs"
                @click="buildManualQuery"
                :disabled="!manualSubject || !manualPredicate || !manualObject"
            >
                <Wand2 class="w-3 h-3 mr-1" /> Insérer dans l'éditeur
            </Button>
            <Button
                size="sm"
                variant="outline"
                class="text-xs"
                @click="handleAutoGenerate"
                :disabled="!activeGraphId || isGenerating"
            >
                <Loader2 v-if="isGenerating" class="w-3 h-3 mr-1 animate-spin" />
                <Wand2 v-else class="w-3 h-3 mr-1" />
                Auto-générer depuis graphe
            </Button>
            <Button
                size="sm"
                :class="mode === 'insert' ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-red-600 hover:bg-red-700'"
                class="text-white text-xs border-0"
                @click="handleExecute"
                :disabled="!activeGraphId || isExecuting || isRunning || !query"
            >
                <Loader2 v-if="isExecuting" class="w-3 h-3 mr-1 animate-spin" />
                <Play v-else class="w-3 h-3 mr-1" />
                Exécuter UPDATE direct
            </Button>
        </div>

        <!-- Messages retour -->
        <p v-if="successMessage" class="text-xs text-emerald-600 dark:text-emerald-400 font-medium">
            {{ successMessage }}
        </p>
        <p v-if="errorMessage" class="text-xs text-red-500 font-medium">
            ❌ {{ errorMessage }}
        </p>
    </div>
</template>
