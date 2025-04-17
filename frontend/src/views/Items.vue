  <template>
    <div class="min-h-screen bg-gray-100 py-12 font-sans">
      <div class="max-w-4xl mx-auto space-y-6">
        <!-- Header Section -->
        <div class="bg-gradient-to-r from-amber-400 to-amber-600 text-[#1c1c1c] rounded-2xl shadow-xl p-8 text-center">
          <h2 class="text-4xl font-extrabold tracking-wide">Item Manager</h2>
          <p class="mt-2 text-[#1c1c1c]/80">Effortlessly manage your items and track rentals.</p>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-8">
          <i class="pi pi-spin pi-spinner text-4xl text-[#ffc107]"></i>
          <p class="mt-2 text-[#1c1c1c]">Loading items and rentals...</p>
        </div>

        <!-- Main Content -->
        <div v-else class="space-y-16">
          <!-- Equipment Gallery -->
          <section>
            <h2 class="text-3xl font-bold text-[#1c1c1c] mb-6 flex items-center">
              <i class="pi pi-box mr-2 text-[#ffc107]"></i> Your Items
            </h2>
            <div v-if="store.userEquipments.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <div v-for="equipment in store.userEquipments" :key="equipment.id" @click="goToDetail(equipment.id)"
                class="bg-white rounded-lg shadow-lg overflow-hidden transform transition-all duration-300 hover:scale-105 hover:shadow-2xl cursor-pointer">
                <div class="relative h-48">
                  <!-- Image -->
                  <img v-if="equipment.images?.length > 0" :src="`${api_base_url}/${equipment.images[0].image_url}`"
                    :alt="equipment.name || 'Equipment'" class="w-full h-full object-cover" />
                  <img v-else src="../assets/images/placeholder.png" alt="No image"
                    class="w-full h-full object-cover opacity-70" />
                  <!-- Status Badge -->
                  <span :class="equipment.is_available ? 'bg-[#ffc107]' : 'bg-gray-500'"
                    class="absolute top-0 left-0 px-2 py-1 rounded-md text-xs font-bold text-[#1c1c1c] flex items-center">
                    <i :class="equipment.is_available ? 'pi pi-check' : 'pi pi-times'" class="mr-1"></i>
                    {{ equipment.is_available ? 'Available' : 'Unavailable' }}
                  </span>
                  <!-- Edit Button -->
                  <button v-if="!isRented(equipment.id)"
                    @click.stop="openEditModal(equipment)"
                    class="absolute bottom-3 right-3 bg-[#1c1c1c] text-[#ffc107] rounded-full h-9 w-9 flex items-center justify-center hover:bg-[#ffc107] hover:text-[#1c1c1c] transition">
                    <i class="pi pi-pencil"></i>
                  </button>
                </div>
                <div class="p-4">
                  <h3 class="text-lg font-semibold text-[#1c1c1c] truncate">{{ equipment.name || 'Unnamed' }}</h3>
                  <p class="text-[#ffc107] text-sm">${{ equipment.hourly_rate || 0 }}/day</p>
                </div>
              </div>
            </div>
            <div v-else class="bg-white rounded-lg shadow-lg p-8 text-center">
              <i class="pi pi-box text-5xl text-[#ffc107] mb-4"></i>
              <p class="text-lg text-[#1c1c1c]">No Item listed yet.</p>
              <RouterLink :to="{ name: 'list-item' }"
                class="inline-block mt-4 px-6 py-2 bg-[#ffc107] text-[#1c1c1c] rounded-md font-semibold hover:bg-[#e0a800] transition">
                List Item
              </RouterLink>
            </div>
          </section>

          <!-- Rental Overview -->
          <section>
            <h2 class="text-3xl font-bold text-[#1c1c1c] mb-6 flex items-center">
              <i class="pi pi-calendar mr-2 text-[#ffc107]"></i> Rental Overview
            </h2>
            <div class="space-y-12">
              <!-- Currently Rented -->
              <div class="bg-white rounded-lg shadow-md p-6">
                <h3 class="text-xl font-semibold text-[#1c1c1c] mb-4">Currently Rented</h3>
                <div class="overflow-x-auto">
                  <table class="w-full text-left">
                    <thead>
                      <tr class="bg-[#1c1c1c] text-[#ffc107] text-sm uppercase">
                        <th class="py-3 px-4">Item</th>
                        <th class="py-3 px-4 text-center">Duration</th>
                        <th class="py-3 px-4 text-center">Total</th>
                        <th class="py-3 px-4 text-center">Action</th>
                      </tr>
                    </thead>
                    <tbody class="text-gray-700">
                      <tr v-if="rentedItems.length === 0">
                        <td colspan="4" class="py-4 text-center text-gray-500">No rented items.</td>
                      </tr>
                      <tr v-for="rental in rentedItems" :key="rental.id"
                        class="border-b border-gray-200 hover:bg-gray-50">
                        <td class="py-3 px-4">({{ rental.quantity || 1 }}) {{ rental.item?.name || 'N/A' }}</td>
                        <td class="py-3 px-4 text-center">
                          {{ rental.booked_dates?.start_date || 'N/A' }} - {{ rental.booked_dates?.end_date || 'N/A' }}
                        </td>
                        <td class="py-3 px-4 text-center">
                          {{ rental.quantity && rental.item?.hourly_rate ? `$${rental.quantity * rental.item.hourly_rate}`
                          : '$0' }}
                        </td>
                        <td class="py-3 px-4 text-center">
                          <button v-if="rental.status === 'return'" @click="openReturnModal(rental.id)"
                            class="px-4 py-2 bg-[#ffc107] text-[#1c1c1c] rounded-md hover:bg-[#e0a800] transition"
                            :disabled="isUpdating">
                            Confirm Return
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <NewReturnConfirmationModal :showReturnModal="showReturnModal" :orderItemId="selectedOrderItem"
                @close="closeReturnModal" @confirm="handleReturnConfirmation" />

              <!-- Awaiting Approval -->
              <div class="bg-white rounded-lg shadow-md p-6">
                <h3 class="text-xl font-semibold text-[#1c1c1c] mb-4">Awaiting Approval</h3>
                <div class="overflow-x-auto">
                  <table class="w-full text-left">
                    <thead>
                      <tr class="bg-[#1c1c1c] text-[#ffc107] text-sm uppercase">
                        <th class="py-3 px-4">Item</th>
                        <th class="py-3 px-4 text-center">Duration</th>
                        <th class="py-3 px-4 text-center">Total</th>
                        <th class="py-3 px-4 text-center">Action</th>
                      </tr>
                    </thead>
                    <tbody class="text-gray-700">
                      <tr v-if="awaitingApprovalItems.length === 0">
                        <td colspan="4" class="py-4 text-center text-gray-500">No items awaiting approval.</td>
                      </tr>
                      <tr v-for="item in awaitingApprovalItems" :key="item.id"
                        class="border-b border-gray-200 hover:bg-gray-50">
                        <td class="py-3 px-4">({{ item.quantity || 1 }}) {{ item.item?.name || 'N/A' }}</td>
                        <td class="py-3 px-4 text-center">
                          {{ item.booked_dates?.start_date || 'N/A' }} - {{ item.booked_dates?.end_date || 'N/A' }}
                        </td>
                        <td class="py-3 px-4 text-center">
                          {{ item.quantity && item.item?.hourly_rate ? `$${item.quantity * item.item.hourly_rate}` : '$0'
                          }}
                        </td>
                        <td class="py-3 px-4 text-center">
                          <button @click="openApprovalModal(item)"
                            class="px-4 py-2 bg-[#ffc107] text-[#1c1c1c] rounded-md hover:bg-[#e0a800] transition"
                            :disabled="isUpdating">
                            Approve
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Awaiting Pickup -->
              <div class="bg-white rounded-lg shadow-md p-6">
                <h3 class="text-xl font-semibold text-[#1c1c1c] mb-4">Awaiting Pickup</h3>
                <div class="overflow-x-auto">
                  <table class="w-full text-left">
                    <thead>
                      <tr class="bg-[#1c1c1c] text-[#ffc107] text-sm uppercase">
                        <th class="py-3 px-4">Item</th>
                        <th class="py-3 px-4 text-center">Duration</th>
                        <th class="py-3 px-4 text-center">Total</th>
                        <th class="py-3 px-4 text-center">Action</th>
                      </tr>
                    </thead>
                    <tbody class="text-gray-700">
                      <tr v-if="awaitingPickups.length === 0">
                        <td colspan="4" class="py-4 text-center text-gray-500">No items awaiting pickup.</td>
                      </tr>
                      <tr v-for="rental in awaitingPickups" :key="rental.id"
                        class="border-b border-gray-200 hover:bg-gray-50">
                        <td class="py-3 px-4">({{ rental.quantity || 1 }}) {{ rental.item?.name || 'N/A' }}</td>
                        <td class="py-3 px-4 text-center">
                          {{ rental.booked_dates?.start_date || 'N/A' }} - {{ rental.booked_dates?.end_date || 'N/A' }}
                        </td>
                        <td class="py-3 px-4 text-center">
                          {{ rental.quantity && rental.item?.hourly_rate ? `$${rental.quantity * rental.item.hourly_rate}`
                          : '$0' }}
                        </td>
                        <td class="py-3 px-4 text-center">
                          <button @click="openPickupConfirmationModal(rental.id)"
                            class="px-4 py-2 bg-[#ffc107] text-[#1c1c1c] rounded-md hover:bg-[#e0a800] transition"
                            :disabled="isUpdating">
                            Confirm Pickup
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Pickup Confirmation Modal Component -->
              <NewPickupConfirmationModal :showPickupModal="showNewPickupConfirmationModal" :orderItem="selectedOrderItem"
                @close="showNewPickupConfirmationModal = false" @confirm="handlePickupConfirmation" />

              <!-- Returned -->
              <div class="bg-white rounded-lg shadow-md p-6">
                <h3 class="text-xl font-semibold text-[#1c1c1c] mb-4">Returned</h3>
                <div class="overflow-x-auto">
                  <table class="w-full text-left">
                    <thead>
                      <tr class="bg-[#1c1c1c] text-[#ffc107] text-sm uppercase">
                        <th class="py-3 px-4">Item</th>
                        <th class="py-3 px-4 text-center">Duration</th>
                        <th class="py-3 px-4 text-center">Total</th>
                        <th class="py-3 px-4 text-center">Status</th>
                      </tr>
                    </thead>
                    <tbody class="text-gray-700">
                      <tr v-if="returnedItems.length === 0">
                        <td colspan="4" class="py-4 text-center text-gray-500">No returned items.</td>
                      </tr>
                      <tr v-for="rental in returnedItems" :key="rental.id"
                        class="border-b border-gray-200 hover:bg-gray-50">
                        <td class="py-3 px-4">({{ rental.quantity || 1 }}) {{ rental.item?.name || 'N/A' }}</td>
                        <td class="py-3 px-4 text-center">
                          {{ rental.booked_dates?.start_date || 'N/A' }} - {{ rental.booked_dates?.end_date || 'N/A' }}
                        </td>
                        <td class="py-3 px-4 text-center">
                          {{ rental.quantity && rental.item?.hourly_rate ? `$${rental.quantity * rental.item.hourly_rate}`
                          : '$0' }}
                        </td>
                        <td class="py-3 px-4 text-center">{{ rental.status || 'N/A' }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- In Items.vue <template>, inside the Rental Overview section -->
              <div class="bg-white rounded-lg shadow-md p-6">
                <h3 class="text-xl font-semibold text-[#1c1c1c] mb-4">Disputed Items</h3>
                <div class="overflow-x-auto">
                  <table class="w-full text-left">
                    <thead>
                      <tr class="bg-[#1c1c1c] text-[#ffc107] text-sm uppercase">
                        <th class="py-3 px-4">Item</th>
                        <th class="py-3 px-4 text-center">Duration</th>
                        <th class="py-3 px-4 text-center">Total</th>
                        <th class="py-3 px-4 text-center">Status</th>
                      </tr>
                    </thead>
                    <tbody class="text-gray-700">
                      <tr v-if="disputedItems.length === 0">
                        <td colspan="4" class="py-4 text-center text-gray-500">No disputed items.</td>
                      </tr>
                      <tr v-for="rental in disputedItems" :key="rental.id"
                        class="border-b border-gray-200 hover:bg-gray-50 bg-red-50">
                        <td class="py-3 px-4">({{ rental.quantity || 1 }}) {{ rental.item?.name || 'N/A' }}</td>
                        <td class="py-3 px-4 text-center">
                          {{ rental.booked_dates?.start_date || 'N/A' }} - {{ rental.booked_dates?.end_date || 'N/A' }}
                        </td>
                        <td class="py-3 px-4 text-center">
                          {{ rental.quantity && rental.item?.hourly_rate ? `$${rental.quantity * rental.item.hourly_rate}`
                          : '$0' }}
                        </td>
                        <td class="py-3 px-4 text-center text-red-600">{{ rental.status || 'N/A' }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- Edit Modal -->
        <transition name="modal">
          <div v-if="editModalVisible" class="fixed inset-0 bg-[#1c1c1c]/80 flex items-center justify-center z-50"
            @click.self="closeEditModal">
            <div class="bg-white rounded-lg p-8 w-full max-w-lg animate-pop">
              <h3 class="text-2xl font-bold text-[#1c1c1c] mb-6">Edit Equipment</h3>
              <form @submit.prevent="updateEquipment" class="space-y-4">
                <div>
                  <label for="name" class="block text-sm font-medium text-[#1c1c1c]">Name</label>
                  <input v-model="editedEquipment.name" type="text" id="name"
                    class="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#ffc107]" required />
                </div>
                <div>
                  <label for="hourly_rate" class="block text-sm font-medium text-[#1c1c1c]">Daily Rate ($)</label>
                  <input v-model.number="editedEquipment.hourly_rate" type="number" step="0.01" id="hourly_rate"
                    class="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#ffc107]" required />
                </div>
                <div>
                  <label for="availableItems" class="block text-sm font-medium text-[#1c1c1c]">Available Quantity</label>
                  <input v-model.number="editedEquipment.available_quantity" type="number" min="1" id="availableItems"
                    class="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#ffc107]" required />
                </div>
                <div>
                  <label for="description" class="block text-sm font-medium text-[#1c1c1c]">Description</label>
                  <textarea v-model="editedEquipment.description" id="description"
                    class="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#ffc107]"
                    rows="4"></textarea>
                </div>
                <div>
                  <label for="category" class="block text-sm font-medium text-[#1c1c1c]">Category</label>
                  <select v-model="editedEquipment.category" id="category"
                    class="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#ffc107]" required>
                    <option v-for="category in store.categories" :key="category.id" :value="category.id">
                      {{ category.name }}
                    </option>
                  </select>
                </div>
                <div>
                  <label for="is_available" class="block text-sm font-medium text-[#1c1c1c]">Availability</label>
                  <select v-model="editedEquipment.is_available" id="is_available"
                    class="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#ffc107]" required>
                    <option :value="true">Available</option>
                    <option :value="false">Unavailable</option>
                  </select>
                </div>
                <div>
                  <label for="images" class="block text-sm font-medium text-[#1c1c1c]">Upload Images</label>
                  <input type="file" id="images" @change="handleImageUpload"
                    class="w-full p-3 border border-gray-300 rounded-md" multiple accept="image/*" />
                </div>
                <div class="flex justify-end space-x-3">
                  <button type="button" @click="closeEditModal"
                    class="px-6 py-2 bg-gray-400 text-white rounded-md hover:bg-gray-500" :disabled="isUpdating">
                    Cancel
                  </button>
                  <button type="submit" class="px-6 py-2 bg-[#ffc107] text-[#1c1c1c] rounded-md hover:bg-[#e0a800]"
                    :disabled="isUpdating">
                    {{ isUpdating ? 'Saving...' : 'Save' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </transition>


        <!-- Approval Modal -->
        <transition name="modal">
          <div v-if="isApprovalModalOpen" class="fixed inset-0 bg-[#1c1c1c]/80 flex items-center justify-center z-50"
            @click.self="isApprovalModalOpen = false">
            <div class="bg-white rounded-lg p-6 w-full max-w-md animate-pop">
              <h3 class="text-xl font-semibold text-[#1c1c1c] mb-4">Approve Rental</h3>
              <p class="text-gray-600 mb-6">Do you want to approve this rental request?</p>
              <div class="flex justify-end space-x-3">
                <button @click="isApprovalModalOpen = false" class="px-6 py-2 bg-gray-400 text-white rounded-md"
                  :disabled="isUpdating">
                  Cancel
                </button>
                <button @click="approveRentalApproval(selectedRental?.id)"
                  class="px-6 py-2 bg-[#ffc107] text-[#1c1c1c] rounded-md hover:bg-[#e0a800]" :disabled="isUpdating">
                  Approve
                </button>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { useAuthStore } from '../store/auth';
import { useEquipmentsStore } from '../store/equipments';
import useNotifications from '@/store/notification.js';
import NewPickupConfirmationModal from '@/components/NewPickupConfirmationModal.vue';
import NewReturnConfirmationModal from '@/components/NewReturnConfirmationModal.vue';
const { showNotification } = useNotifications();
const authStore = useAuthStore();
const store = useEquipmentsStore();
const router = useRouter();
const api_base_url = import.meta.env.VITE_API_BASE_URL;

const editModalVisible = ref(false);
const editedEquipment = ref({});
const newImages = ref([]);
const isUpdating = ref(false);
const showReturnModal = ref(false);
const isApprovalModalOpen = ref(false);
const showNewPickupConfirmationModal = ref(false);
const selectedOrderItem = ref(null);
const selectedRental = ref(null);
const orderItems = ref([]);
const loading = ref(true);

// Log store categories on mount
const logCategories = () => {
store.fetchCategories();
  console.log('Store Categories:', store.categories);
};

// Fetch user equipments with retry logic
const fetchUserEquipments = async (retryCount = 3) => {
  try {
    await store.fetchUserEditableEquipments();
  } catch (error) {
    console.error('Error fetching user items:', error);
    if (retryCount > 0) {
      console.log(`Retrying fetchUserEquipments... (${retryCount} attempts left)`);
      await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1s
      await fetchUserEquipments(retryCount - 1);
    } else {
      showNotification('Error', 'Failed to load items. Please try again later.', 'error');
    }
  }
};

// Fetch order items with retry logic
const fetchOrderItems = async (retryCount = 3) => {
  try {
    const response = await axios.get(`${api_base_url}/api/order-items/`, {
      withCredentials: true,
    });
    orderItems.value = Array.isArray(response.data) ? response.data : [];
   
  } catch (error) {
    console.error('Error fetching order items:', error);
    if (retryCount > 0) {
      console.log(`Retrying fetchOrderItems... (${retryCount} attempts left)`);
      await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1s
      await fetchOrderItems(retryCount - 1);
    } else {
      showNotification('Error', 'Failed to load order items. Please try again later.', 'error');
    }
  }
};

// Computed properties for rental statuses
const awaitingApprovalItems = computed(() => {
  return Array.isArray(orderItems.value)
    ? orderItems.value.filter(item => item.status === 'pending')
    : [];
});

const rentedItems = computed(() => {
  return Array.isArray(orderItems.value)
    ? orderItems.value.filter(item => item.status === 'rented' || item.status === 'return')
    : [];
});

const returnedItems = computed(() => {
  return Array.isArray(orderItems.value)
    ? orderItems.value.filter(item => item.status === 'completed')
    : [];
});

const awaitingPickups = computed(() => {
  return Array.isArray(orderItems.value)
    ? orderItems.value.filter(item => item.status === 'pickup')
    : [];
});

const disputedItems = computed(() => {
  return Array.isArray(orderItems.value)
    ? orderItems.value.filter(item => item.status === 'disputed')
    : [];
});

// Check if equipment is rented
const isRented = (equipmentId) => {
  return (
    rentedItems.value.some((rental) => rental.item?.id === equipmentId) ||
    awaitingPickups.value.some((rental) => rental.item?.id === equipmentId) ||
    awaitingApprovalItems.value.some((rental) => rental.item?.id === equipmentId) ||
    disputedItems.value.some((rental) => rental.item?.id === equipmentId) ||
    returnedItems.value.some((rental) => rental.item?.id === equipmentId)
  );
};

// Mount lifecycle
onMounted(async () => {
  try {
    loading.value = true;
    if (!authStore.user) {
      console.warn('No user authenticated.');
      showNotification('Error', 'Please log in to view your items and rentals.', 'error');
      router.push('/login'); // Redirect to login if needed
      return;
    }
    await Promise.all([fetchUserEquipments(), fetchOrderItems()]);
    // Log categories after fetching data
    logCategories();
  } catch (error) {
    console.error('Error during mount:', error);
    showNotification('Error', 'Failed to initialize data. Please try again.', 'error');
  } finally {
    loading.value = false;
  }
});

// Navigation to equipment details
const goToDetail = (equipmentId) => {
  if (equipmentId) {
    router.push({ name: 'equipment-details', params: { id: equipmentId } });
  } else {
    showNotification('Error', 'Invalid item ID.', 'error');
  }
};

// Check if equipment is editable
const isEditable = (equipmentId) => {
  const equipment = store.userEquipments.find((eq) => eq.id === equipmentId);
  return equipment ? authStore.user?.id === equipment.user_id : false;
};

// Edit equipment modal
const openEditModal = (equipment) => {
  editedEquipment.value = { ...equipment, category: equipment.category?.id || equipment.category };
  newImages.value = [];
  editModalVisible.value = true;
};

const closeEditModal = () => {
  editModalVisible.value = false;
  editedEquipment.value = {};
  newImages.value = [];
};

const handleImageUpload = (event) => {
  newImages.value = Array.from(event.target.files);
};

const updateEquipment = async () => {
  if (!editedEquipment.value.name || !editedEquipment.value.hourly_rate || !editedEquipment.value.available_quantity) {
    showNotification('Error', 'Please fill in all required fields.', 'error');
    return;
  }

  isUpdating.value = true;
  const formData = new FormData();
  formData.append('name', editedEquipment.value.name);
  formData.append('hourly_rate', editedEquipment.value.hourly_rate);
  formData.append('available_quantity', editedEquipment.value.available_quantity);
  formData.append('description', editedEquipment.value.description || '');
  formData.append('category', editedEquipment.value.category);
  formData.append('is_available', editedEquipment.value.is_available);
  newImages.value.forEach((image) => formData.append('images', image));


  try {
    const response = await axios.put(
      `${api_base_url}/api/equipments/${editedEquipment.value.id}/`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        withCredentials: true,
      }
    );
    store.userEquipments = store.userEquipments.map((eq) =>
      eq.id === editedEquipment.value.id ? response.data : eq
    );
    closeEditModal();
    showNotification('Success', 'Item updated successfully!', 'success');
  } catch (error) {
    console.error('Error updating Item:', error);
    showNotification('Error', 'Failed to update Item. Please try again.', 'error');
  } finally {
    isUpdating.value = false;
  }
};

// Return confirmation
const openReturnModal = (orderItemId) => {
  selectedOrderItem.value = orderItemId;
  showReturnModal.value = true;
};

const closeReturnModal = () => {
  showReturnModal.value = false;
  selectedOrderItem.value = null;
};

const handleReturnConfirmation = async (returnData) => {
  if (!returnData.orderItemId) {
    showNotification('Error', 'Invalid order item ID.', 'error');
    return;
  }

  const formData = new FormData();
  formData.append('returnCondition', returnData.returnCondition);
  if (returnData.complaintText) {
    formData.append('complaintText', returnData.complaintText);
  }
  if (returnData.image) {
    formData.append('image', returnData.image.blob, returnData.image.filename);
  }

  try {
    const response = await axios.post(
      `${api_base_url}/api/order-items/${returnData.orderItemId}/confirm_return/`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        withCredentials: true,
      }
    );
    const message =
      returnData.returnCondition === 'damaged'
        ? 'Item return recorded as damaged and marked as disputed.'
        : 'Item return confirmed successfully!';
    showNotification('Success', message, 'success');
    await fetchOrderItems();
  } catch (error) {
    console.error('Error confirming return:', error);
    let errorMessage = 'Failed to confirm return. Please try again.';
    if (error.response?.data?.error) {
      errorMessage = error.response.data.error;
    } else if (error.response?.data) {
      errorMessage = typeof error.response.data === 'string' ? error.response.data : JSON.stringify(error.response.data);
    } else if (error.message) {
      errorMessage = error.message;
    }
    showNotification('Error', errorMessage, 'error');
  } finally {
    showReturnModal.value = false;
    selectedOrderItem.value = null;
  }
};

// Approve rental
const openApprovalModal = (rental) => {
  selectedRental.value = rental;
  isApprovalModalOpen.value = true;
};

const approveRentalApproval = async (rentalId) => {
  if (!rentalId) {
    showNotification('Error', 'Invalid rental ID.', 'error');
    return;
  }
  try {
    await axios.post(
      `${api_base_url}/api/order-items/${rentalId}/approve/`,
      {},
      { withCredentials: true }
    );
    await fetchOrderItems();
    showNotification('Success', 'Rental approved successfully!', 'success');
    isApprovalModalOpen.value = false;
  } catch (error) {
    console.error('Error approving rental:', error);
    showNotification('Error', 'Rental approval failed. Please try again.', 'error');
  }
};

// Pickup confirmation
const openPickupConfirmationModal = (rentalId) => {
  selectedOrderItem.value = rentalId;
  showNewPickupConfirmationModal.value = true;
};

const handlePickupConfirmation = async () => {
  try {
    await fetchOrderItems();
    showNewPickupConfirmationModal.value = false;
    selectedOrderItem.value = null;
    showNotification('Success', 'Pickup confirmed successfully!', 'success');
  } catch (error) {
    console.error('Error confirming pickup:', error);
    showNotification('Error', 'Failed to confirm pickup. Please try again.', 'error');
  }
};
</script>
<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.animate-pop {
  animation: pop 0.3s ease-out;
}

@keyframes pop {
  0% {
    transform: scale(0.95);
    opacity: 0;
  }

  100% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>