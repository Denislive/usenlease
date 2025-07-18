<template>
  <div v-if="relatedEquipments.length" class="mt-6">
    <h3 class="text-lg font-semibold mb-3 text-gray-900">You May Also Like</h3>

    <!-- Grid Layout for Medium and Larger Screens -->
    <div v-if="!isSmallScreen" class="grid sm:grid-cols-3 md:grid-cols-6 lg:grid-cols-10 xl:grid-cols-10 gap-4">
      <div v-for="equipment in relatedEquipments" :key="equipment.id" class="bg-white p-2 rounded shadow-md h-full">
        <div class="relative">
          <span
            v-if="equipment.is_available"
            class="absolute top-0 left-0 bg-green-500 text-white text-[10px] sm:text-xs font-bold px-2 py-1 rounded"
          >
            Available
          </span>
          <span
            v-else
            class="absolute top-0 left-0 bg-blue-500 text-white text-[10px] sm:text-xs font-bold px-2 py-1 rounded cursor-pointer"
            @click="goToDetail(equipment.id)"
          >
          check details
          </span>

          <!-- Image or Placeholder -->
          <img
            v-if="equipment.images && equipment.images.length > 0"
            :src="equipment.images[0].image_url"
            :alt="`Image of ${equipment.name}`"
            class="w-full h-32 object-cover rounded-t-md"
            loading="lazy"
          />
          <div v-else class="w-full h-32 bg-gray-100 flex items-center justify-center rounded-t-md">
            <i class="pi pi-image text-4xl text-gray-400"></i>
          </div>
        </div>

        <div class="p-2">
          <h5 class="text-sm font-semibold mb-1 text-gray-900">
            {{ store.truncateText(equipment.name, 20) }}
          </h5>
          <p class="text-gray-600 text-xs sm:text-sm mb-2">{{ equipment.hourly_rate }} / Day</p>
          <button 
            @click="goToDetail(equipment.id)" 
            class="bg-[#ff6f00] rounded text-white text-xs sm:text-sm px-3 sm:px-4 py-1 sm:py-2 mt-2 transition duration-300 hover:bg-[#ff9e00] transform hover:scale-110"
          >
            Rent Now
          </button>
        </div>
      </div>
    </div>

    <!-- Paginated Layout for Small Screens -->
    <div v-else>
      <div class="grid grid-cols-3 gap-4">
        <div v-for="equipment in paginatedEquipments" :key="equipment.id" class="bg-white p-2 rounded shadow-md h-full">
          <div class="relative">
            <span
              v-if="equipment.is_available"
              class="absolute top-0 left-0 bg-green-500 text-white text-[10px] sm:text-xs font-bold px-2 py-1 rounded"
            >
              Available
            </span>
            <span
              v-else
              class="absolute top-0 left-0 bg-blue-500 text-white text-[10px] sm:text-xs font-bold px-2 py-1 rounded cursor-pointer"
              @click="goToDetail(equipment.id)"
            >
              Click to check details
            </span>

            <!-- Image or Placeholder -->
            <img
              v-if="equipment.images && equipment.images.length > 0"
              :src="equipment.images[0].image_url"
              :alt="equipment.name"
              class="w-full h-32 lg:h-48 object-cover rounded-t-md"
              loading="lazy"
            />
            <div v-else class="w-full h-32 lg:h-48 bg-gray-100 flex items-center justify-center rounded-t-md">
              <i class="pi pi-image text-4xl text-gray-400"></i>
            </div>
          </div>

          <div class="p-2">
            <h5 class="text-sm font-semibold mb-1 text-gray-900">
              {{ store.truncateText(equipment.name, 20) }}
            </h5>
            <p class="text-gray-600 text-xs sm:text-sm mb-2">{{ equipment.hourly_rate }} / Day</p>
            <button 
              @click="goToDetail(equipment.id)" 
              class="bg-[#ff6f00] rounded text-white text-xs sm:text-sm px-3 sm:px-4 py-1 sm:py-2 mt-2 transition duration-300 hover:bg-[#ff9e00] transform hover:scale-110"
            >
              Rent Now
            </button>
          </div>
        </div>
      </div>

      <!-- Pagination Controls (Only if there are more items to show) -->
      <div v-if="relatedEquipments.length > itemsPerPage" class="flex justify-between mt-4">
        <button
          @click="prev"
          :disabled="currentIndex === 0"
          class="bg-gray-300 text-gray-700 px-3 py-1 rounded disabled:opacity-50"
        >
          Previous
        </button>
        <button
          @click="next"
          :disabled="currentIndex + itemsPerPage >= relatedEquipments.length"
          class="bg-gray-300 text-gray-700 px-3 py-1 rounded disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useEquipmentsStore } from "@/store/equipments";

const store = useEquipmentsStore();
const route = useRoute();
const router = useRouter();
const relatedEquipments = computed(() => store.relatedEquipments);

// Track screen size
const isSmallScreen = ref(window.innerWidth < 640);

// Listen for screen resize
window.addEventListener("resize", () => {
isSmallScreen.value = window.innerWidth < 640;
});

// Pagination variables
const currentIndex = ref(0);
const itemsPerPage = ref(3);

const paginatedEquipments = computed(() => {
if (!isSmallScreen.value) return relatedEquipments.value;
return relatedEquipments.value.slice(currentIndex.value, currentIndex.value + itemsPerPage.value);
});

// Pagination functions
const next = () => {
if (currentIndex.value + itemsPerPage.value < relatedEquipments.value.length) {
  currentIndex.value += itemsPerPage.value;
}
};

const prev = () => {
if (currentIndex.value > 0) {
  currentIndex.value -= itemsPerPage.value;
}
};

const fetchRelatedItems = async () => {
const equipmentId = route.params.id;
if (equipmentId) {
  await store.fetchRelatedEquipments(equipmentId);
}
};

const goToDetail = (equipmentId) => {
if (equipmentId) {
  router.push({ name: "equipment-details", params: { id: equipmentId } });
}
};

// Fetch data when the component mounts
onMounted(fetchRelatedItems);

// Watch for route changes and refetch data
watch(() => route.params.id, fetchRelatedItems);
</script>
