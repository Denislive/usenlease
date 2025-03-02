<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100 p-4">
    <div class="bg-white shadow-md rounded-lg p-6 w-full max-w-lg">
      <div class="flex justify-center items-center">
        <img src="../assets/images/logo.jpeg" alt="logo" class="h-30 w-40">
      </div>
      <h2 class="text-2xl font-bold text-center my-6">List Item</h2>
      <form @submit.prevent="handleSubmit">
        <!-- Item Name -->
        <div class="mb-4 relative">
          <label for="itemName" class="block text-sm font-medium text-gray-700">Item Name</label>
          <input type="text" id="itemName" placeholder="Item Name" v-model="itemName" @input="validateItemName" :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none',
            itemNameError ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-[#1c1c1c]']">
          <p v-if="itemNameError" class="absolute text-red-500 text-sm mt-1">{{ itemNameError }}</p>
        </div>

        <!-- Category -->
        <div class="mb-4 relative">
          <label for="category" class="block text-sm font-medium text-gray-700">Category</label>
          <select id="category" v-model="selectedCategory" @change="validateCategory" required :class="[
            'mt-1 block w-full border rounded-md p-2 focus:outline-none',
            categoryError ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-[#1c1c1c]'
          ]">
            <option value="" disabled selected>Select a category</option>
            <option v-for="(cat, index) in categories" :key="index" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
          <p v-if="categoryError" class="text-red-500 text-sm mt-1">{{ categoryError }}</p>
        </div>

        <!-- Hourly Rate -->
        <div class="mb-4 relative">
          <label for="hourlyRate" class="block text-sm font-medium text-gray-700">Hourly Rate</label>
          <input type="number" id="hourlyRate" placeholder="99.99" v-model.number="hourlyRate"
            @input="validateHourlyRate" required step="0.01" :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none',
              hourlyRateError ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-[#1c1c1c]']">
          <p v-if="hourlyRateError" class="absolute text-red-500 text-sm mt-1">{{ hourlyRateError }}</p>
        </div>

        <!-- Tags with Preview -->
        <div class="mb-4 relative">
          <label for="tags" class="block text-sm font-medium text-gray-700">Tags</label>
          <input type="text" id="tags" v-model="tagsInput"
            placeholder="Add mutiple tags by hitting enter to add another" @keydown.enter.prevent="addTags"
            class="mt-1 block w-full border rounded-md p-2 focus:outline-none border-gray-300 focus:border-[#1c1c1c]" />
          <p v-if="tagsError" class="absolute text-red-500 text-sm mt-1">{{ tagsError }}</p>

          <!-- Tag Previews -->
          <div v-if="tags.length" class="flex flex-wrap gap-2 mt-3">
            <div v-for="(tag, index) in tags" :key="index"
              class="flex items-center bg-[#1c1c1c] text-white rounded-md px-3 py-1 text-sm shadow-md cursor-pointer">
              {{ tag }}
              <button @click="removeTag(index)" class="ml-2 text-white hover:text-red-400 focus:outline-none">
                ×
              </button>
            </div>
          </div>
        </div>


        <!-- Description -->
        <div class="mb-4 relative">
          <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
          <textarea id="description" placeholder="Item description" v-model="description" @input="validateDescription"
            required
            :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none',
              descriptionError ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-[#1c1c1c]']"></textarea>
          <p v-if="descriptionError" class="absolute text-red-500 text-sm mt-1">{{ descriptionError }}</p>
        </div>

        <!-- Available Items -->
        <div class="mb-4 relative">
          <label for="availableItems" class="block text-sm font-medium text-gray-700">Available Items</label>
          <input type="number" placeholder="Available items for renting out" id="availableItems"
            v-model.number="availableItems" @input="validateAvailableItems" required
            :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none',
              availableItemsError ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-[#1c1c1c]']" />
          <p v-if="availableItemsError" class="absolute text-red-500 text-sm mt-1">{{ availableItemsError }}</p>
        </div>

        <!-- Image Upload with Drag-and-Drop -->
        <div class="mb-4 relative">
          <label for="images" class="block text-sm font-medium text-gray-700">Upload Images</label>
          <div @drop.prevent="handleDrop" @dragover.prevent
            class="mt-1 w-full border-2 border-dashed rounded-md p-4 bg-gray-50 text-center text-gray-500 cursor-pointer hover:bg-gray-100"
            @click="triggerFileSelect" :class="imageError ? 'border-red-500' : 'border-gray-300'">
            <p>Drag and drop images here, or click to select files</p>
          </div>
          <input type="file" id="images" ref="fileInput" multiple @change="handleFileSelect" hidden />
          <p v-if="imageError" class="absolute text-red-500 text-sm mt-1">{{ imageError }}</p>
        </div>

        <!-- Image Preview -->
        <div v-if="images.length" class="mb-4">
          <h3 class="text-sm font-medium text-gray-700 mb-2">Image Preview</h3>
          <div class="flex flex-wrap gap-2">
            <div v-for="(image, index) in imagePreviews" :key="index"
              class="w-20 h-20 border rounded-md overflow-hidden">
              <img :src="image" alt="Preview" class="w-full h-full object-cover">
            </div>
          </div>
        </div>

        <!-- Terms -->
        <div class="mb-4 relative">
          <label for="terms" class="block text-sm font-medium text-gray-700">Terms</label>
          <textarea id="terms" rows="7" cols="30" placeholder="1.Rental Period.
2.Usage Restrictions.
3.Maintenance and Care.
4.Insurance.
5.Delivery and Pickup.
6.Late Returns.
    " v-model="terms" @input="validateTerms"
            :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none',
              termsError ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-[#1c1c1c]']"></textarea>
          <p v-if="termsError" class="absolute text-red-500 text-sm mt-1">{{ termsError }}</p>
        </div>

        <div>
          <h5 class="text-xl font-semibold text-center text-1c1c1c mb-4">Equipment Specifications</h5>

          <div v-for="(spec, index) in specifications" :key="index" class="mb-4">
            <div class="flex space-x-4">
              <!-- Specification Key Input -->
              <div class="w-1/2">
                <label for="key" class="block text-sm font-medium text-gray-700">Specification</label>
                <input type="text" v-model="spec.key" id="key" placeholder="color"
                  class="mt-1 block w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:border-[#1c1c1c]" />
              </div>

              <!-- Specification Value Input -->
              <div class="w-1/2">
                <label for="value" class="block text-sm font-medium text-gray-700">Value</label>
                <input type="text" v-model="spec.value" id="value" placeholder="red"
                  class="mt-1 block w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:border-[#1c1c1c]" />
              </div>

              <!-- Remove Specification Button -->
              <button v-if="specifications.length > 1" @click="removeSpecification(index)"
                class="text-red-500 flex items-center mt-2 px-2 py-1 rounded-md hover:bg-gray-100 transition-all">
                <i class="pi pi-trash mr-2"></i>
              </button>
            </div>
          </div>

          <!-- Add Specification Button -->

          <i class="pi pi-plus mr-2 bg-[#1c1c1c] text-white py-2 px-4 rounded-md mt-4 flex items-center"
            @click="addSpecification"></i>

        </div>

        <h5 class="text-xl font-semibold text-gray-800 mb-4 text-center">Item location details</h5>


        <!-- Street Address -->
        <div class="mb-4 relative">
          <label for="streetAddress" class="block text-sm font-medium text-gray-700">Street Address</label>
          <input type="text" id="streetAddress" v-model="streetAddress" @input="validateStreetAddress" required :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none',
            streetAddressError ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-[#1c1c1c]']">
          <p v-if="streetAddressError" class="absolute text-red-500 text-sm mt-1">{{ streetAddressError }}</p>
        </div>

        <!-- City -->
        <div class="mb-4 relative">
          <label for="city" class="block text-sm font-medium text-gray-700">City</label>
          <input type="text" id="city" v-model="city" @input="validateCity" required :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none',
            cityError ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-[#1c1c1c]']">
          <p v-if="cityError" class="absolute text-red-500 text-sm mt-1">{{ cityError }}</p>
        </div>

        <!-- State -->
        <div class="mb-4 relative">
          <label for="state" class="block text-sm font-medium text-gray-700">State</label>
          <input type="text" id="state" v-model="state" @input="validateState" required :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none',
            stateError ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-[#1c1c1c]']">
          <p v-if="stateError" class="absolute text-red-500 text-sm mt-1">{{ stateError }}</p>
        </div>

        <!-- Zip Code -->
        <div class="mb-4 relative">
          <label for="zipCode" class="block text-sm font-medium text-gray-700">Zip Code</label>
          <input type="text" id="zipCode" v-model="zipCode" @input="validateZipCode" required :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none',
            zipCodeError ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-[#1c1c1c]']">
          <p v-if="zipCodeError" class="absolute text-red-500 text-sm mt-1">{{ zipCodeError }}</p>
        </div>


        <!-- Country -->
        <div class="mb-4 relative">
          <label for="country" class="block text-sm font-medium text-gray-700">Country</label>
          <select id="country" v-model="country" @change="validateCountry" required :class="[
            'mt-1 block w-full border rounded-md p-2 focus:outline-none',
            countryError ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-[#1c1c1c]'
          ]">
            <option value="" disabled selected>Select a country</option>
            <option v-for="(countryName, index) in countries" :key="index" :value="countryName">
              {{ countryName }}
            </option>
          </select>
          <p v-if="countryError" class="text-red-500 text-sm mt-1">{{ countryError }}</p>
        </div>



        <button type="submit" :class="[
          'w-full rounded-md py-2 transition duration-200',
          isFormInvalid ? 'bg-red-500 text-white' : 'bg-[#1c1c1c] text-white'
        ]">
          Submit
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import Cookies from 'js-cookie';
import { useAuthStore } from '@/store/auth';
import useNotifications from '@/store/notification';
import { openDB, saveFormData } from '@/db/db'; // Import the IndexedDB utility

const authStore = useAuthStore();
const { showNotification } = useNotifications();

const api_base_url = import.meta.env.VITE_API_BASE_URL;

const itemName = ref('');
const hourlyRate = ref(null);
const selectedCategory = ref("");
const tagsInput = ref(""); // Input field value
const tags = ref([]); // Array of individual tags
const description = ref('');
const terms = ref('');
const streetAddress = ref('');
const city = ref('');
const state = ref('');
const zipCode = ref('');
const countries = ref([]);
const country = ref('');
const availableItems = ref(null);
const images = ref([]);
const imagePreviews = ref([]);

const addTags = () => {
  const tag = tagsInput.value.trim(); // Trim any surrounding spaces
  validateTags();


  if (tag) {
    tags.value.push(tag); // Add the tag to the tags array
    tagsInput.value = ""; // Clear input after adding
    tagsError.value = null; // Clear error
  } else {
    tagsError.value = "Please enter a valid tag."; // Error if tag is empty
  }
};


const removeTag = (index) => {
  tags.value.splice(index, 1); // Remove tag by index
};


const specifications = ref([{ key: '', value: '' }]);  // Initially, one specification

const addSpecification = () => {
  specifications.value.push({ key: '', value: '' }); // Add a new specification
};

const removeSpecification = (index) => {
  specifications.value.splice(index, 1); // Remove the specification at the given index
};

const itemNameError = ref('');
const hourlyRateError = ref('');
const categoryError = ref('');
const tagsError = ref('');
const descriptionError = ref('');
const availableItemsError = ref('');
const imageError = ref('');
const streetAddressError = ref('');
const cityError = ref('');
const termsError = ref('');
const stateError = ref('');
const zipCodeError = ref('');
const countryError = ref('');

const router = useRouter();
const categories = ref([]);

const fetchCountries = async () => {
  try {
    const response = await axios.get("https://restcountries.com/v3.1/all");
    countries.value = response.data.map((c) => c.name.common).sort();
  } catch (error) {
  }
};

onMounted(async () => {
  try {
    const response = await axios.get(`${api_base_url}/api/categories/`);
    categories.value = response.data;
  } catch (error) {
  }

  fetchCountries();
});

const getUserIdFromToken = () => {
  const storedUser = Cookies.get('user');

  if (storedUser) {
    const userData = authStore.decryptData(storedUser);
    authStore.user.value = userData;
    return userData.id;
  }
  return null;
};

const validateItemName = () => {
  itemNameError.value = !itemName.value
    ? 'Item name is required.'
    : itemName.value.length < 3
      ? 'Item name must be at least 3 characters long.'
      : '';
};

const validateHourlyRate = () => {
  hourlyRateError.value = hourlyRate.value === null || hourlyRate.value <= 0
    ? 'Hourly rate must be greater than 0.'
    : '';
};

const validateCategory = () => {
  categoryError.value = !selectedCategory.value ? 'Please select a valid category.' : '';
};


const validateTags = () => {
  tagsError.value = tagsInput.value.length < 3
    ? 'Tags must be at least 3 characters long.'
    : '';
};

const validateDescription = () => {
  descriptionError.value = !description.value
    ? 'Description is required.'
    : description.value.length < 10
      ? 'Description must be at least 10 characters long.'
      : '';
};

const validateTerms = () => {
  termsError.value = !terms.value
    ? 'Terms are required.'
    : terms.value.length < 10
      ? 'Terms must be at least 10 characters long.'
      : '';
};

const validateAvailableItems = () => {
  availableItemsError.value = availableItems.value <= 0
    ? 'Please enter a valid number of available items.'
    : '';
};

const validateStreetAddress = () => {
  streetAddressError.value = !streetAddress.value
    ? 'Street address is required.'
    : '';
};

const validateCity = () => {
  cityError.value = !city.value ? 'City is required.' : '';
};

const validateState = () => {
  stateError.value = !state.value ? 'State is required.' : '';
};

const validateZipCode = () => {
  zipCodeError.value = !zipCode.value
    ? 'Zip code is required.'
    : !/^\d{5}$/.test(zipCode.value)
      ? 'Please enter a valid zip code (5 digits).'
      : '';
};

const validateCountry = () => {
  countryError.value = !country.value ? 'Country is required.' : '';
};

const validateImages = () => {
  imageError.value = images.value.length === 0
    ? 'Please upload at least one image.'
    : images.value.length > 4
      ? 'You can only upload a maximum of four images.'
      : '';
};


const isFormInvalid = computed(() => {
  return (
    itemNameError.value ||
    hourlyRateError.value ||
    categoryError.value ||
    tagsError.value ||
    descriptionError.value ||
    availableItemsError.value ||
    imageError.value ||
    streetAddressError.value ||
    cityError.value ||
    stateError.value ||
    zipCodeError.value ||
    countryError.value
  );
});

const generateImagePreviews = (files) => {
  imagePreviews.value = files.map(file => URL.createObjectURL(file));
};

const handleFileSelect = (event) => {
  images.value = Array.from(event.target.files);
  generateImagePreviews(images.value);
  validateImages();
};

const handleDrop = (event) => {
  images.value = Array.from(event.dataTransfer.files);
  generateImagePreviews(images.value);
  validateImages();
};

const triggerFileSelect = () => {
  document.getElementById('images').click();
};

const handleSubmit = async () => {
  // Run all validation functions before submitting
  validateItemName();
  validateHourlyRate();
  validateCategory();
  validateDescription();
  validateTerms();
  validateAvailableItems();
  validateStreetAddress();
  validateCity();
  validateState();
  validateZipCode();
  validateCountry();
  validateImages();

  // Check if any validation errors exist
  const hasErrors =
    itemNameError.value ||
    hourlyRateError.value ||
    categoryError.value ||
    tagsError.value ||
    descriptionError.value ||
    termsError.value ||
    availableItemsError.value ||
    streetAddressError.value ||
    cityError.value ||
    stateError.value ||
    zipCodeError.value ||
    countryError.value ||
    imageError.value;

  if (hasErrors) {
    return; // Exit early if there are errors
  }

  const formData = new FormData();
  const userId = getUserIdFromToken();

  formData.append('owner', userId);
  formData.append('name', itemName.value);
  formData.append('description', description.value);
  formData.append('hourly_rate', parseFloat(hourlyRate.value));
  formData.append('is_available', true);
  formData.append('category', selectedCategory.value);
  formData.append('available_quantity', availableItems.value);
  formData.append('terms', terms.value);
  formData.append('specifications', JSON.stringify(specifications.value));
  formData.append('street_address', streetAddress.value);
  formData.append('city', city.value);
  formData.append('state', state.value);
  formData.append('zip_code', zipCode.value);
  formData.append('country', country.value);

  const tagsArray = tags.value; // Get the current tags array
  formData.append("tags", JSON.stringify(tagsArray)); // Add tags as a JSON string

  images.value.forEach(image => {
    formData.append('images', image);
  });

  if (userId) {
    try {
      const response = await axios.post(`${api_base_url}/api/equipments/`, formData, {
        withCredentials: true
      });
      if (response.status === 201) {
        const newEquipmentId = response.data.id;
        router.push({ name: 'equipment-details', params: { id: newEquipmentId } });
        showNotification('Item Listing Successful', `${response.data.name} created successfully!`, 'success');
        resetFormFields();
      } else {
        showNotification('Error Listing Item', 'Unexpected response status!', 'error');
      }
    } catch (error) {
      handleError(error);
    }
  } else {
    router.push('/login');
    await saveFormDataToIndexedDB(formData);
  }
};

const resetFormFields = () => {
  itemName.value = '';
  hourlyRate.value = null;
  selectedCategory.value = null;
  tags.value = '';
  description.value = '';
  terms.value = '';
  streetAddress.value = '';
  city.value = '';
  state.value = '';
  zipCode.value = '';
  country.value = '';
  availableItems.value = null;
  images.value = [];
  imagePreviews.value = [];
};

const handleError = (error) => {
  if (error.response) {
    showNotification('Error Listing Item', `Error posting item. ${error.response.data.detail}. Switch to Lessor!`, 'error');
  } else if (error.request) {
    showNotification('Error Listing Item', `Check Your Network Connection. ${error.request}`, 'error');
  } else {
    showNotification('Error Listing Item', `Error setting up the request. ${error}`, 'error');
  }
};

async function saveFormDataToIndexedDB(formData) {
  const payload = {};

  for (const [key, value] of formData.entries()) {
    if (value instanceof File) {
      const base64String = await fileToBase64(value);
      payload[key] = { base64: base64String, name: value.name, type: value.type };
    } else {
      payload[key] = value;
    }
  }

  try {
    await openDB();
    await saveFormData(payload);
  } catch (error) {
    showNotification('Error Saving Data', error, 'error');
  }
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}
</script>




<style scoped>
/* Responsive styles can go here if needed */
@media (max-width: 640px) {

  /* Adjust padding for smaller screens */
  .bg-white {
    padding: 1rem;
  }
}
</style>