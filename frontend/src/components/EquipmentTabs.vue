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
          <p>{{ selectedEquipment?.description }}</p>
        </div>
        <div v-show="activeTab === 'specification'" class="tabs-panel">
          <ul>
            <li v-for="(spec, index) in selectedEquipment?.specifications" :key="index" class="mb-2">
              {{ index + 1 }}. {{ spec.name }} ({{ spec.value }})
            </li>
          </ul>
        </div>
        <div v-show="activeTab === 'terms'" class="tabs-panel">
          <p>{{ selectedEquipment?.terms }}</p>
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
import useNotifications from '@/store/notification';

import axios from 'axios';

export default {
  setup() {
    const activeTab = ref('description');
    const route = useRoute();
    const api_base_url = import.meta.env.VITE_API_BASE_URL;
    const { showNotification } = useNotifications();

    const newReview = ref({
      rating: null,
      text: '',
    });

    const authStore = useAuthStore();
    const equipmentsStore = useEquipmentsStore();
    const selectedEquipment = computed(() => equipmentsStore.selectedEquipment);

    // Fetch equipment data on mount
    onMounted(async () => {
      try {
        await equipmentsStore.fetchEquipments();
        const equipmentId = route.params.id;

        if (!equipmentId) {
          throw new Error('Invalid equipment ID.');
        }

        const equipment = equipmentsStore.getEquipmentById(equipmentId);

        if (!equipment) {
          throw new Error('Equipment not found.');
        }
      } catch (error) {
        showNotification('Error', 'Failed to load equipment details. Please try again.', 'error');
      }
    });

    const submitReview = async () => {
      if (!authStore.isAuthenticated) {
        showNotification('Authentication Required', 'You need to log in to submit a review.', 'error');
        return;
      }

      if (!selectedEquipment.value || !selectedEquipment.value.id) {
        showNotification('Error', 'Equipment data is unavailable. Please try again later.', 'error');
        return;
      }

      const reviewData = {
        rating: newReview.value.rating,
        review_text: newReview.value.text.trim(),
        equipment: selectedEquipment.value.id,
      };

      try {
        const response = await axios.post(`${api_base_url}/api/reviews/`, reviewData, {
          withCredentials: true,
          timeout: 10000, // 10-second timeout
        });


        // Ensure `equipment_reviews` is an array before updating
        if (!Array.isArray(selectedEquipment.value.equipment_reviews)) {
          selectedEquipment.value.equipment_reviews = [];
        }

        // Check if response contains the review details
        if (response.data && (response.data.id || response.data.review_text)) {
          selectedEquipment.value.equipment_reviews.push(response.data);
          showNotification('Success', 'Thank you for reviewing the item!', 'success');
        } else {
          showNotification('Success', 'Thank you for rating the item!', 'success');
        }

        // Reset review form
        newReview.value.rating = null;
        newReview.value.text = '';

      } catch (error) {

        if (error.code === 'ECONNABORTED') {
          showNotification('Timeout Error', 'The request timed out. Please check your connection and try again.', 'error');
        } else if (error.response) {
          const { status, data } = error.response;

          if (status === 403 && data?.error) {
            showNotification('Permission Denied', data.error, 'error');
          } else if (status >= 500) {
            showNotification('Server Error', 'The server encountered an issue. Please try again later.', 'error');
          } else {
            showNotification('Review Error', data?.message || 'An error occurred while submitting your review.', 'error');
          }
        } else {
          showNotification('Unexpected Error', 'Something went wrong. Please try again later.', 'error');
        }
      }
    };


    // Safe date formatting
    const formatDate = (date) => {
      try {
        return format(new Date(date), 'PPPpp');
      } catch (error) {
        return 'Invalid Date';
      }
    };

    return {
      api_base_url,
      activeTab,
      newReview,
      selectedEquipment,
      submitReview,
      formatDate,
    };
  },
};
</script>
