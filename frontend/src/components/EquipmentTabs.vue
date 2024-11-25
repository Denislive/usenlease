<template>
  <div class="container mx-auto py-4">
    <!-- Tabs for Description, Specification, Terms, Reviews -->
    <div class="bg-white rounded-lg shadow-md">
      <ul class="flex border-b">
        <li class="mr-1">
          <a href="#" @click.prevent="activeTab = 'description'"
            :class="{ 'border-b-2 border-[#ffc107] font-semibold': activeTab === 'description', 'text-gray-600': activeTab !== 'description' }"
            class="inline-block py-2 px-2">Description</a>
        </li>
        <li class="mr-1">
          <a href="#" @click.prevent="activeTab = 'specification'"
            :class="{ 'border-b-2 border-[#ffc107] font-semibold': activeTab === 'specification', 'text-gray-600': activeTab !== 'specification' }"
            class="inline-block py-2 px-2">Specification</a>
        </li>
        <li class="mr-1">
          <a href="#" @click.prevent="activeTab = 'terms'"
            :class="{ 'border-b-2 border-[#ffc107] font-semibold': activeTab === 'terms', 'text-gray-600': activeTab !== 'terms' }"
            class="inline-block py-2 px-2">Terms</a>
        </li>
        <li>
          <a href="#" @click.prevent="activeTab = 'reviews'"
            :class="{ 'border-b-2 border-[#ffc107] font-semibold': activeTab === 'reviews', 'text-gray-600': activeTab !== 'reviews' }"
            class="inline-block py-2 px-2">Reviews</a>
        </li>
      </ul>

      <div class="p-4">
        <div v-show="activeTab === 'description'" class="tabs-panel">
          <p>{{ selectedEquipment?.description || 'Loading...' }}</p>
        </div>
        <div v-show="activeTab === 'specification'" class="tabs-panel">
          <ul>
            <li v-for="(spec, index) in selectedEquipment?.specifications" :key="index" class="mb-2">
              {{ index + 1 }}. {{ spec.name }} ({{ spec.value }})
            </li>
          </ul>
        </div>
        <div v-show="activeTab === 'terms'" class="tabs-panel">
          <p>{{ selectedEquipment?.terms || 'Loading...' }}</p>
        </div>
        <div v-show="activeTab === 'reviews'" class="tabs-panel">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Reviews Section -->
            <div class="mt-2 max-w-xl px-2">
              <h2 class="text-2xl text-gray-800 mb-2">Reviews</h2>
              <div v-if="selectedEquipment?.equipment_reviews.length > 0" class="space-y-6 rounded">
                <div v-for="(review, index) in selectedEquipment?.equipment_reviews" :key="index"
                  class="border p-2 rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 bg-gray-100">
                  <div class="flex items-center mb-2">
                    <strong class="text-xs">{{ review.user }}</strong>
                    <span class="ml-2 text-sm text-gray-500">{{ formatDate(review.date_created) }}</span>
                  </div>
                  <p class="text-gray-700 text-base">{{ review.review_text }}</p>
                </div>
              </div>
              <div v-else>
                <p class="text-center text-lg text-gray-500">No reviews yet. Be the first to review!</p>
              </div>
            </div>

            <!-- Add Review Section -->
            <div class="mt-2">
              <h3 class="text-2xl text-gray-800 mb-2">Add a Review</h3>
              <form @submit.prevent="submitReview" class="space-y-4">
                <!-- Review Text Section -->
                <div>
                  <label for="review-text" class="block text-sm font-medium text-gray-700">Review Text</label>
                  <textarea id="review-text" v-model="newReview.text"
                    class="w-full p-2 border border-gray-300 rounded-md focus:outline-none" rows="3"
                    placeholder="Write your review..."></textarea>
                </div>

                <!-- Rating Section -->
                <div>
                  <label for="rating" class="block text-sm font-medium text-gray-700">Rating</label>
                  <div class="flex items-center space-x-1">
                    <template v-for="star in 5" :key="star">
                      <i @click="newReview.rating = star" :class="[
                        'pi',
                        star <= newReview.rating ? 'pi-star-fill text-yellow-400' : 'pi-star text-gray-300',
                        'text-xl cursor-pointer'
                      ]"></i>
                    </template>
                  </div>
                </div>

                <!-- Submit Button -->
                <div class="flex justify-end">
                  <button type="submit" class="px-4 py-2 bg-[#1c1c1c] text-white rounded-lg">Submit Review</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useEquipmentsStore } from '@/store/equipments';
import { format } from 'date-fns';
import { useRoute } from 'vue-router';
import { useAuthStore } from '@/store/auth';

import axios from 'axios';

export default {
  setup() {
    const activeTab = ref('description');
    const route = useRoute();
    const newReview = ref({
      rating: null,
      text: ''
    });

    const authStore = useAuthStore();
    const equipmentsStore = useEquipmentsStore();
    const selectedEquipment = computed(() => equipmentsStore.selectedEquipment);

    onMounted(() => {
      equipmentsStore.fetchEquipments();
      const equipmentId = route.params.id;
      equipmentsStore.getEquipmentById(equipmentId);
    });
    const submitReview = async () => {
  if (!authStore.isAuthenticated) {
    console.log("User is not authenticated");
    // Optionally redirect to login or display an authentication prompt
    return;
  }

  try {
    // Prepare the review data payload
    const reviewData = {
      rating: newReview.value.rating,
      review_text: newReview.value.text,
      equipment: selectedEquipment.value.id, // Assuming `selectedEquipment` has the `id`
    };

     // Check for null or empty fields
  if (!reviewData.rating || !reviewData.equipment) {
    console.error("All fields are required.");
    alert("Please complete all fields before submitting your review.");
    return;
  }

    // Send a POST request to submit the review
    const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/reviews/`, reviewData, {
      withCredentials: true, // Send cookies for authentication if needed
    });

    // Log success and handle the response as needed
    console.log("Review submitted successfully:", response.data);

    // Optionally update the reviews list in the UI
    equipmentsStore.fetchEquipments(); // Re-fetch equipment data if reviews are part of it

    // Reset the review form
    newReview.value.rating = null;
    newReview.value.text = '';

  } catch (error) {
    console.error("Error submitting review:", error);
    // Optionally display an error message to the user
  }
};

    const formatDate = (date) => {
      try {
        return format(new Date(date), 'PPPpp');
      } catch (error) {
        return 'Invalid Date';
      }
    };

    return {
      activeTab,
      newReview,
      selectedEquipment,
      submitReview,
      formatDate,
    };
  }
};
</script>
