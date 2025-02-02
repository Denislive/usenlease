<template>
    <div class="min-h-screen bg-gray-100 text-gray-800">
        <div class="max-w-4xl mx-auto py-8 px-4">
            <!-- Page Header -->
            <h1 class="text-2xl font-bold mb-4">Privacy Notice</h1>
            <!-- Notice Section -->
            <div class="bg-gray-800 text-white p-4 rounded-md shadow-md">
                <h3 class="text-lg font-semibold">We Value Your Privacy</h3>
                <p class="text-sm mt-2">
                    This website uses cookies to enhance your experience. By continuing to use this site, you agree to
                    our use of cookies.
                </p>
            </div>

            <!-- Privacy Message -->
            <!-- Privacy Message -->
            <p v-if="cookieInfo" class="text-lg mb-4" v-html="cookieInfo.privacy_cookie_notice">
            </p>
            <p v-else class="text-lg mb-4">
                The privacy notice will be updated soon.
            </p>

        </div>
    </div>
</template>

<script>
import { ref, onMounted, watch } from "vue";
import { useCompanyInfoStore } from "@/store/company";

export default {
    name: "PrivacyCookiePage",
    setup() {
        const companyStore = useCompanyInfoStore();
        const cookieInfo = ref(null);

        // Fetch company info when the component is mounted
        onMounted(async () => {
            await companyStore.fetchCompanyInfo();
            cookieInfo.value = companyStore.companyInfo;
        });

        // Watch for updates to company info
        watch(
            () => companyStore.companyInfo,
            (newInfo) => {
                if (newInfo) {
                    cookieInfo.value = newInfo;
                }
            },
            { immediate: true }
        );

        return {
            cookieInfo,
        };
    },
};
</script>

<style scoped>
a {
    transition: color 0.3s ease;
}
</style>