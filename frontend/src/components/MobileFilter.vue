<script setup>
import { ref, computed, onMounted } from 'vue';
import { useEquipmentsStore } from '@/store/equipments';

const showFilters = ref(false);
const toggleFilters = () => {
  showFilters.value = !showFilters.value;
};

const store = useEquipmentsStore();
const categories = computed(() => store.categories);
const equipments = computed(() => store.equipments);
const filteredEquipments = computed(() => store.filteredEquipments);

// Reactive array to track selected category names
const selectedCategories = ref([]);

// Fetch categories and equipment on component mount
onMounted(async () => {
  await store.fetchCategories();
  await store.fetchEquipments();
});

// Clear all selected filters
const clearFilters = () => {
  selectedCategories.value = [];
  applyFilters(); // Reset the filters and show all equipment
};

// Apply filters based on selected category names
const applyFilters = () => {
  if (selectedCategories.value.length === 0) {
    store.filteredEquipments = store.equipments; // No filters selected, show all
  } else {
    const selectedCategoryIds = categories.value
      .filter((category) => selectedCategories.value.includes(category.name))
      .map((category) => category.id);

    store.filteredEquipments = store.equipments.filter((equipment) =>
      selectedCategoryIds.includes(equipment.category)
    );
  }
};

// Toggle category selection
const toggleCategory = (categoryName) => {
  const index = selectedCategories.value.indexOf(categoryName);
  if (index === -1) {
    selectedCategories.value.push(categoryName);
  } else {
    selectedCategories.value.splice(index, 1);
  }
  applyFilters();
};
</script>
<template>
  <div class="md:hidden">
    <!-- Filters Button -->
    <button 
      @click="toggleFilters" 
      class="w-full text-xl font-bold mb-4 flex items-center justify-center bg-[#1c1c1c] text-white rounded-md py-2 hover:bg-[#ffc107] hover:text-[#1c1c1c] transition"
    >
      <i class="pi pi-filter mr-2"></i> Filters
    </button>

    <!-- Filters Panel -->
    <div v-if="showFilters" class="border border-gray-300 rounded-lg p-4 shadow-md bg-white mb-4">
      <ul class="space-y-6">
        <!-- Category Filter -->
        <li class="product-filters-tab">
          <a href="#" class="text-lg font-semibold text-gray-800 hover:text-blue-600 transition">
            Category
          </a>
          <ul class="ml-4 mt-4 space-y-4">
            <!-- Clear All -->
            <li>
              <a 
                href="#" 
                class="text-sm font-medium text-red-500 hover:underline transition" 
                @click="clearFilters" 
                id="category-clear-all"
              >
                Clear All
              </a>
            </li>
            <!-- Category Items -->
            <li 
              v-for="category in categories" 
              :key="category.id" 
              @click="toggleCategory(category.name)" 
              class="flex items-center cursor-pointer bg-gray-100 hover:bg-gray-200 rounded-md p-2 transition"
            >
              <input 
                type="checkbox" 
                :id="'category-checkbox' + category.id" 
                :value="category.name" 
                v-model="selectedCategories"
                @change="applyFilters"
                class="hidden" 
              />
              <label :for="'category-checkbox' + category.id" class="flex items-center space-x-3">
                <!-- Dynamic Icon -->
                <span 
                  :class="{
                    'pi pi-check-circle text-blue-500': selectedCategories.includes(category.name),
                    'pi pi-circle text-gray-400': !selectedCategories.includes(category.name)
                  }"
                  class="text-xl"
                ></span>
                <!-- Category Name -->
                <span class="text-gray-700 text-lg font-medium">
                  {{ category.name }}
                </span>
              </label>
            </li>
          </ul>
        </li>
      </ul>
    </div>
  </div>
</template>
