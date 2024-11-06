  <template>
    <div class="flex items-center justify-center min-h-screen bg-gray-100 p-4">
      <div class="bg-white shadow-md rounded-lg p-6 w-full max-w-md">
        <h2 class="text-2xl font-bold text-center mb-6">List Item</h2>
        <form @submit.prevent="handleSubmit">
          <!-- Item Name -->
          <div class="mb-4 relative">
            <label for="itemName" class="block text-sm font-medium text-gray-700">Item Name</label>
            <input type="text" id="itemName" v-model="itemName" @input="validateItemName" required :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none',
              itemNameError ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-[#1c1c1c]']">
            <p v-if="itemNameError" class="absolute text-red-500 text-sm mt-1">{{ itemNameError }}</p>
          </div>

          <!-- Category -->
          <div class="mb-4 relative">
            <label for="category" class="block text-sm font-medium text-gray-700">Category</label>
            <select id="category" v-model="selectedCategory" required :class="[
              'mt-1 block w-full border rounded-md p-2 focus:outline-none',
              categoryError ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-[#1c1c1c]'
            ]">
              <option value="" disabled>Select a category</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat">{{ cat.name }}</option>
            </select>

            <!-- Error message positioned below the select field -->
            <p v-if="categoryError" class="text-red-500 text-sm mt-1">{{ categoryError }}</p>
          </div>

          <!-- Hourly Rate -->
          <div class="mb-4 relative">
            <label for="hourlyRate" class="block text-sm font-medium text-gray-700">Hourly Rate</label>
            <input type="number" id="hourlyRate" v-model.number="hourlyRate" @input="validateHourlyRate" required
              step="0.01" :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none',
                hourlyRateError ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-[#1c1c1c]']">
            <p v-if="hourlyRateError" class="absolute text-red-500 text-sm mt-1">{{ hourlyRateError }}</p>
          </div>







          <!-- Tags -->
          <div class="mb-4 relative">
            <label for="tags" class="block text-sm font-medium text-gray-700">Tags</label>
            <input type="text" id="tags" v-model="tags" @input="validateTags" required :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none',
              tagsError ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-[#1c1c1c]']">
            <p v-if="tagsError" class="absolute text-red-500 text-sm mt-1">{{ tagsError }}</p>
          </div>

          <!-- Description -->
          <div class="mb-4 relative">
            <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
            <textarea id="description" v-model="description" @input="validateDescription" required
              :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none',
                descriptionError ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-[#1c1c1c]']"></textarea>
            <p v-if="descriptionError" class="absolute text-red-500 text-sm mt-1">{{ descriptionError }}</p>
          </div>

          <!-- Available Items -->
          <div class="mb-4 relative">
            <label for="availableItems" class="block text-sm font-medium text-gray-700">Available Items</label>
            <input type="number" id="availableItems" v-model.number="availableItems" @input="validateAvailableItems"
              required
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

          <!-- Terms -->
          <div class="mb-4 relative">
            <label for="terms" class="block text-sm font-medium text-gray-700">Terms</label>
            <textarea id="terms" v-model="terms" @input="validateTerms"
              :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none',
                termsError ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-[#1c1c1c]']"></textarea>
            <p v-if="termsError" class="absolute text-red-500 text-sm mt-1">{{ termsError }}</p>
          </div>

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
            <input type="text" id="country" v-model="country" @input="validateCountry" required :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none',
              countryError ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-[#1c1c1c]']">
            <p v-if="countryError" class="absolute text-red-500 text-sm mt-1">{{ countryError }}</p>
          </div>

          <button type="submit" :class="[
            'w-full rounded-md py-2 transition duration-200',
            itemNameError || hourlyRateError || categoryError || tagsError || descriptionError ||
              streetAddressError || cityError || stateError || zipCodeError || countryError ? 'bg-red-500 text-white' : 'bg-[#1c1c1c] text-white'
          ]">
            List Item
          </button>
        </form>

      </div>
    </div>
  </template>
<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import Cookies from 'js-cookie'; // Import js-cookie for cookie management
import { useAuthStore } from '@/store/auth';

const authStore = useAuthStore();

const itemName = ref('');
const hourlyRate = ref(null);
const selectedCategory = ref(null);
const tags = ref('');
const description = ref('');
const terms = ref('');
const streetAddress = ref('');
const city = ref('');
const state = ref('');
const zipCode = ref('');
const country = ref('');
const availableItems = ref(null);
const images = ref([]);

const errors = ref({
  itemName: '',
  hourlyRate: '',
  category: '',
  tags: '',
  description: '',
  availableItems: '',
  image: '',
  streetAddress: '',
  city: '',
  state: '',
  zipCode: '',
  country: '',
});

const router = useRouter();
const categories = ref([]); // This will hold the list of categories

// Fetch categories when the component mounts
onMounted(async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/categories/');
    categories.value = response.data; // Assuming response.data contains the categories
  } catch (error) {
    console.error('Error fetching categories:', error);
  }
});

// Function to get logged-in user ID from token
const getUserIdFromToken = () => {
  const storedUser = Cookies.get('user');
  if (storedUser) {
    const userData = JSON.parse(storedUser);
    authStore.user.value = userData;
    console.log("User data retrieved from cookies:", authStore.user.value);
    return userData.id;
  }
  return null;
};

const validateInputs = () => {
  // Reset error messages
  Object.keys(errors.value).forEach(key => {
    errors.value[key] = '';
  });

  let isValid = true;

  // Input validation
  if (!itemName.value) {
    errors.value.itemName = 'Item name is required.';
    isValid = false;
  }
  if (hourlyRate.value === null) {
    errors.value.hourlyRate = 'Hourly rate is required.';
    isValid = false;
  }
  if (!selectedCategory.value || !selectedCategory.value.id) {
    errors.value.category = 'Category is required.';
    isValid = false;
  }
  if (availableItems.value <= 0) {
    errors.value.availableItems = 'Please enter a valid number of available items.';
    isValid = false;
  }
  if (images.value.length === 0) {
    errors.value.image = 'Please upload at least one image.';
    isValid = false;
  }

  return isValid;
};

// Handle file selection and drag-and-drop functionality
const handleFileSelect = (event) => {
  images.value = Array.from(event.target.files);
};

const handleDrop = (event) => {
  event.preventDefault();
  images.value = Array.from(event.dataTransfer.files);
};

const triggerFileSelect = () => {
  document.getElementById('images').click();
};

const handleSubmit = async () => {
  // Validate inputs before proceeding
  if (!validateInputs()) {
    console.error('Validation failed');
    return; // Optionally, display an error message to the user
  }

  // Prepare FormData instance
  const formData = new FormData();

  // Get the user ID from the token
  const userId = getUserIdFromToken();

  // Append fields to FormData
  formData.append('owner', userId); // Set the owner in the FormData
  formData.append('name', itemName.value);
  formData.append('description', description.value);
  formData.append('hourly_rate', parseFloat(hourlyRate.value));
  formData.append('is_available', true);
  formData.append('category', selectedCategory.value.id);
  formData.append('available_quantity', availableItems.value);
  formData.append('street_address', streetAddress.value);
  formData.append('city', city.value);
  formData.append('state', state.value);
  formData.append('zip_code', zipCode.value);
  formData.append('country', country.value);

  // Convert tags to an array and then to a JSON string and append to FormData
  const tagsArray = tags.value.split(',').map(tag => tag.trim()).filter(tag => tag); // Ensure no empty tags
  formData.append('tags', JSON.stringify(tagsArray)); // Split tags string into an array, trim spaces, and convert to JSON

  // Append images (if any)
  images.value.forEach(image => {
    formData.append('images', image);
  });

  // Log the FormData to verify its contents
  for (const [key, value] of formData.entries()) {
    console.log(`${key}:`, value);
  }

  // Check userId and proceed with posting
  if (userId) {
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/equipments/', formData, {
        withCredentials: true // Important for sending HTTP-only cookies
      });
      const newEquipmentId = response.data.id;
      router.push({ name: 'equipment-details', params: { id: newEquipmentId } });
      console.log('Item posted:', response.data);

      // Reset form fields
      resetFormFields();
    } catch (error) {
      handleError(error);
    }
  } else {
    console.log("User not logged in. Redirecting to login.");
    router.push('/login');
    await saveFormDataToLocalStorage(formData);
  }
};

// Function to reset form fields
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
  images.value = []; // Reset images array
};

// Function to handle errors
const handleError = (error) => {
  if (error.response) {
    console.error('Error posting item:', error.response.data);
  } else if (error.request) {
    console.error('No response received:', error.request);
  } else {
    console.error('Error setting up the request:', error.message);
  }
};

// Save FormData to local storage for later use
async function saveFormDataToLocalStorage(formData) {
  const payload = {};

  // Store non-file fields in `payload`
  for (const [key, value] of formData.entries()) {
    if (value instanceof File) {
      // Convert file to Base64
      const base64String = await fileToBase64(value);
      payload[key] = { base64: base64String, name: value.name, type: value.type };
    } else {
      payload[key] = value;
    }
  }

  // Save `payload` to `localStorage`
  localStorage.setItem('payload', JSON.stringify(payload));
}

// Helper function to convert a File to Base64
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