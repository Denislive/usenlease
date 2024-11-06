<template>
  <div class="container mx-auto py-4">
    <!-- Tabs for Description, Specification, Terms, Reviews -->
    <div class="bg-white rounded-lg shadow-md">
      <ul class="flex border-b">
        <li class="mr-1">
          <a
            href="#"
            @click.prevent="activeTab = 'description'"
            :class="{'border-b-2 border-[#ffc107] font-semibold': activeTab === 'description', 'text-gray-600': activeTab !== 'description'}"
            class="inline-block py-2 px-2"
          >Description</a>
        </li>
        <li class="mr-1">
          <a
            href="#"
            @click.prevent="activeTab = 'specification'"
            :class="{'border-b-2 border-[#ffc107] font-semibold': activeTab === 'specification', 'text-gray-600': activeTab !== 'specification'}"
            class="inline-block py-2 px-2"
          >Specification</a>
        </li>
        <li class="mr-1">
          <a
            href="#"
            @click.prevent="activeTab = 'terms'"
            :class="{'border-b-2 border-[#ffc107] font-semibold': activeTab === 'terms', 'text-gray-600': activeTab !== 'terms'}"
            class="inline-block py-2 px-2"
          >Terms</a>
        </li>
        <li>
          <a
            href="#"
            @click.prevent="activeTab = 'reviews'"
            :class="{'border-b-2 border-[#ffc107] font-semibold': activeTab === 'reviews', 'text-gray-600': activeTab !== 'reviews'}"
            class="inline-block py-2 px-2"
          >Reviews</a>
        </li>
      </ul>

      <div class="p-4">
        <div v-show="activeTab === 'description'" class="tabs-panel">
          <p>{{ selectedEquipment?.description || 'Loading...' }}</p>
        </div>
        <div v-show="activeTab === 'specification'" class="tabs-panel">
          <ul>
            <li v-for="(spec, index) in selectedEquipment?.specifications" :key="index" class="mb-2">{{ spec }}</li>
          </ul>
        </div>
        <div v-show="activeTab === 'terms'" class="tabs-panel">
          <p>{{ selectedEquipment?.terms || 'Loading...' }}</p>
        </div>
        <div v-show="activeTab === 'reviews'" class="tabs-panel">
          <!-- Review section as defined -->
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useEquipmentsStore } from '@/store/equipments';

export default {
  data() {
    return {
      activeTab: 'description',
      reviews: [
        { id: 1, user: 'Alice', rating: 5, review_text: 'Great equipment!' },
        { id: 2, user: 'Bob', rating: 4, review_text: 'Very useful.' }
      ],
      newReview: {
        rating: null,
        text: ''
      },
      isAuthenticated: false
    };
  },
  computed: {
    selectedEquipment() {
      return this.equipmentsStore.selectedEquipment;
    }
  },
  methods: {
    submitReview() {
      console.log('Review submitted:', this.newReview);
      this.newReview.rating = null;
      this.newReview.text = '';
    }
  },
  created() {
    this.equipmentsStore = useEquipmentsStore();
    this.equipmentsStore.fetchEquipments();
    this.equipmentsStore.getEquipmentById(this.$route.params.id); // Replace with actual equipment ID
  }
};
</script>
