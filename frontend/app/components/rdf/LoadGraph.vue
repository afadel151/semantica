<script setup>
import { PlusCircle } from 'lucide-vue-next';

const emit = defineEmits(['uploaded', 'error'])


const file_name = ref('')
const file = ref(null)
const error = ref('')

const handleFileUpload = (event) => {
    file.value = event.target.files[0];
};
const config = useRuntimeConfig()

const loadFile = async () => {
    if (!file.value || file_name.value === '') {
        error.value = 'All fields must be set'
        return
    }
    try {
        const form = new FormData()
        form.append('name', file_name.value)
        form.append('file', file.value)
        await $fetch(`${config.public.apiBase}/rdf/upload`, {  
            method: 'POST',
            body: form
        })
        emit('uploaded')
    } catch (err) {
        error.value = 'Upload failed'
        emit('error')
    }
}
</script>

<template>
    <Dialog>
        <DialogTrigger as-child>
            <Button>
                <PlusCircle />
                Upload Graph
            </Button>
        </DialogTrigger>
        <DialogContent class="sm:max-w-[425px]">
            <DialogHeader>
                <DialogTitle>Upload a graph file</DialogTitle>
            </DialogHeader>
            <div class="grid gap-4">
                <div class="grid gap-3">
                    <Label for="name-1">File Name</Label>
                    <Input v-model="file_name" default-value="new_file" />
                </div>
                <div class="grid gap-3">
                    <Label for="username-1">File</Label>
                    <Input type="file" @change="handleFileUpload" />
                </div>
            </div>
            {{ error }}
            <DialogFooter>
                <DialogClose as-child>
                    <Button variant="outline">
                        Cancel
                    </Button>
                </DialogClose>
                <DialogClose as-child>

                    <Button type="submit" @click="loadFile">
                        Upload
                    </Button>
                </DialogClose>
            </DialogFooter>
        </DialogContent>
    </Dialog>
</template>
