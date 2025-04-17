<template>
    <div class="min-h-screen bg-amber-50 py-12">
      <div class="max-w-4xl mx-auto space-y-6">
        <!-- Header Section -->
        <div class="bg-gradient-to-r from-amber-400 to-amber-600 text-[#1c1c1c] rounded-2xl shadow-xl p-8 text-center">
          <h2 class="text-4xl font-extrabold tracking-wide">Account Dashboard</h2>
          <p class="mt-2 text-[#1c1c1c]/80">Your personal hub for managing details.</p>
        </div>
  
        <!-- Profile Card -->
        <div class="bg-white rounded-2xl shadow-lg p-6 flex flex-col sm:flex-row items-center gap-6">
          <div class="relative">
            <img
              :src="`${api_base_url}/${authStore.user?.image || 'default-profile.png'}`"
              alt="Profile"
              class="w-20 h-20 rounded-full border-4 border-amber-200 object-cover"
            />
            <button
              @click="openImageModal"
              class="absolute bottom-0 right-0 bg-amber-500 text-[#1c1c1c] rounded-full p-2 hover:bg-amber-600 transition-colors"
            >
              <i class="pi pi-camera"></i>
            </button>
          </div>
          <div class="text-center sm:text-left">
            <h3 class="text-2xl font-bold text-[#1c1c1c]">
              {{ authStore.user?.first_name || 'Unknown' }} {{ authStore.user?.last_name || '' }}
            </h3>
            <p class="mt-1 text-amber-600">{{ authStore.user?.email || 'No email provided' }}</p>
          </div>
        </div>
  
        <!-- Info Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="bg-white rounded-2xl shadow-md p-5">
            <p class="text-sm text-[#1c1c1c]/60 uppercase">Email</p>
            <p class="text-lg font-semibold text-[#1c1c1c]">{{ authStore.user?.email || 'Not provided' }}</p>
          </div>
          <div class="bg-white rounded-2xl shadow-md p-5">
            <p class="text-sm text-[#1c1c1c]/60 uppercase">Phone</p>
            <p class="text-lg font-semibold text-[#1c1c1c]">{{ authStore.user?.phone_number || 'Not provided' }}</p>
            <button
              @click="openPhoneModal"
              class="mt-2 text-amber-600 hover:text-amber-700 flex items-center gap-2"
            >
              <i class="bi bi-pencil-square"></i>{{ authStore.user?.phone_number ? 'Edit' : 'Add' }} Phone
            </button>
          </div>
          <div class="bg-white rounded-2xl shadow-md p-5">
            <p class="text-sm text-[#1c1c1c]/60 uppercase">Role</p>
            <p class="text-lg font-semibold text-[#1c1c1c]">{{ authStore.user?.role || 'Not assigned' }}</p>
          </div>
          <div class="bg-white rounded-2xl shadow-md p-5">
            <p class="text-sm text-[#1c1c1c]/60 uppercase">Company</p>
            <p class="text-lg font-semibold text-[#1c1c1c]">{{ authStore.user?.user_address?.company_name || 'Not provided' }}</p>
            <button
              @click="openAddressModal"
              class="mt-2 text-amber-600 hover:text-amber-700 flex items-center gap-2"
            >
              <i class="bi bi-pencil-square"></i>{{ authStore.user?.user_address?.id ? 'Edit' : 'Add' }} Address
            </button>
          </div>
          <div class="bg-white rounded-2xl shadow-md p-5">
            <p class="text-sm text-[#1c1c1c]/60 uppercase">Address</p>
            <p class="text-lg font-semibold text-[#1c1c1c]">{{ authStore.user?.user_address?.street_address || 'Not provided' }}</p>
          </div>
          <div class="bg-white rounded-2xl shadow-md p-5">
            <p class="text-sm text-[#1c1c1c]/60 uppercase">City</p>
            <p class="text-lg font-semibold text-[#1c1c1c]">{{ authStore.user?.user_address?.city || 'Not provided' }}</p>
          </div>
          <div class="bg-white rounded-2xl shadow-md p-5">
            <p class="text-sm text-[#1c1c1c]/60 uppercase">Zip Code</p>
            <p class="text-lg font-semibold text-[#1c1c1c]">{{ authStore.user?.user_address?.zip_code || 'Not provided' }}</p>
          </div>
          <div class="bg-white rounded-2xl shadow-md p-5">
            <p class="text-sm text-[#1c1c1c]/60 uppercase">Country</p>
            <p class="text-lg font-semibold text-[#1c1c1c]">{{ authStore.user?.user_address?.country || 'Not provided' }}</p>
          </div>
        </div>
  
        <!-- Role Switch Card -->
        <div class="bg-white rounded-2xl shadow-lg p-6 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <i class="bi bi-shield-lock text-2xl text-amber-600"></i>
            <span class="text-lg font-semibold text-[#1c1c1c]">Role: {{ authStore.user?.role || 'Not assigned' }}</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-sm text-[#1c1c1c]/70">Switch to {{ authStore.user?.role === 'lessor' ? 'lessee' : 'lessor' }}</span>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                v-model="authStore.isOn"
                class="sr-only peer"
                @change="authStore.updateUserRole()"
              />
              <div
                class="w-12 h-6 bg-[#1c1c1c]/20 rounded-full peer-checked:bg-amber-600 peer-checked:after:translate-x-6 after:content-[''] after:absolute after:left-0.5 after:top-0.5 after:w-5 after:h-5 after:rounded-full after:bg-white transition-all"
              ></div>
            </label>
          </div>
        </div>
  
        <!-- Image Modal -->
        <div v-if="imageModalVisible" class="fixed inset-0 bg-[#1c1c1c]/50 flex items-center justify-center z-50">
          <div class="bg-white rounded-2xl p-8 w-full max-w-md animate-pop">
            <h3 class="text-xl font-bold text-[#1c1c1c] mb-4">{{ authStore.user?.image ? 'Update' : 'Add' }} Profile Picture</h3>
            <form @submit.prevent="uploadProfilePicture">
              <div class="mb-4">
                <label for="profile-pic" class="block text-sm font-medium text-[#1c1c1c]/70">Choose Image</label>
                <input
                  id="profile-pic"
                  type="file"
                  accept="image/*"
                  class="mt-1 block w-full border-[#1c1c1c]/20 rounded-lg shadow-sm focus:ring-amber-500 focus:border-amber-500"
                  @change="handleImageSelect"
                  required
                />
              </div>
              <div class="flex justify-end gap-3">
                <button
                  type="button"
                  @click="imageModalVisible = false"
                  class="px-4 py-2 bg-[#1c1c1c]/10 rounded-lg hover:bg-[#1c1c1c]/20"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  :disabled="isUploading"
                  class="px-4 py-2 bg-amber-600 text-[#1c1c1c] rounded-lg hover:bg-amber-700 disabled:opacity-50"
                >
                  {{ isUploading ? 'Uploading...' : 'Save' }}
                </button>
              </div>
            </form>
          </div>
        </div>
  
        <!-- Phone Modal -->
        <div v-if="phoneModalVisible" class="fixed inset-0 bg-[#1c1c1c]/50 flex items-center justify-center z-50">
          <div class="bg-white rounded-2xl p-8 w-full max-w-md animate-pop">
            <h3 class="text-xl font-bold text-[#1c1c1c] mb-4">{{ authStore.user?.phone_number ? 'Update' : 'Add' }} Phone Number</h3>
            <form @submit.prevent="updatePhone">
              <div class="mb-4">
                <label for="phone" class="block text-sm font-medium text-[#1c1c1c]/70">Phone Number</label>
                <input
                  id="phone"
                  v-model="phoneForm.phone_number"
                  type="tel"
                  class="mt-1 block w-full border-[#1c1c1c]/20 rounded-lg shadow-sm focus:ring-amber-500 focus:border-amber-500"
                  pattern="[0-9]{10,15}"
                  placeholder="e.g., 1234567890"
                  required
                />
              </div>
              <div class="flex justify-end gap-3">
                <button
                  type="button"
                  @click="phoneModalVisible = false"
                  class="px-4 py-2 bg-[#1c1c1c]/10 rounded-lg hover:bg-[#1c1c1c]/20"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  :disabled="isUpdating"
                  class="px-4 py-2 bg-amber-600 text-[#1c1c1c] rounded-lg hover:bg-amber-700 disabled:opacity-50"
                >
                  {{ isUpdating ? 'Saving...' : 'Save' }}
                </button>
              </div>
            </form>
          </div>
        </div>
  
        <!-- Address Modal -->
        <div v-if="addressModalVisible" class="fixed inset-0 bg-[#1c1c1c]/50 flex items-center justify-center z-50">
          <div class="bg-white rounded-2xl p-8 w-full max-w-md animate-pop">
            <h3 class="text-xl font-bold text-[#1c1c1c] mb-4">{{ authStore.user?.user_address?.id ? 'Update' : 'Add' }} Address</h3>
            <form @submit.prevent="updateAddress">
              <div class="mb-4">
                <label for="company" class="block text-sm font-medium text-[#1c1c1c]/70">Company Name</label>
                <input
                  id="company"
                  v-model="addressForm.company_name"
                  type="text"
                  class="mt-1 block w-full border-[#1c1c1c]/20 rounded-lg shadow-sm focus:ring-amber-500 focus:border-amber-500"
                />
              </div>
              <div class="mb-4">
                <label for="street" class="block text-sm font-medium text-[#1c1c1c]/70">Street Address</label>
                <input
                  id="street"
                  v-model="addressForm.street_address"
                  type="text"
                  class="mt-1 block w-full border-[#1c1c1c]/20 rounded-lg shadow-sm focus:ring-amber-500 focus:border-amber-500"
                  required
                />
              </div>
              <div class="mb-4">
                <label for="city" class="block text-sm font-medium text-[#1c1c1c]/70">City</label>
                <input
                  id="city"
                  v-model="addressForm.city"
                  type="text"
                  class="mt-1 block w-full border-[#1c1c1c]/20 rounded-lg shadow-sm focus:ring-amber-500 focus:border-amber-500"
                  required
                />
              </div>
              <div class="mb-4">
                <label for="zip" class="block text-sm font-medium text-[#1c1c1c]/70">Zip Code</label>
                <input
                  id="zip"
                  v-model="addressForm.zip_code"
                  type="text"
                  class="mt-1 block w-full border-[#1c1c1c]/20 rounded-lg shadow-sm focus:ring-amber-500 focus:border-amber-500"
                  required
                />
              </div>
              <div class="mb-4">
                <label for="country" class="block text-sm font-medium text-[#1c1c1c]/70">Country</label>
                <input
                  id="country"
                  v-model="addressForm.country"
                  type="text"
                  class="mt-1 block w-full border-[#1c1c1c]/20 rounded-lg shadow-sm focus:ring-amber-500 focus:border-amber-500"
                  required
                />
              </div>
              <div class="flex justify-end gap-3">
                <button
                  type="button"
                  @click="addressModalVisible = false"
                  class="px-4 py-2 bg-[#1c1c1c]/10 rounded-lg hover:bg-[#1c1c1c]/20"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  :disabled="isUpdating"
                  class="px-4 py-2 bg-amber-600 text-[#1c1c1c] rounded-lg hover:bg-amber-700 disabled:opacity-50"
                >
                  {{ isUpdating ? 'Saving...' : 'Save' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import  axios  from 'axios';
  import { useAuthStore } from '../store/auth';
  
  const authStore = useAuthStore();
  const api_base_url = import.meta.env.VITE_API_BASE_URL;
  
  const imageModalVisible = ref(false);
  const phoneModalVisible = ref(false);
  const addressModalVisible = ref(false);
  const isUploading = ref(false);
  const isUpdating = ref(false);
  
  // Form data
  const phoneForm = ref({
    phone_number: '',
  });
  const addressForm = ref({
    company_name: '',
    street_address: '',
    city: '',
    zip_code: '',
    country: '',
  });
  const selectedImage = ref(null);
  
  const openImageModal = () => {
    selectedImage.value = null;
    imageModalVisible.value = true;
  };
  
  const openPhoneModal = () => {
    phoneForm.value.phone_number = authStore.user?.phone_number || '';
    phoneModalVisible.value = true;
  };
  
  const openAddressModal = () => {
    addressForm.value = {
      company_name: authStore.user?.user_address?.company_name || '',
      street_address: authStore.user?.user_address?.street_address || '',
      city: authStore.user?.user_address?.city || '',
      zip_code: authStore.user?.user_address?.zip_code || '',
      country: authStore.user?.user_address?.country || '',
    };
    addressModalVisible.value = true;
  };
  
  const handleImageSelect = (event) => {
    selectedImage.value = event.target.files[0];
  };
  
  const uploadProfilePicture = async () => {
    if (!selectedImage.value) return;
    if (selectedImage.value.size > 5 * 1024 * 1024) {
      alert('Image size should be less than 5MB');
      return;
    }
  
    isUploading.value = true;
    const formData = new FormData();
    formData.append('image', selectedImage.value);
  
    try {
      const response = await axios.put(
        `${api_base_url}/api/accounts/users/${authStore.user?.id}/`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          withCredentials: true,
        }
      );
      authStore.user.image = response.data.image_url || response.data.image;
      await authStore.getUserData();
      imageModalVisible.value = false;
    } catch (error) {
      console.error('Error uploading profile picture:', error);
      alert('Failed to upload profile picture. Please try again.');
    } finally {
      isUploading.value = false;
    }
  };
  
  const updatePhone = async () => {
    if (!phoneForm.value.phone_number.match(/^[0-9]{10,15}$/)) {
      alert('Please enter a valid phone number (10-15 digits).');
      return;
    }
  
    isUpdating.value = true;
    try {
      const updatedUserData = { phone_number: phoneForm.value.phone_number };
      const response = await axios.put(
        `${api_base_url}/api/accounts/users/${authStore.user?.id}/`,
        updatedUserData,
        { withCredentials: true }
      );
      authStore.user.phone_number = response.data.phone_number;
      await authStore.getUserData();
      phoneModalVisible.value = false;
    } catch (error) {
      console.error('Error updating phone number:', error);
      alert('Failed to update phone number. Please try again.');
    } finally {
      isUpdating.value = false;
    }
  };
  
  const updateAddress = async () => {
    if (!addressForm.value.street_address || !addressForm.value.city || !addressForm.value.zip_code || !addressForm.value.country) {
      alert('Please fill in all required address fields.');
      return;
    }
  
    isUpdating.value = true;
    const updatedAddressData = {
      company_name: addressForm.value.company_name || '',
      street_address: addressForm.value.street_address,
      city: addressForm.value.city,
      zip_code: addressForm.value.zip_code,
      country: addressForm.value.country,
    };
  
    try {
      let response;
      if (authStore.user?.user_address?.id) {
        // Update existing address
        response = await axios.put(
          `${api_base_url}/api/accounts/physical-addresses/${authStore.user.user_address.id}/`,
          updatedAddressData,
          { withCredentials: true }
        );
      } else {
        // Add new address
        response = await axios.post(
          `${api_base_url}/api/accounts/physical-addresses/`,
          { ...updatedAddressData, user: authStore.user?.id },
          { withCredentials: true }
        );
      }
      authStore.user.user_address = response.data;
      await authStore.getUserData();
      addressModalVisible.value = false;
    } catch (error) {
      console.error('Error updating address:', error);
      alert('Failed to update address. Please try again.');
    } finally {
      isUpdating.value = false;
    }
  };
  </script>
  
  <style scoped>
  .animate-pop {
    animation: pop 0.3s ease-out;
  }
  
  @keyframes pop {
    0% {
      transform: scale(0.8);
      opacity: 0;
    }
    100% {
      transform: scale(1);
      opacity: 1;
    }
  }
  </style>