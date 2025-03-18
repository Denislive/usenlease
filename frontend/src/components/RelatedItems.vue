<template>
    <div v-if="relatedEquipments.length" class="mt-6">
      <h3 class="text-lg font-semibold mb-3 text-gray-900">You May Also Like</h3>
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-8 xl:grid-cols-10 gap-4">
        <div v-for="equipment in relatedEquipments" :key="equipment.id" class="bg-white p-2 rounded shadow-md">
          <div class="relative">
            <span
              v-if="equipment.is_available"
              class="absolute top-0 left-0 bg-green-500 text-white text-[10px] sm:text-xs font-bold px-2 py-1 rounded"
            >
              Available
            </span>
            <span
              v-else
              class="absolute top-0 left-0 bg-blue-500 text-white text-[10px] sm:text-xs font-bold px-2 py-1 rounded"
              @click="goToDetail(equipment.id)"
            >
              Click to check details
            </span>
  
            <img
              v-if="equipment.images.length > 0"
              :src="equipment.images[0].image_url"
              alt="Equipment Image"
              class="w-full h-32 lg:h-48 object-contain"
            />
            <img
              v-else
              src="https://via.placeholder.com/350"
              alt="Placeholder Image"
              class="w-full h-32 object-contain"
            />
          </div>
  
          <div class="p-1">
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
    </div>
  </template>
  
  <script setup>
  import { onMounted, computed } from "vue";
  import { useRoute, useRouter } from "vue-router";
  import { useEquipmentsStore } from "@/store/equipments";
  
  const store = useEquipmentsStore();
  const route = useRoute();
  const router = useRouter();
  const relatedEquipments = computed(() => store.relatedEquipments);

  const fetchRelatedItems = async () => {
    const equipmentId = route.params.id; // Extracting ID from the URL
    if (equipmentId) {
      await store.fetchRelatedEquipments(equipmentId);
    }
  };
  
  const goToDetail = (equipmentId) => {
  if (equipmentId) {
    router.push({ name: 'equipment-details', params: { id: equipmentId } });
  }
};
  
  onMounted(() => {
    fetchRelatedItems();
  });
  </script>
  