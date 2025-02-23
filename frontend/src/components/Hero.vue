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
                :class="['bg-transparent text-[#1c1c1c] p-3 focus:outline-none cursor-pointer border-r border-gray-200', dropdownWidthClass]"
              >
                <option disabled selected>All</option>
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
import { ref, computed, watch, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import debounce from 'lodash/debounce';

const store = useStore();
const router = useRouter();

// Fetch categories and equipments on component mount
onMounted(async () => {
  console.log('HERO - onMounted - Fetching categories and equipments...');
  await store.dispatch('fetchCategories');
  await store.dispatch('fetchEquipments');
  console.log('HERO - onMounted - Data fetching completed.');
});

// Search Query
const searchQuery = computed({
  get: () => {
    const value = store.getters.getSearchQuery;
    console.log('HERO - Computed Property [searchQuery] - Getter:', value);
    return value;
  },
  set: (value) => {
    console.log('HERO - Computed Property [searchQuery] - Setter:', value);
    store.commit('setSearchQuery', value); // ✅ FIX APPLIED
  },
});


// Categories
const categories = computed(() => {
  const value = store.getters.getCategories;
  console.log('HERO - Computed Property [categories]:', value);
  return value || [];
});

// Equipments
const equipments = computed(() => {
  const value = store.getters.getEquipments;
  console.log('HERO - Computed Property [equipments]:', value);
  return value || [];
});

const showMoreCategories = ref(false);
const displayedCategories = computed(() => {
  const value = showMoreCategories.value ? categories.value : categories.value.slice(0, 20);
  console.log('HERO - Computed Property [displayedCategories]:', value);
  return value;
});

const selectedCategory = ref('All');
const dropdownWidthClass = ref('static-width');

// Handle dropdown change
const handleDropdownChange = (event) => {
  selectedCategory.value = event.target.value;
  dropdownWidthClass.value = selectedCategory.value === 'All' ? 'static-width' : 'dynamic-width';
  console.log('HERO - Event [handleDropdownChange] - New selected category:', selectedCategory.value);
};

// Navigate to category details
const goToDetail = () => {
  const currentRoute = router.currentRoute.value;
  console.log('HERO - Function [goToDetail] - Navigating to details. Selected category:', selectedCategory.value, 'Search query:', searchQuery.value, 'Current route:', currentRoute);
  if (selectedCategory.value !== 'All') {
    if (
      currentRoute.name === 'category-details' &&
      currentRoute.query.cat === selectedCategory.value &&
      currentRoute.query.search === searchQuery.value
    ) {
      console.log('HERO - Function [goToDetail] - Replacing route with updated search query.');
      router.replace({ name: 'category-details', query: { cat: selectedCategory.value, search: searchQuery.value + '&' } });
    } else {
      console.log('HERO - Function [goToDetail] - Pushing new route.');
      router.push({ name: 'category-details', query: { cat: selectedCategory.value, search: searchQuery.value } });
    }
  }
};

// Update search with debounce
const updateSearch = debounce(() => {
  const query = searchQuery.value.trim().toLowerCase();
  const filteredEquipments = equipments.value.filter((equipment) => {
    const matchesCategory = selectedCategory.value === 'All' || equipment.category.toLowerCase() === selectedCategory.value.toLowerCase();
    const matchesQuery = equipment.name.toLowerCase().includes(query);
    return matchesCategory && matchesQuery;
  });

  console.log('HERO - Function [updateSearch] - Filtered equipments based on query and category:', filteredEquipments);

  // ✅ Fix applied: Use commit instead of dispatch
  store.commit('setFilteredEquipments', filteredEquipments);
}, 300);

// Watch searchQuery and selectedCategory
watch(
  [searchQuery, selectedCategory],
  () => {
    console.log('HERO - Watcher triggered - searchQuery:', searchQuery.value, 'selectedCategory:', selectedCategory.value);
    updateSearch();
  },
  { immediate: true }
);
</script>

<style>
select.static-width {
  width: 8rem; /* Static width for the disabled option */
  background-color: #fff;
  color: #1c1c1c;
  border-radius: 5px;
  margin-right: 5px;
}
select.dynamic-width {
  width: auto; /* Dynamic width for other options */
}

.search {
  border-radius: 5px;
}

/* Additional styles can go here if needed */
.hero {
  min-height: 100px;
  /* Ensure the hero section is not squeezed */
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
