<template>
    <h1 class="mx-2">Doc FILE</h1>
    <form @submit.prevent="submit">
        <Input id="picture" type="file" @change="onFileChange" />
        <button
            type="submit"
            class="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded"
        >
            Submit
        </button>
    </form>

    <draggable
        v-model="questions"
        tag="div"
        item-key="id"
        :animation="200"
        @change="onDragChange"
    >
        <template #item="{ element: ques, index: quesIndex }">
            <div class="mb-4 p-4 border rounded shadow-sm bg-white">
                <h2 class="font-semibold mb-2"> {{ques.order}} {{ ques.question }}</h2>
                <div
                    v-for="(opt, optIndex) in ques.options"
                    :key="optIndex"
                    class="di"
                >
                    <input
                        type="radio"
                        class="mx-2"
                        :name="'question_' + quesIndex"
                        :value="opt"
                        v-model="answers[quesIndex]"
                        :id="'q' + quesIndex + '_opt' + optIndex"
                    />
                    <label :for="'q' + quesIndex + '_opt' + optIndex">{{
                        opt
                    }}</label>
                </div>
            </div>
        </template>
    </draggable>

    <button
        type="submit"
        class="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded"
        @click="saveAnswers"
    >
        Save Answers
    </button>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import Input from "@/components/ui/input/Input.vue";
import axios from "axios";
import draggable from "vuedraggable";

const form = reactive({
    file: null,
});
const questions = ref([]);
const answers = reactive({});

onMounted(() => {
    getQuestions();
});

const getQuestions = async () => {
    try {
        const res = await axios.get(route("get.post"));
        questions.value = res.data;

        questions.value.forEach((ques, index)=>{
            answers[index] = ques.answer || null;
        })
        console.log("question:", JSON.stringify(questions.value));
    } catch (error) {
        console.error("Failed to fetch questions:", error);
    }
};

const onFileChange = (event) => {
    const file = event.target.files[0];
    form.file = file;
};

const submit = async () => {
    if (!form.file) {
        alert("Please select a file first.");
        return;
    }

    const formData = new FormData();
    formData.append("file", form.file);

    try {
        const response = await axios.post(route("file.post"), formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        });
        console.log("response:", response.data);
        await getQuestions();
    } catch (error) {
        console.error("Upload failed:", error);
    }
};

const onDragChange = async () => {
    questions.value.forEach((question, index) => {
        question.order = index + 1;
    });

    const payload = questions.value.map(({ id, order }) => ({ id, order }));
    try {
        const response = await axios.post(route("reorder.post"), {
            questions: payload,
        });
        console.log("Reorder saved:", response.data);
        await getQuestions();
    } catch (error) {
        console.error("Failed to save reorder:", error);
    }

    console.log("Updated questions order:", questions.value);
};

const saveAnswers = async () => {
    try {
        const payload = questions.value.map((question, index) => ({
            question_id: question.id,
            answer: answers[index] || null,
        }));
        const res = await axios.post(route("save.post"), { answers: payload });
        await getQuestions();
    } catch (error) {
        console.error(error);
    }
};
</script>
