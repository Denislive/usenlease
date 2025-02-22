<template>
  <section class="hero bg-gradient-to-r from-[#ff9e00] to-[#ffc107] py-2 lg:py-10 relative text-white overflow-hidden">
    <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-t from-[#1c1c1c] to-transparent opacity-60"></div>

    <div class="container mx-auto text-center relative z-10 px-4">
      <h1 class="text-3xl lg:text-5xl font-bold leading-tight mb-6">
        Rent the Best Equipment for Your Needs
      </h1>
      <p class="text-sm text-black lg:text-xl mb-8">
        Find top-quality equipment for any project. Fast delivery and great customer support.
      </p>

      <!-- Search Box -->
      <div class="flex justify-center">
        <div class="w-full max-w-xl bg-white p-2 search shadow-lg">
          <div class="flex items-center">
            <!-- Categories Dropdown -->
            <div class="relative flex-shrink-0">
              <select
                v-model="selectedCategory"
                @change="goToDetail"
                :class="['bg-transparent text-[#1c1c1c] p-3 border-r border-gray-200', dropdownWidthClass]"
              >
                <option value="All">All</option>
                <option v-for="category in displayedCategories" :key="category.id" :value="category.slug">
                  {{ category.name }}
                </option>
              </select>
            </div>

            <!-- Search Input -->
            <input
              type="text"
              class="flex-1 w-full text-[#1c1c1c] border-none text-lg focus:outline-none"
              placeholder="I am looking for ..."
              v-model="searchQuery"
            />

            <!-- Search Button -->
            <button
              @click="goToDetail"
              class="bg-[#ff6f00] text-white rounded-full px-4 py-3 transition duration-300 hover:bg-[#ff9e00] transform hover:scale-110"
            >
              <i class="pi pi-search text-lg"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useEquipmentsStore } from '@/store/equipments';
import { useRouter } from 'vue-router';
import debounce from 'lodash/debounce';

const store = useStore();
const equipmentStore = useEquipmentsStore();
const router = useRouter();

// Fetch categories on mount
onMounted(async () => {
  console.log('Fetching categories...');
  await store.dispatch('fetchCategories'); // Ensure Vuex store has this action
});

// Search Query
const searchQuery = computed({
  get: () => store.getters.getSearchQuery || '',
  set: (value) => store.dispatch('setSearchQuery', value),
});

// Categories
const categories = computed(() => {
  console.log('Computing categories:', equipmentStore.categories);
  return equipmentStore.categories ?? [];
});

const showMoreCategories = ref(false);
const displayedCategories = computed(() => {
  if (!categories.value.length) return [];
  return showMoreCategories.value ? categories.value : categories.value.slice(0, 20);
});

const selectedCategory = ref('All');
const dropdownWidthClass = computed(() => (selectedCategory.value === 'All' ? 'static-width' : 'dynamic-width'));

// Handle category change
const goToDetail = () => {
  console.log('Navigating to:', selectedCategory.value, 'Search:', searchQuery.value);
  router.push({ name: 'category-details', query: { cat: selectedCategory.value, search: searchQuery.value } });
};

// Debounce search updates
const updateSearch = debounce(() => {
  console.log('Updating search:', searchQuery.value);
  const query = searchQuery.value.trim().toLowerCase();
  const filteredEquipments = equipmentStore.equipments.filter((equipment) => {
    return (
      (selectedCategory.value === 'All' || equipment.category.toLowerCase() === selectedCategory.value.toLowerCase()) &&
      equipment.name.toLowerCase().includes(query)
    );
  });
  store.dispatch('setFilteredEquipments', filteredEquipments);
}, 300);

// Watch searchQuery and selectedCategory
watch([searchQuery, selectedCategory], updateSearch, { immediate: true });
</script>

<style>
select.static-width {
  width: 8rem;
  background-color: #fff;
  color: #1c1c1c;
  border-radius: 5px;
  margin-right: 5px;
}
select.dynamic-width {
  width: auto;
}

.search {
  border-radius: 5px;
}

.hero {
  min-height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
