<script setup>
import { ref, watch } from "vue";
import { useCompanyInfoStore } from "@/store/company";

// Fetch company info
const companyStore = useCompanyInfoStore();
const companyInfo = ref(null); // Initialize as null

// Fetch data and update companyInfo
companyStore.fetchCompanyInfo();
watch(
    () => companyStore.companyInfo,
    (newInfo) => {
        if (newInfo) {
            companyInfo.value = newInfo; // Assign the value when available
        }
    },
    { immediate: true }
);
</script>

<template>
    <div class="min-h-screen bg-gray-100 text-gray-800">
        <div class="max-w-4xl mx-auto py-8 px-4">
            <!-- Page Header -->
            <h1 class="text-2xl font-bold mb-4">Terms and Conditions</h1>

            <!-- Intro Section -->
            <div v-if="companyInfo" class="bg-gray-200 p-4 rounded-md shadow-md mb-6">
                <p class="text-sm">
                    Welcome to {{ companyInfo.name || "our website" }}. These terms and conditions outline the rules and
                    regulations for the use of our services. Please read them carefully before accessing or using our
                    services.
                </p>
            </div>

            <!-- Terms Content -->
            <section v-if="companyInfo" class="space-y-4">
            
                <div>
                    <p v-html="companyInfo.terms_and_conditions || fallbackText"></p>
                </div>

            </section>

            <!-- Loading State -->
            <p v-else class="text-center text-gray-500">
                Loading terms and conditions...
            </p>

            <!-- Footer -->
            <div class="mt-8" v-if="companyInfo">
                <p class="text-sm">
                    If you have any questions about these terms, please contact us at
                    <a :href="`mailto:support@${companyInfo.name?.toLowerCase().replace(/\s+/g, '') || 'example'}.com`"
                        class="underline text-blue-500 hover:text-blue-700">
                        support@{{ companyInfo.name?.toLowerCase().replace(/\s+/g, '') || 'example' }}.com
                    </a>.
                </p>
            </div>
        </div>
    </div>
</template>

<style scoped>
a {
    transition: color 0.3s ease;
}
</style>
