<script setup lang="ts">
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import { Trash } from 'lucide-vue-next';
const config = useRuntimeConfig()

const emit = defineEmits(['deleted', 'error'])


defineProps<{
    onto_id: string
}>()

const deleteGraph = async (id: string) => {
    try {
        const res: any = await $fetch(`${config.public.apiBase}/ontology/${id}`, {
            method: 'DELETE'
        });
        if (res) {
            emit("deleted")
        }
    } catch (error) {
        emit("error")
    }

}
</script>

<template>
    <AlertDialog>
        <AlertDialogTrigger>
            <Button variant="destructive">
                <Trash />
                Delete
            </Button>
        </AlertDialogTrigger>
        <AlertDialogContent>
            <AlertDialogHeader>
                <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                <AlertDialogDescription>
                    This action cannot be undone. This will delete the ontology
                    and remove your data from our servers.
                </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction @click="deleteGraph(onto_id)">Delete</AlertDialogAction>
            </AlertDialogFooter>
        </AlertDialogContent>
    </AlertDialog>
</template>
