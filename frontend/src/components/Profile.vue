<template>
  <div class="grid grid-cols-12 gap-8 p-8">
    <!-- Sidebar -->
    <div class="col-span-12 md:col-span-4 lg:col-span-3 bg-white p-4 rounded-lg shadow-md">
      <div class="flex items-center space-x-4 mb-6">
        <i class="bi bi-person text-black text-2xl"></i>
        <span class="text-lg font-medium">Welcome, {{ user.first_name || "John Doe" }}</span>
      </div>
      <hr class="my-4">

      <!-- Personal Information Section (Yellow color) -->
      <div class="nav-item text-white bg-[#ffc107] font-semibold py-2 px-4 rounded-md mb-4 cursor-pointer"
        :class="{ 'text-white bg-[#1c1c1c]': activeSection === 'personal-info' }"
        @click="setActiveSection('personal-info')">
        Personal Information
      </div>

      <!-- Other Sections (Dark Gray) -->
      <div v-for="(section, index) in otherSections" :key="index" :class="{
        'text-white bg-[#1c1c1c]': activeSection === section.name,
        'text-[#ffc107]': activeSection !== section.name
      }" class="nav-item font-semibold py-2 px-4 rounded-md cursor-pointer mb-2"
        @click="setActiveSection(section.name)">
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
            <div class="flex items-center space-x-4">
              <img :src="`http://127.0.0.1:8000${user.image}`"  alt="Profile"
                class="w-16 h-16 rounded-full border-4 border-gray-200 shadow-lg" />
              <div>
                <label for="profile-pic" class="cursor-pointer text-blue-600 underline">
                  {{ user.image ? 'Change Picture' : 'Add Picture' }}
                </label>
                <input id="profile-pic" type="file" accept="image/*" class="hidden" @change="uploadProfilePicture" />
              </div>
              <div>
                <p class="text-xl font-semibold text-gray-800">Welcome, {{ user.first_name || 'John Doe' }}</p>
                <p class="text-gray-500 text-sm">Manage your personal details below.</p>
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
                  <button @click="phoneModalVisible = !phoneModalVisible" class="ml-2 text-blue-600 underline">
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
              <button @click="addressModalVisible = !addressModalVisible" class="ml-2 text-blue-600 underline">
                <i class="bi bi-pencil-square mr-2"></i>
                {{ user.user_address.id ? 'Edit Address' : 'Add Address' }}
              </button>
            </div>

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
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useAuthStore } from '@/store/auth';
export default {
  setup() {
    // Initialize the auth store
    const authStore = useAuthStore();

    // Reactive state variables
    const activeSection = ref("personal-info");
    const phoneNumber = ref("");

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

    const sections = [
      { name: "personal-info", label: "Personal Information", content: "Manage your personal information here..." },
      { name: "my-equipments", label: "My Equipments", content: "Manage your equipments here..." },
      { name: "my-orders", label: "My Orders", content: "View your order history..." },
      { name: "settings", label: "Settings", content: "Adjust your preferences..." },
      { name: "wishlist", label: "Wishlist", content: "View your saved items..." },
      { name: "chats", label: "Chats", content: "Check your conversations..." },
      { name: "reports", label: "Reports", content: "View your account reports..." },
    ];

    const otherSections = [
      { name: "my-equipments", label: "My Equipments" },
      { name: "my-orders", label: "My Orders" },
      { name: "settings", label: "Settings" },
      { name: "wishlist", label: "Wishlist" },
      { name: "chats", label: "Chats" },
      { name: "reports", label: "Reports" },
    ];

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
        const response = await axios.put(`${import.meta.env.VITE_API_BASE_URL}/api/accounts/users/${authStore.user.id}/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          withCredentials: true, // Include authentication cookies
        });

        user.image = response.data.image_url; // Update the image URL
        alert("Image successful");
      } catch (error) {
        console.error(error);
      }
    };

    // Fetch user data from API
    const getUserData = async () => {
      try {
        const response = await axios.get(
          `${import.meta.env.VITE_API_BASE_URL}/api/accounts/users/${authStore.user.id}/`,
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
          `${import.meta.env.VITE_API_BASE_URL}/api/accounts/users/${authStore.user.id}/`,
          updatedUserData,
          { withCredentials: true }
        );
        user.value = response.data;

        phoneModalVisible.value = false;
        alert("Phone number updated successfully!");
      } catch (error) {
        console.error("Error updating phone number:", error);
        alert("There was an error updating your phone number.");
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
            `${import.meta.env.VITE_API_BASE_URL}/api/accounts/physical-addresses/${user.value.user_address.id}/`,
            updatedAddressData,
            { withCredentials: true }
          );
        } else {
          // Add new address
          response = await axios.post(
            `${import.meta.env.VITE_API_BASE_URL}/api/accounts/physical-addresses/`,
            updatedAddressData,
            { withCredentials: true }
          );
        }

        user.value.user_address = response.data;
        addressModalVisible.value = false;

        console.log(user.value)
      } catch (error) {
        console.error("Error saving address:", error);
      }
    };


    // Fetch user data when the component is mounted
    onMounted(() => {
      getUserData();
    });

    return {
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
