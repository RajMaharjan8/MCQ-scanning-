<template>
    <div>
        <label
            for="file-upload"
            class="cursor-pointer inline-block rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
            Choose File
        </label>
        <input
            id="file-upload"
            type="file"
            class="hidden"
            @change="handleFileChange"
        />
        <span v-if="fileName" class="ml-3 text-gray-700">{{ fileName }}</span>
    </div>
</template>

<script>
import { defineComponent } from 'vue';
export default defineComponent({
    
})
</script>