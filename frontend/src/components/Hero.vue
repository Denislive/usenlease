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
import { ref, computed, watch } from 'vue';
import { useStore } from 'vuex';
import { useEquipmentsStore } from '@/store/equipments';
import { useRouter } from 'vue-router';
import debounce from 'lodash/debounce';

const store = useStore();
const equipmentStore = useEquipmentsStore();
const router = useRouter();

const searchQuery = computed({
  get: () => store.getters.getSearchQuery,
  set: (value) => {
    store.dispatch('setSearchQuery', value);
  },
});

const categories = computed(() => equipmentStore.categories);
const equipments = computed(() => equipmentStore.equipments);

const showMoreCategories = ref(false);
const displayedCategories = computed(() => {
  if (!categories.value || categories.value.length === 0) {
    return [];
  }
  return showMoreCategories.value ? categories.value : categories.value.slice(0, 20);
});

const selectedCategory = ref('All');
const dropdownWidthClass = ref('static-width');

const handleDropdownChange = (event) => {
  selectedCategory.value = event.target.value;
  dropdownWidthClass.value = selectedCategory.value === 'All' ? 'static-width' : 'dynamic-width';
};

const goToDetail = () => {
  if (selectedCategory.value !== 'All') {
    const currentRoute = router.currentRoute.value;
    if (currentRoute.name === 'category-details' && currentRoute.query.cat === selectedCategory.value && currentRoute.query.search === searchQuery.value) {
      router.replace({ name: 'category-details', query: { cat: selectedCategory.value, search: searchQuery.value + '&' } });
    } else {
      router.push({ name: 'category-details', query: { cat: selectedCategory.value, search: searchQuery.value } });
    }
  }
};

const updateSearch = debounce(() => {
  const query = searchQuery.value.trim().toLowerCase();
  const filteredEquipments = equipments.value.filter((equipment) => {
    const matchesCategory = selectedCategory.value === 'All' || equipment.category.toLowerCase() === selectedCategory.value.toLowerCase();
    const matchesQuery = equipment.name.toLowerCase().includes(query);
    return matchesCategory && matchesQuery;
  });
  store.dispatch('setFilteredEquipments', filteredEquipments);
}, 300);

watch([searchQuery, selectedCategory], updateSearch);
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
