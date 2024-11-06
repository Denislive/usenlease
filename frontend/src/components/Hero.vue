<template>
  <section class="hero bg-[#ffc107] py-6">
    <div class="container mx-auto">
      <div class="flex flex-col items-center text-center">
        <div class="w-full">
          <div class="flex flex-col items-center">
            <span class="text-2xl font-bold custom-text">Find Equipment</span>
            <div class="flex items-center mt-3 custom-location-box cursor-pointer" data-open="usaLocationModal" id="allButton">
              <i class="pi pi-map-marker text-xl location-icon"></i>
              <span class="ml-2">All in USA</span>
            </div>
          </div>
        </div>

        <!-- Search Box -->
        <div class="w-full mt-6">
          <div class="flex justify-center">
            <div class="sm:w-3/4 md:w-10/12 lg:w-8/12 mt-4 md:mt-0">
              <div class="flex">
                <input
                  class="flex-1 border border-gray-300 rounded-l-md p-2"
                  type="search"
                  id="searchInput"
                  name="query"
                  placeholder="Search anything..."
                  v-model="searchQuery"
                  @input="updateSearch"
                  required
                />
                <button type="submit" class="bg-[#1c1c1c] text-white rounded-r-md p-2">
                  Search
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue';
import { useStore } from 'vuex';

const store = useStore();
const searchQuery = computed({
  get: () => store.getters.getSearchQuery,
  set: (value) => {
    store.dispatch('setSearchQuery', value);
  },
});

// The updateSearch function is no longer needed since we're using computed setter
</script>

<style scoped>
/* Additional styles can go here if needed */
</style>
