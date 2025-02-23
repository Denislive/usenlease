<template>
  <section class="hero bg-gradient-to-r from-[#ff9e00] to-[#ffc107] py-2 lg:py-10 relative text-white overflow-hidden">
    <!-- Background Elements -->
    <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-t from-[#1c1c1c] to-transparent opacity-60"></div>

    <!-- Hero Content -->
    <div class="container mx-auto text-center relative z-10 px-4">
      <h1 class="text-3xl lg:text-5xl font-bold leading-tight mb-6 animate__animated animate__fadeIn animate__delay-1s">
        Rent the Best Equipment for Your Needs
      </h1>
      <p class="text-sm text-black lg:text-xl mb-8 animate__animated animate__fadeIn animate__delay-2s">
        Find top-quality equipment for any project. Fast delivery and great customer support.
      </p>

      <!-- Search Box with Integrated Categories Dropdown -->
      <div class="flex justify-center">
        <div class="w-full max-w-xl bg-white p-2 search shadow-lg">
          <div class="flex items-center">
            <!-- Categories Dropdown -->
            <div class="relative flex-shrink-0">
              <select
                v-model="selectedCategory"
                @change="goToDetail"
                class="bg-transparent text-[#1c1c1c] p-3 focus:outline-none cursor-pointer border-r border-gray-200"
              >
                <option :value="'All'">All</option>
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

            <!-- Go to Detail Button -->
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

    <!-- Decorative Circle Effect -->
    <div class="absolute top-1/4 left-1/4 w-24 h-24 bg-[#ff6f00] rounded-full opacity-20 animate-pulse"></div>
    <div class="absolute top-2/3 right-1/4 w-36 h-36 bg-[#ff6f00] rounded-full opacity-30 animate-pulse"></div>
  </section>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import debounce from 'lodash/debounce';

const store = useStore();
const router = useRouter();

// Search Query
const searchQuery = computed({
  get: () => store.getters.getSearchQuery,
  set: (value) => store.dispatch('setSearchQuery', value),
});

// Categories
const categories = computed(() => store.getters.getCategories);
const selectedCategory = ref('All');
const showMoreCategories = ref(false);

const displayedCategories = computed(() => {
  return categories.value?.length > 0 ? (showMoreCategories.value ? categories.value : categories.value.slice(0, 20)) : [];
});

// Navigate to category details
const goToDetail = () => {
  if (selectedCategory.value !== 'All') {
    const query = { cat: selectedCategory.value, search: searchQuery.value };
    const currentRoute = router.currentRoute.value;
    
    if (currentRoute.name === 'category-details' && currentRoute.query.cat === query.cat && currentRoute.query.search === query.search) {
      router.replace({ name: 'category-details', query: { ...query, search: query.search + '&' } });
    } else {
      router.push({ name: 'category-details', query });
    }
  }
};

// Update search with debounce
const updateSearch = debounce(() => {
  const query = searchQuery.value.trim().toLowerCase();
  const filteredEquipments = store.getters.getEquipments.filter((equipment) => {
    const matchesCategory = selectedCategory.value === 'All' || equipment.category.toLowerCase() === selectedCategory.value.toLowerCase();
    const matchesQuery = equipment.name.toLowerCase().includes(query);
    return matchesCategory && matchesQuery;
  });

  store.dispatch('setFilteredEquipments', filteredEquipments);
}, 300);

// Watch searchQuery and selectedCategory
watch([searchQuery, selectedCategory], updateSearch, { immediate: true });
</script>

<style>
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
