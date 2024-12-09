<template>
  <div class="grid grid-cols-12 gap-8 md:px-32 py-4">
    <!-- Sidebar -->
    <div class="col-span-12 lg:col-span-3 bg-white p-4 rounded-lg  hidden lg:block shadow-md">
      <div class="flex items-center space-x-4 mb-6">
        <i class="bi bi-person text-black text-2xl"></i>
        <span class="text-lg font-medium">Welcome, {{ user.first_name || user.email || "John Doe" }}</span>
      </div>

      <hr class="my-4">


      <!-- Other Sections (Dark Gray) -->
      <div v-for="(section, index) in visibleSections" :key="index" :class="{
        'text-white bg-[#1c1c1c]': activeSection === section.name,
        'text-[#ffc107]': activeSection !== section.name,
      }" class="nav-item font-semibold py-2 px-4 rounded-md cursor-pointer mb-2" :id="section.name"
        @click="navigateToSection(section.name)">
        {{ section.label }}
      </div>

    </div>

    <!-- Sidebar -->
    <div v-if="showSidebar" class="col-span-12 lg:col-span-3 bg-white p-4 rounded-lg shadow-md md:block lg:hidden">
      <div class="flex items-center space-x-4 mb-6">
        <i class="bi bi-person text-black text-2xl"></i>
        <span class="text-lg font-medium">
          Welcome, {{ user.first_name || user.email || "John Doe" }}
        </span>
      </div>
      <!-- Logout Option -->
      <button @click="handleLogout" class="w-full px-4 py-2 text-white bg-red-500 hover:text-[#1c1c1c] rounded">
        Logout
      </button>
      <hr class="my-4" />


      <!-- Other Sections (Dark Gray) -->
      <div v-for="(section, index) in visibleSections" :key="index" :class="{
        'text-white bg-[#1c1c1c]': activeSection === section.name,
        'text-[#ffc107]': activeSection !== section.name,
      }" class="nav-item font-semibold py-2 px-4 rounded-md cursor-pointer mb-2" :id="section.name"
        @click="navigateToSection(section.name)">
        {{ section.label }}
      </div>

    </div>



    <!-- Main Content Area -->
    <div class="col-span-12 md:col-span-8 lg:col-span-9 bg-white p-6 rounded-lg shadow-md">
      <div v-for="section in sections" :key="section.name" class="space-y-6">
        <div v-show="activeSection === section.name" class="section-content">
          <h3 class="text-3xl font-semibold text-gray-800 mb-6 border-b border-gray-300 pb-3">
            {{ section.label }}
          </h3>

          <!-- Personal Information Section -->
          <div v-if="activeSection === 'personal-info'" class="space-y-6">
            <button @click="closeSidebar"
              class="mr-4 text-gray-800 mt-2 rounded-full p-2 focus:outline-none transition">
              <i class="pi pi-arrow-circle-left" style="font-size: 1.5rem"></i>
            </button>
            <div class="flex items-center justify-center space-x-4">
              <img :src="`${api_base_url}${user.image}`" alt="Profile"
                class="w-16 h-16 rounded-full border-4 border-gray-200 shadow-lg" />
              <div>
                <label for="profile-pic" class="cursor-pointer text-[#ffc107] underline">
                  {{ user.image ? 'Change Picture' : 'Add Picture' }}
                </label>
                <input id="profile-pic" type="file" accept="image/*" class="hidden" @change="uploadProfilePicture" />
              </div>
              <div>
                <p class="text-xl font-semibold text-gray-800">Welcome, {{ user.first_name || user.email || 'John Doe'
                  }}</p>
              </div>
            </div>

            <hr class="my-6 border-gray-200" />

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <p class="flex items-center text-gray-700">
                <i class="bi bi-person-circle mr-2 text-xl text-gray-500"></i>
                <span><strong>Full Name:</strong> {{ user.first_name }} {{ user.last_name }}</span>
              </p>

              <p class="flex items-center text-gray-700">
                <i class="bi bi-envelope mr-2 text-xl text-gray-500"></i>
                <span><strong>Email:</strong> {{ user.email }}</span>
              </p>

              <p class="flex items-center text-gray-700">
                <i class="bi bi-phone mr-2 text-xl text-gray-500"></i>
                <span>
                  <strong>Phone Number:</strong> {{ user.phone_number || 'Not provided' }}
                  <button @click="phoneModalVisible = !phoneModalVisible" class="ml-2 text-[#ffc107] underline">
                    Edit
                  </button>
                </span>
              </p>

              <p class="flex items-center text-gray-700">
                <i class="bi bi-shield-lock mr-2 text-xl text-gray-500"></i>
                <span><strong>Role:</strong> {{ user.role || 'Not assigned' }}</span>
              </p>

              <!-- Address Information -->
              <p class="flex items-center text-gray-700">
                <i class="bi bi-building mr-2 text-xl text-gray-500"></i>
                <span><strong>Company Name:</strong> {{ user.user_address?.company_name || 'Not provided' }}</span>
              </p>

              <p class="flex items-center text-gray-700">
                <i class="bi bi-building mr-2 text-xl text-gray-500"></i>
                <span>
                  <strong>Address:</strong>
                  {{ user.user_address?.street_address || 'No address provided' }}
                </span>
              </p>

              <p class="flex items-center text-gray-700">
                <i class="bi bi-geo-alt mr-2 text-xl text-gray-500"></i>
                <span><strong>City:</strong> {{ user.user_address?.city || 'Not provided' }}</span>
              </p>

              <p class="flex items-center text-gray-700">
                <i class="bi bi-code-slash mr-2 text-xl text-gray-500"></i>
                <span><strong>Zip Code:</strong> {{ user.user_address?.zip_code || 'Not provided' }}</span>
              </p>



              <p class="flex items-center text-gray-700">
                <i class="bi bi-globe mr-2 text-xl text-gray-500"></i>
                <span><strong>Country:</strong> {{ user.user_address?.country || 'Not provided' }}</span>
              </p>
              <button @click="addressModalVisible = !addressModalVisible" class="ml-2 text-[#ffc107] underline">
                <i class="bi bi-pencil-square mr-2"></i>
                {{ user.user_address && user.user_address.id ? 'Edit Address' : 'Add Address' }}
              </button>

            </div>

          </div>



          <!-- My Equipments Section -->
          <div v-if="activeSection === 'my-equipments'">
            <button @click="closeSidebar"
              class="mr-4 text-gray-800 mt-2 rounded-full p-2 focus:outline-none transition">
              <i class="pi pi-arrow-circle-left" style="font-size: 1.5rem"></i>
            </button>
            <div v-if="equipments.length > 0">
              <div class="container mx-auto p-4">
                <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">

                  <!-- Loop through the filtered equipments -->
                  <div v-for="equipment in equipments" :key="equipment.id" @click="openEditModal(equipment)"
                    class="bg-white rounded-lg shadow-lg overflow-hidden transition-transform hover:scale-105 cursor-pointer">
                    <div class="relative">
                      <!-- Availability Badge -->
                      <span :class="{
                        'bg-green-500': equipment.is_available,
                        'bg-red-500': !equipment.is_available
                      }"
                        class="absolute top-2 left-2 text-white text-xs font-bold px-2 py-1 rounded flex items-center">
                        <i :class="{
                          'pi pi-check-circle': equipment.is_available,
                          'pi pi-times-circle': !equipment.is_available
                        }" class="mr-1"></i>
                        {{ equipment.is_available ? 'Available' : 'Unavailable' }}
                      </span>

                      <!-- Equipment Image -->
                      <img v-if="equipment.images.length > 0" :src="`${api_base_url}${equipment.images[0].image_url}`"
                        :alt="equipment.images[0].image_url" class="w-full h-48 object-cover" />
                      <img v-else src="https://via.placeholder.com/350" alt="Placeholder Image"
                        class="w-full h-48 object-cover" />

                      <!-- Edit Button -->
                      <a href="#" @click.stop="openEditModal(equipment)"
                        class="absolute bottom-4 right-4 bg-[#1c1c1c] text-white rounded-full h-10 w-10 flex items-center justify-center hover:text-[#ffc107] transition">
                        <i class="pi pi-pencil"></i>
                      </a>
                    </div>

                    <!-- Equipment Details -->
                    <div class="p-4">
                      <h5 class="text-lg font-semibold">{{ equipment.name }}</h5>
                      <p class="text-gray-600">{{ equipment.hourly_rate }} / Hr</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-else>
              <p>No equipment found.</p>
            </div>
          </div>




          <div v-if="activeSection === 'my-orders'">
  <button @click="closeSidebar"
    class="mr-4 text-gray-800 mt-2 rounded-full p-2 focus:outline-none transition">
    <i class="pi pi-arrow-circle-left" style="font-size: 1.5rem"></i>
  </button>
  <div class="p-6 bg-gray-100 min-h-screen">
    <h1 class="text-3xl font-bold text-gray-800 mb-4">Order Management</h1>

    <!-- Filters Section -->
    <div class="flex flex-wrap gap-4 mb-6">
      <select v-model="selectedStatus" @change="filterOrders"
        class="px-4 py-2 bg-white border rounded-md shadow-sm focus:outline-none focus:ring focus:ring-blue-300">
        <option value="">All Statuses</option>
        <option value="pending">Pending</option>
        <option value="approved">Approved</option>
        <option value="rented">Rented</option>
        <option value="rejected">Rejected</option>
        <option value="canceled">Canceled</option>
        <option value="completed">Completed</option>
      </select>
      <input v-model="searchQuery" @input="filterOrders" type="text" placeholder="Search by Order ID"
        class="px-4 py-2 bg-white border rounded-md shadow-sm focus:outline-none focus:ring focus:ring-[#1c1c1c]" />
    </div>

    <!-- Orders Table -->
    <div v-if="!loading" class="overflow-hidden rounded-lg shadow-lg bg-white">
      <div class="overflow-x-auto"> <!-- Make the table horizontally scrollable on small devices -->
        <table class="table-auto w-full border-collapse">
          <thead>
            <tr class="bg-gray-200 text-gray-600 uppercase text-sm leading-normal">
              <th class="py-3 px-6 text-left">Order ID</th>
              <th class="py-3 px-6 text-center">Status</th>
              <th class="py-3 px-6 text-center">Total Items</th>
              <th class="py-3 px-6 text-center">Total Price</th>
              <th class="py-3 px-6 text-center">Actions</th>
            </tr>
          </thead>
          <tbody class="text-gray-600 text-sm font-light">

            <tr v-for="order in filteredOrders" :key="order.id"
              class="border-b border-gray-200 hover:bg-gray-100">
              <td class="py-3 px-6 text-left">{{ order.id }}</td>
              <td class="py-3 px-6 text-center">
                <span :class="{
                  'px-3 py-1 rounded-full text-white': true,
                  'bg-yellow-500': order.status === 'pending',
                  'bg-green-500': order.status === 'approved',
                  'bg-blue-500': order.status === 'rented',
                  'bg-red-500': order.status === 'rejected',
                  'bg-red-500': order.status === 'canceled',
                  'bg-gray-500': order.status === 'completed',
                }">
                  {{ order.status }}
                </span>
              </td>
              <td class="py-3 px-6 text-center">{{ order.total_order_items }}</td>
              <td class="py-3 px-6 text-center">${{ order.order_total_price }}</td>
              <td class="py-3 px-6 text-center">
                <button @click="openModal(order)"
                  class="px-4 py-2 bg-blue-500 text-white rounded-md shadow-sm hover:bg-blue-600">
                  Manage
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else class="text-center">Loading orders...</div>
  </div>

  <!-- Modal -->
  <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
    <div class="bg-white rounded-lg shadow-lg w-96 p-6">
      <h2 class="text-xl font-semibold mb-4">Manage Order #{{ selectedOrder.id }}</h2>
      <p class="mb-4">Current Status: <strong>{{ selectedOrder.status }}</strong></p>

      <!-- Actions -->
      <div>
        <button v-if="selectedOrder.status === 'pending'"
          @click="performAction(selectedOrder.id, 'terminate')"
          class="px-4 py-2 bg-red-500 text-white rounded-md shadow-sm hover:bg-red-600">
          Terminate Rental
        </button>

        <button v-if="['rejected', 'canceled', 'completed'].includes(selectedOrder.status)"
          @click="performAction(selectedOrder.id, 'reorder')"
          class="px-4 py-2 bg-green-500 text-white rounded-md shadow-sm hover:bg-green-600">
          Reorder
        </button>

        <button @click="confirmDelete(selectedOrder)"
          class="mx-4 px-4 py-2 bg-red-500 text-white rounded-md shadow-sm hover:bg-red-600">
          Delete Rental
        </button>
      </div>

      <button @click="closeModal"
        class="mt-4 px-4 py-2 bg-gray-300 text-gray-800 rounded-md shadow-sm hover:bg-gray-400">
        Close
      </button>
    </div>
  </div>

  <!-- Delete Confirmation -->
  <div v-if="showDeleteConfirm"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
    <div class="bg-white rounded-lg shadow-lg w-96 p-6">
      <h2 class="text-xl font-semibold mb-4">Delete Order</h2>
      <p class="mb-4">Are you sure you want to delete Order #{{ orderToDelete.id }}?</p>
      <div class="flex justify-end">
        <button @click="performAction(orderToDelete.id, 'delete')"
          class="px-4 py-2 bg-red-500 text-white rounded-md shadow-sm hover:bg-red-600">
          Yes, Delete
        </button>
        <button @click="cancelDelete"
          class="ml-4 px-4 py-2 bg-gray-300 text-gray-800 rounded-md shadow-sm hover:bg-gray-400">
          Cancel
        </button>
      </div>
    </div>
  </div>
</div>



          <!-- <div v-if="activeSection === 'settings'">
            <h1>My equipments updated</h1>

          </div> -->


          <div v-if="activeSection === 'chats'" class="lg:px-4 py-2 min-h-screen flex flex-col lg:flex-row">

            <!-- Chat List -->
            <div v-if="!activeChat" class="w-full lg:w-3/3 bg-white shadow-lg rounded-lg overflow-hidden mb-4 lg:mb-0">

              <div class="border-b px-4 py-4 bg-[#ffc107] text-gray-800 font-bold text-lg flex items-center">
                <button @click="closeSidebar"
                  class="mr-4 text-gray-800 mt-2 rounded-full p-2 focus:outline-none transition">
                  <i class="pi pi-arrow-circle-left" style="font-size: 1.5rem"></i>
                </button>
                <div class="text-xl mr-2">💬</div>
                Chats
              </div>
              <ul class="divide-y divide-gray-200">
                <li v-for="chat in chats" :key="chat.id" @click="openChat(chat.id)"
                  class="px-4 py-3 hover:bg-[#ffe58a] cursor-pointer flex items-center transition">
                  <div
                    class="flex-shrink-0 w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center text-lg font-bold text-[#ffc107] shadow-md">
                    {{ chat.name.charAt(0) }}
                  </div>
                  <div class="ml-3 flex-1">
                    <p class="font-medium text-gray-800">{{ chat.name }}</p>
                    <p class="text-sm text-gray-600 truncate">{{ chat.lastMessage }}</p>
                  </div>
                  <h6 class="text-xs text-gray-500">{{ formatDate(chat.created_at) }}</h6>
                </li>
              </ul>
            </div>

            <!-- Messages Window -->
            <div v-if="activeChat" class="w-full lg:w-3/3 bg-white shadow-lg rounded-lg flex flex-col">
              <!-- Header -->
              <div class="border-b px-4 py-3 bg-[#ffc107] text-gray-800 font-bold flex items-center">
                <button @click="activeChat = null"
                  class="mr-4 text-gray-800 bg-[#ffe58a] hover:bg-[#ffd740] rounded-full p-2 focus:outline-none transition">
                  ←
                </button>
                <span>
                  {{ chats.find((chat) => chat.id === activeChat)?.name }}
                </span>
              </div>

              <!-- Chat Content -->
              <div class="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50 h-60 md:h-80 lg:h-auto">
                <div v-for="message in messages[activeChat]" :key="message.id"
                  :class="message.sentBy === 'me' ? 'justify-end' : 'justify-start'" class="flex">
                  <div class="flex flex-col">
                    <!-- Message -->
                    <p :class="{
                      'bg-[#ffe58a] text-gray-800': message.sentBy === 'me',
                      'bg-gray-200 text-gray-700': message.sentBy !== 'me',
                    }" class="inline-block px-4 py-2 rounded-xl shadow-md max-w-xs">
                      {{ message.text }}
                    </p>
                    <!-- Timestamp -->
                    <h6 class="text-xs text-gray-500 text-right mt-1">{{ formatDate(message.sent_at) }}</h6>
                  </div>
                </div>
              </div>

              <!-- Message Input -->
              <div class="border-t px-4 py-3 bg-gray-100 flex items-center">
                <input v-model="newMessage" type="text" placeholder="Type a message..."
                  class="flex-1 px-3 py-2 rounded-full border border-gray-300 bg-white text-gray-800 placeholder-gray-500 focus:ring-2 focus:ring-[#ffc107] outline-none shadow-sm transition" />
                <button @click="sendMessage"
                  class="ml-3 bg-[#ffc107] hover:bg-[#ffd740] text-gray-800 px-4 py-2 rounded-full shadow-md transition">
                  Send
                </button>
              </div>
            </div>
          </div>


          <div v-if="activeSection === 'reports'">
            <button @click="closeSidebar"
              class="mr-4 text-gray-800 mt-2 rounded-full p-2 focus:outline-none transition">
              <i class="pi pi-arrow-circle-left" style="font-size: 1.5rem"></i>
            </button>
            <h1>My Reports</h1>

          </div>

          <!-- Other Sections Content -->
          <div v-else>
            <p class="text-gray-600">{{ section.content }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- Modal for Editing Address -->
  <div v-if="addressModalVisible" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
    <div class="bg-white p-8 rounded-lg shadow-lg w-full sm:w-96">
      <h2 class="text-xl font-semibold mb-4">{{ user.user_address.id ? 'Update Address' : 'Add Address' }}</h2>
      <div class="mb-4">
        <label for="full_name" class="block text-sm font-medium">Full Name</label>
        <input v-model="user.user_address.full_name" id="full_name" type="text"
          class="mt-1 p-2 border border-gray-300 rounded-md w-full" placeholder="Enter full name" />
      </div>
      <div class="mb-4">
        <label for="street_address" class="block text-sm font-medium">Street Address</label>
        <input v-model="user.user_address.street_address" id="street_address" type="text"
          class="mt-1 p-2 border border-gray-300 rounded-md w-full" placeholder="Enter street address" />
      </div>
      <div class="mb-4">
        <label for="street_address2" class="block text-sm font-medium">Street Address Line 2</label>
        <input v-model="user.user_address.street_address2" id="street_address2" type="text"
          class="mt-1 p-2 border border-gray-300 rounded-md w-full" placeholder="Enter street address line 2" />
      </div>
      <div class="mb-4">
        <label for="city" class="block text-sm font-medium">City</label>
        <input v-model="user.user_address.city" id="city" type="text"
          class="mt-1 p-2 border border-gray-300 rounded-md w-full" placeholder="Enter city" />
      </div>
      <div class="mb-4">
        <label for="state" class="block text-sm font-medium">State</label>
        <input v-model="user.user_address.state" id="state" type="text"
          class="mt-1 p-2 border border-gray-300 rounded-md w-full" placeholder="Enter state" />
      </div>
      <div class="mb-4">
        <label for="zip_code" class="block text-sm font-medium">Zip Code</label>
        <input v-model="user.user_address.zip_code" id="zip_code" type="text"
          class="mt-1 p-2 border border-gray-300 rounded-md w-full" placeholder="Enter zip code" />
      </div>
      <div class="mb-4">
        <label for="country" class="block text-sm font-medium">Country</label>
        <input v-model="user.user_address.country" id="country" type="text"
          class="mt-1 p-2 border border-gray-300 rounded-md w-full" placeholder="Enter country" />
      </div>
      <div class="flex justify-between">
        <button @click="addressModalVisible = false" class="px-4 py-2 bg-gray-300 text-white rounded-md">Cancel</button>
        <button @click="updateAddress" class="px-4 py-2 bg-blue-500 text-white rounded-md">
          <i class="bi bi-pencil-square"></i> {{ user.user_address.id ? 'Save Address' : 'Add Address' }}
        </button>
      </div>
    </div>
  </div>

  <!-- Modal for Editing Phone Number -->
  <div v-if="phoneModalVisible" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
    <div class="bg-white p-8 rounded-lg shadow-lg w-full sm:w-96">
      <h2 class="text-xl font-semibold mb-4">Update Phone Number</h2>
      <div class="mb-4">
        <input v-model="phoneNumber" id="phone_number" type="text"
          class="mt-1 p-2 border border-gray-300 rounded-md w-full"
          :placeholder="user.phone_number || 'Enter phone number'" />
      </div>
      <div class="flex justify-between">
        <button @click="phoneModalVisible = false" class="px-4 py-2 bg-gray-300 text-white rounded-md">Cancel</button>
        <button @click="updatePhoneNumber" class="px-4 py-2 bg-blue-500 text-white rounded-md">Update</button>
      </div>
    </div>

  </div>

</template>



<script>
import { ref, onMounted, reactive } from 'vue';
import axios from 'axios';
import { useAuthStore } from '@/store/auth';

import { useRouter, useRoute } from 'vue-router';
import { format } from 'date-fns';

export default {
  setup() {


    const chats = ref([]); // List of chats
    const messages = reactive({}); // Messages for each chat, keyed by chat ID
    const activeChat = ref(null); // Currently open chat ID
    const newMessage = ref(""); // Message being typed  

    const categories = ref([]);

    const api_base_url = import.meta.env.VITE_API_BASE_URL;


    // Handle Logout functionality
    const handleLogout = async () => {
      await authStore.logout();  // Wait for the logout method to finish
      router.push('/'); // Redirect to login page
    };


    const editModalVisible = ref(false);
    const editedEquipment = reactive({
      id: null,
      name: '',
      hourly_rate: '',
      description: '',
      category: null,
      is_available: true,
      images: null,
    });

    const fetchCategories = async () => {
      // Fetch categories from your API
      const response = await axios.get(`${api_base_url}/api/categories`);
      categories.value = response.data;
    };



    const openEditModal = (equipment) => {
      Object.assign(editedEquipment, equipment); // Clone the equipment into the editedEquipment
      fetchCategories(); // Fetch categories for the dropdown
      editModalVisible.value = true;
    };

    const closeEditModal = () => {
      editModalVisible.value = false;
      Object.assign(editedEquipment, { id: null, name: '', hourly_rate: '', description: '', category: null, is_available: true, image: null });
    };

    const handleImageUpload = (event) => {
      const files = event.target.files;
      if (files.length > 0) {
        // Store the selected files in an array
        editedEquipment.images = Array.from(files); // Store multiple images in an array
      }
    };

    const updateEquipment = async () => {
      const payload = {};
      const formData = new FormData();

      // Append regular fields to the formData
      formData.append('name', editedEquipment.name);
      formData.append('hourly_rate', editedEquipment.hourly_rate);
      formData.append('description', editedEquipment.description);
      formData.append('category', editedEquipment.category);
      formData.append('is_available', editedEquipment.is_available);

      // Check if there are any images and convert them to base64 if necessary
      if (editedEquipment.images && editedEquipment.images.length > 0) {
        for (const image of editedEquipment.images) {
          // Convert image to base64
          const base64String = await fileToBase64(image);

          // Add the base64 string to the payload (if needed for future use)
          payload['images'] = payload['images'] || [];
          payload['images'].push({ base64: base64String, name: image.name, type: image.type });

          // Append each image file to the FormData for file upload
          formData.append('images', image); // Append each image as 'images[]'
        }
      }

      try {
        // Make the API call to update the equipment
        await axios.put(`${api_base_url}/api/equipments/${editedEquipment.id}/`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });

        // Close the modal and refresh the equipment list after successful update
        closeEditModal();
        fetchUserEquipments(); // Refresh the equipment list
      } catch (error) {
        console.error('Error updating equipment:', error);
      }
    };

    // Helper function to convert file to base64
    const fileToBase64 = (file) => {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result.split(',')[1]); // Remove data URL prefix
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
    };

    // Fetch the list of chats
    const fetchChats = async () => {
      try {
        const response = await axios.get(`${api_base_url}/api/accounts/chats/`, { withCredentials: true });

        chats.value = response.data.map((chat) => {
          const otherParticipant = chat.participants.find((participant) => participant.id !== authStore.user.id);

          return {
            id: chat.id,
            name: otherParticipant?.username || "Unknown",
            lastMessage: chat.messages.length
              ? chat.messages[chat.messages.length - 1].content
              : "No messages yet",
            created_at: chat.created_at,
            participants: chat.participants,
          };
        });
      } catch (error) {
        console.error("Error fetching chats:", error);
      }
    };

    // Fetch messages for a specific chat
    const fetchMessages = async (chatId) => {
      try {
        const response = await axios.get(`${api_base_url}/api/accounts/chats/${chatId}/`, {
          withCredentials: true,
        });

        messages[chatId] = response.data.messages.map((msg) => ({
          id: msg.id,
          text: msg.content,
          sentBy: msg.sender === authStore.user.id ? 'me' : 'them',
          sent_at: msg.sent_at,
          sender: msg.sender
        }));
        activeChat.value = chatId;
      } catch (error) {
        console.error("Error fetching messages:", error);
      }
    };

    // Send a new message
    const sendMessage = async () => {
      if (!newMessage.value.trim()) return; // Don't send empty messages

      try {
        const response = await axios.post(
          `${api_base_url}/api/accounts/messages/`,
          {
            content: newMessage.value,
            chat: activeChat.value, // Current chat ID
            receiver: getReceiverId(activeChat.value), // Get receiver ID for this chat
          },
          { withCredentials: true }
        );

        fetchMessages(activeChat.value);
        newMessage.value = ""; // Clear input field
      } catch (error) {
        console.error("Error sending message:", error);
      }
    };


    // Open a chat and fetch its messages
    const openChat = (chatId) => {
      if (!messages[chatId]) {
        fetchMessages(chatId);
      } else {
        activeChat.value = chatId;
      }
    };

    // Get the receiver's ID for a given chat
    const getReceiverId = (chatId) => {
      const chat = chats.value.find((c) => c.id === chatId);
      const receiver = chat.participants[0] !== authStore.user.id ? chat.participants[0].id : chat.participants[1].id;

      return receiver;
    };



    // Initialize the auth store
    const authStore = useAuthStore();
    const router = useRouter();
    const showModal = ref(false);
    const selectedOrder = ref(null);
    const showDeleteConfirm = ref(false);
    const orderToDelete = ref(null);


    const openModal = (order) => {
      selectedOrder.value = order;
      showModal.value = true;
    };

    const closeModal = () => {
      showModal.value = false;
      selectedOrder.value = null;
      showDeleteConfirm.value = false;
    };


    const confirmDelete = (order) => {
      orderToDelete.value = order;
      showDeleteConfirm.value = true;
    };

    const cancelDelete = () => {
      showDeleteConfirm.value = false;
      orderToDelete.value = null;
    };

    const deleteOrder = (orderId) => {
      // API call to delete the order
      showDeleteConfirm.value = false;
      closeModal();
      // Remove order from UI after success
    };


    // Handle order action
    const performAction = async (order, action) => {
      try {
        const response = await axios.post(`${api_base_url}/api/orders/${order}/${action}/`, {}, {
          withCredentials: true,  // This ensures cookies (credentials) are sent with the request
        });
        showModal.value = false;
        await fetchOrders(); // Refresh order list
        closeModal()
      } catch (error) {
        console.error(error);
        alert(error.response?.data?.error || "An error occurred");
      }
    };



    // Reactive state variables
    const activeSection = ref("personal-info");
    const phoneNumber = ref("");

    const equipments = ref([]); // To hold the fetched equipment data

    // Fetch user equipments on mount with credentials
    const fetchUserEquipments = async () => {
      try {
        const response = await axios.get(`${api_base_url}/api/equipments/`, {
          withCredentials: true,  // This ensures cookies (credentials) are sent with the request
        });
        equipments.value = response.data;  // Assign the fetched equipment to `equipments`
      } catch (error) {
        console.error('Error fetching user equipment:', error);
      }
    };

    const goToDetail = (equipmentId) => {
      if (equipmentId) {
        router.push({ name: 'equipment-details', params: { id: equipmentId } });
      } else {
        console.error('Equipment ID is missing!'); // Log an error if ID is missing
      }
    }



    const orders = ref([]);
    const filteredOrders = ref([]);
    const searchQuery = ref('');
    const selectedStatus = ref('');
    const loading = ref(true);

    const fetchOrders = async () => {
      try {
        const response = await axios.get(`${api_base_url}/api/orders/`, {
          withCredentials: true,
        });
        orders.value = response.data;
        filteredOrders.value = response.data; // Initial population
      } catch (error) {
        console.error('Error fetching orders:', error);
      } finally {
        loading.value = false;
      }
    };

    const filterOrders = () => {
      filteredOrders.value = orders.value.filter((order) => {
        return (
          (selectedStatus.value ? order.status === selectedStatus.value : true) &&
          (searchQuery.value
            ? order.id.toLowerCase().includes(searchQuery.value.toLowerCase())
            : true)
        );
      });
    };





    // Mock user object for demonstration purposes
    const user = ref({
      user_address: {
        full_name: '',  // Default value
        street_address: '',
        city: '',
        state: '',
        zip_code: '',
        country: ''
      }
    });
    const addressModalVisible = ref(false);
    const phoneModalVisible = ref(false);
    const showSidebar = ref(true); // Sidebar visibility state

    const closeSidebar = () => {

      showSidebar.value = true;
      activeSection.value = null;

    };



    const route = useRoute();

   // Function to navigate to a section
const navigateToSection = (sectionName) => {
  activeSection.value = sectionName;

  // Update URL query parameter
  router.replace({ query: { section: sectionName } });

  // Scroll to the section
  const sectionElement = document.getElementById(sectionName);
  if (sectionElement) {
    sectionElement.scrollIntoView({ behavior: "smooth" });
  }

  // Hide sidebar on small devices
  if (window.innerWidth < 1024) {
    showSidebar.value = false;
  }
};


    const sections = [
      { name: "personal-info", label: "Personal Information" },
      { name: "my-equipments", label: "My Equipments", show: authStore.user.role === 'lessor' },
      { name: "my-orders", label: "My Orders", show: authStore.user.role === 'lessee' },
      // { name: "settings", label: "Settings", content: "Adjust your preferences..." },
      { name: "chats", label: "Chats" },
      { name: "reports", label: "Reports", },
    ];

    const otherSections = [
      { name: "my-equipments", label: "My Equipments" },
      { name: "my-orders", label: "My Orders" },
      // { name: "settings", label: "Settings" },
      { name: "chats", label: "Chats" },
      { name: "reports", label: "Reports" },
    ];

    // Filter sections to only include those that should be shown
    const visibleSections = sections.filter(section => section.show !== false);


    // Method to set the active section
    const setActiveSection = (sectionName) => {
      activeSection.value = sectionName;
    };


    const uploadProfilePicture = async (event) => {
      const file = event.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append('image', file);

      try {
        const response = await axios.put(`${api_base_url}/api/accounts/users/${authStore.user.id}/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          withCredentials: true, // Include authentication cookies
        });

        user.image = response.data.image_url; // Update the image URL
        await getUserData();
      } catch (error) {
        console.error(error);
      }
    };

    // Fetch user data from API
    const getUserData = async () => {
      try {
        const response = await axios.get(
          `${api_base_url}/api/accounts/users/${authStore.user.id}/`,
          { withCredentials: true }
        );
        user.value = {
          ...response.data,
          user_address: response.data.user_address || {
            full_name: '',
            street_address: '',
            street_address2: '',
            city: '',
            state: '',
            zip_code: '',
            country: ''
          }
        };
      } catch (error) {
        console.error("Error fetching user data:", error);
      }
    };

    // Update phone number via PUT request
    const updatePhoneNumber = async () => {
      try {
        const updatedUserData = { phone_number: phoneNumber.value };
        const response = await axios.put(
          `${api_base_url}/api/accounts/users/${authStore.user.id}/`,
          updatedUserData,
          { withCredentials: true }
        );
        user.value = response.data;

        phoneModalVisible.value = false;
      } catch (error) {
        console.error("Error updating phone number:", error);
      }
    };

    const updateAddress = async () => {
      try {
        const updatedAddressData = {
          full_name: user.value.user_address?.full_name || "",
          street_address: user.value.user_address?.street_address || "",
          street_address2: user.value.user_address?.street_address2 || "",
          city: user.value.user_address?.city || "",
          state: user.value.user_address?.state || "",
          zip_code: user.value.user_address?.zip_code || "",
          country: user.value.user_address?.country || "",
        };

        let response;
        if (user.value.user_address.id) {
          // Update existing address
          response = await axios.put(
            `${api_base_url}/api/accounts/physical-addresses/${user.value.user_address.id}/`,
            updatedAddressData,
            { withCredentials: true }
          );
        } else {
          // Add new address
          response = await axios.post(
            `${api_base_url}/api/accounts/physical-addresses/`,
            updatedAddressData,
            { withCredentials: true }
          );
        }

        user.value.user_address = response.data;
        addressModalVisible.value = false;

      } catch (error) {
        console.error("Error saving address:", error);
      }
    };



    const formatDate = (date) => {
      try {
        return format(new Date(date), 'Ppp');
      } catch (error) {
        return 'Invalid Date';
      }
    };



    // Fetch user data when the component is mounted
    onMounted(() => {
      const section = route.query.section;
  if (section) {
    navigateToSection(section);
  }
      getUserData();
      fetchChats();
      fetchUserEquipments();
      fetchOrders();  // Fetch orders on mount
    });

    return {
      navigateToSection,
      closeSidebar,
      showSidebar,
      api_base_url,
      handleLogout,
      visibleSections,
      formatDate,

      categories,

      editModalVisible,
      editedEquipment,
      openEditModal,
      closeEditModal,
      handleImageUpload,
      updateEquipment,

      fetchChats,
      fetchMessages,


      getReceiverId,
      chats,
      messages,
      activeChat,
      newMessage,
      openChat,
      sendMessage,
      showDeleteConfirm,
      orderToDelete,
      confirmDelete,
      cancelDelete,
      performAction,
      showModal,
      openModal,
      closeModal,
      selectedOrder,
      orders,
      filteredOrders,
      searchQuery,
      selectedStatus,
      filterOrders,
      loading,
      equipments,
      goToDetail,
      uploadProfilePicture,
      authStore,
      activeSection,
      phoneNumber,
      user,
      addressModalVisible,
      phoneModalVisible,
      sections,
      otherSections,
      setActiveSection,
      updatePhoneNumber,
      updateAddress,
    };
  },
};
</script>
