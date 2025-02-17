<template>
    <div class="flex items-center justify-center py-4 px-2 md:h-screen bg-gray-200">
        <div class="bg-white shadow-md rounded-lg m-0 p-2 w-full max-w-lg">
            <div class="flex justify-center items-center">
        <img src="../assets/images/logo.jpeg" alt="logo" class="h-30 w-40">
      </div>
            <h2 class="text-2xl font-bold text-center my-6">Create your account</h2>

            <form @submit.prevent="handleSignup">
                <div v-if="currentStep === 1">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                        <div class="relative">
                            <label for="firstName" class="block text-sm font-medium text-gray-700">First Name</label>
                            <input type="text" placeholder="First Name" id="firstName" v-model="firstName" @input="validateFirstName"
                                :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none', errors.firstName ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-green-500']">
                            <span v-if="errors.firstName" class="absolute right-2 top-10 text-red-500">
                                <i class="pi pi-exclamation-triangle"></i>
                            </span>
                            <span v-if="!errors.firstName && firstName" class="absolute right-2 top-10 text-green-500">
                                <i class="pi pi-check"></i>
                            </span>
                            <p v-if="errors.firstName" class="text-red-500 text-sm">{{ errors.firstName }}</p>
                        </div>
                        <div class="relative">
                            <label for="lastName" class="block text-sm font-medium text-gray-700">Last Name</label>
                            <input type="text" placeholder="Last Name" id="lastName" v-model="lastName" @input="validateLastName"
                                :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none', errors.lastName ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-green-500']">
                            <span v-if="errors.lastName" class="absolute right-2 top-10 text-red-500">
                                <i class="pi pi-exclamation-triangle"></i>
                            </span>
                            <span v-if="!errors.lastName && lastName" class="absolute right-2 top-10 text-green-500">
                                <i class="pi pi-check"></i>
                            </span>
                            <p v-if="errors.lastName" class="text-red-500 text-sm">{{ errors.lastName }}</p>
                        </div>
                        <div class="relative">
                            <label for="companyName" class="block text-sm font-medium text-gray-700">Company
                                Name</label>
                            <input type="text" placeholder="Company Name" id="companyName" v-model="companyName" @input="validateCompanyName"
                                :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none', errors.companyName ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-green-500']">
                            <span v-if="errors.companyName" class="absolute right-2 top-10 text-red-500">
                                <i class="pi pi-exclamation-triangle"></i>
                            </span>
                            <span v-if="!errors.companyName && companyName"
                                class="absolute right-2 top-10 text-green-500">
                                <i class="pi pi-check"></i>
                            </span>
                            <p v-if="errors.companyName" class="text-red-500 text-sm">{{ errors.companyName }}</p>
                        </div>
                        <div class="relative">
                            <label for="role" class="block text-sm font-medium text-gray-700">Role</label>
                            <select id="role" v-model="role" @change="validateRole"
                                :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none', errors.role ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-green-500']">
                                <option value="">Select Role</option>
                                <option value="lessor">Lessor</option>
                                <option value="lessee">Lessee</option>
                            </select>
                            <span v-if="errors.role" class="absolute right-2 top-10 text-red-500">
                                <i class="pi pi-exclamation-triangle"></i>
                            </span>
                            <span v-if="!errors.role && role" class="absolute right-2 top-10 text-green-500">
                                <i class="pi pi-check"></i>
                            </span>
                            <p v-if="errors.role" class="text-red-500 text-sm">{{ errors.role }}</p>
                        </div>
                        <vue-tel-input v-model="phone" mode="international" @input="debounceValidatePhone"
                            :placeholder="'Enter your phone number'" :required="true">
                        </vue-tel-input>

                        <!-- Error/Success Icons -->
                        <span v-if="errors.phone" class="absolute right-2 top-10 text-red-500">
                            <i class="pi pi-exclamation-triangle"></i>
                        </span>
                        <span v-else-if="!errors.phone && phone" class="absolute right-2 top-10 text-green-500">
                            <i class="pi pi-check"></i>
                        </span>

                        <!-- Error Message -->
                        <p v-if="errors.phone" class="text-red-500 text-sm">{{ errors.phone }}</p>

                        <div class="relative">
                            <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
                            <input type="email" placeholder="user@email.com"id="email" v-model="email" @input="validateEmail"
                                :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none', errors.email ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-green-500']">
                            <span v-if="errors.email" class="absolute right-2 top-10 text-red-500">
                                <i class="pi pi-exclamation-triangle"></i>
                            </span>
                            <span v-if="!errors.email && email" class="absolute right-2 top-10 text-green-500">
                                <i class="pi pi-check"></i>
                            </span>
                            <p v-if="errors.email" class="text-red-500 text-sm">{{ errors.email }}</p>
                        </div>
                    </div>
                    <button type="button" @click="nextStep" :class="[
                        'w-full rounded-md py-2 hover:text-[#ffc107] transition duration-200',
                        isStepOneValid ? 'bg-[#1c1c1c] text-white' : 'bg-red-500 text-white'
                    ]" :disabled="!isStepOneValid">

                        Next
                    </button>

                </div>

                <div v-else-if="currentStep === 2">
                    <div class="mb-4">
                        <label for="documentType" class="block text-sm font-medium text-gray-700">Document Type</label>
                        <select id="documentType" v-model="documentType" @change="validateDocumentType"
                            :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none', errors.documentType ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-green-500']">
                            <option value="">Select Document Type</option>
                            <option value="id">ID</option>
                            <option value="passport">Passport</option>
                            <option value="dl">DL</option>
                        </select>
                        <span v-if="errors.documentType" class="absolute right-2 top-10 text-red-500">
                            <i class="pi pi-exclamation-triangle"></i>
                        </span>
                        <span v-if="!errors.documentType && documentType"
                            class="absolute right-2 top-10 text-green-500">
                            <i class="pi pi-check"></i>
                        </span>
                        <p v-if="errors.documentType" class="text-red-500 text-sm">{{ errors.documentType }}</p>
                    </div>
                    <div class="mb-4">
                        <label for="identityDocument" class="block text-sm font-medium text-gray-700">Identity
                            Document</label>
                        <input type="file" id="identityDocument" class="mt-1 block w-full border border-gray-300 rounded-md p-2"
                            @change="(e) => handleFileChange(e, 'identityDocument')" required
                            >

                            <span v-if="errors.identityDocumentFile" class="absolute right-2 top-10 text-red-500">
                            <i class="pi pi-exclamation-triangle"></i>
                        </span>
                        <span v-if="!errors.identityDocumentFile && identityDocumentFile"
                            class="absolute right-2 top-10 text-green-500">
                            <i class="pi pi-check"></i>
                        </span>
                        <p v-if="errors.identityDocumentFile" class="text-red-500 text-sm">{{ errors.identityDocumentFile }}</p>
                    </div>
                    <div class="mb-4">
                        <label for="proofOfAddress" class="block text-sm font-medium text-gray-700">Proof of
                            Address</label>
                        <input type="file" id="proofOfAddress" @change="(e) => handleFileChange(e, 'proofOfAddress')"
                            required class="mt-1 block w-full border border-gray-300 rounded-md p-2">
                    </div>
                    <h3 class="text-lg font-bold mb-4">Set Your Password</h3>
                    <div class="mb-4">
                        <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
                        <input type="password" id="password" v-model="password" @input="validatePassword"
                            :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none', errors.password ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-green-500']">
                        <span v-if="errors.password" class="absolute right-2 top-10 text-red-500">
                            <i class="pi pi-exclamation-triangle"></i>
                        </span>
                        <span v-if="!errors.password && password" class="absolute right-2 top-10 text-green-500">
                            <i class="pi pi-check"></i>
                        </span>
                        <p v-if="errors.password" class="text-red-500 text-sm">{{ errors.password }}</p>
                    </div>
                    <div class="mb-4">
                        <label for="confirmPassword" class="block text-sm font-medium text-gray-700">Confirm
                            Password</label>
                        <input type="password" id="confirmPassword" v-model="confirmPassword"
                            @input="validateConfirmPassword"
                            :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none', errors.confirmPassword ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-green-500']">
                        <span v-if="errors.confirmPassword" class="absolute right-2 top-10 text-red-500">
                            <i class="pi pi-exclamation-triangle"></i>
                        </span>
                        <span v-if="!errors.confirmPassword && confirmPassword"
                            class="absolute right-2 top-10 text-green-500">
                            <i class="pi pi-check"></i>
                        </span>
                        <p v-if="errors.confirmPassword" class="text-red-500 text-sm">{{ errors.confirmPassword }}</p>
                    </div>
                    <div class="flex justify-between">
                        <button type="button" @click="prevStep" class="bg-gray-300 text-gray-700 rounded-md py-2 px-4">
                            Back
                        </button>
                        <button type="button" @click="nextStep" :class="[
                            'bg-[#1c1c1c] text-white rounded-md py-2 px-4 transition duration-200',
                            isStepTwoValid ? 'bg-[#1c1c1c] text-white' : 'bg-red-500 text-white'
                        ]" :disabled="!isStepTwoValid">
                            Next
                        </button>
                    </div>
                </div>


                <div v-else-if="currentStep === 3">
                    <!-- Step 3: Terms and Conditions -->
                    <div class="h-48 overflow-y-scroll mb-4 border border-gray-300 p-2">
                        <div>
                            <p v-html="companyInfoStore.companyInfo?.terms_and_conditions || 'Item terms' "></p>
                        </div>
                        <div class="flex items-center mb-4">
                        <input type="checkbox" id="acceptTerms" v-model="acceptedTerms" required class="mr-2">
                        <label for="acceptTerms" class="text-xl text-gray-700">I accept the terms and conditions</label>
                    </div>
                    </div>
                    
                    <div class="flex justify-between">
                        <button type="button" @click="prevStep" class="bg-gray-300 text-gray-700 rounded-md py-2 px-4">
                            Back
                        </button>
                        <button type="submit" :class="[
                            'rounded-md py-2 px-4 transition duration-200',
                            acceptedTerms ? 'bg-[#1c1c1c] text-white' : 'bg-red-500 text-white'
                        ]" :disabled="!acceptedTerms">
                            Sign Up
                        </button>
                    </div>
                </div>
            </form>

            <div v-if="successMessage" class="mt-4 text-green-500 text-sm text-center">
                {{ successMessage }}
            </div>
            <div v-if="errorMessage" class="mt-4 text-red-500 text-sm text-center">
                {{ errorMessage }}
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import Cookies from 'js-cookie';
import axios from 'axios';
import { useCompanyInfoStore } from '@/store/company';
import useNotifications from '@/store/notification';

const companyInfoStore = useCompanyInfoStore();
const { showNotification } = useNotifications();



const api_base_url = import.meta.env.VITE_API_BASE_URL;
const router = useRouter();

// Refs for file handling
const currentStep = ref(1);
const firstName = ref('');
const lastName = ref('');
const companyName = ref('');
const role = ref('');
const phone = ref('');
const email = ref('');
const documentType = ref('');
const password = ref('');
const confirmPassword = ref('');
const acceptedTerms = ref(false);


const identityDocumentFile = ref(null);
const proofOfAddressFile = ref(null);

const errors = ref({});
const successMessage = ref('');
const errorMessage = ref('');



// Example function to set the email in a cookie
function setEmailCookie(email) {
    Cookies.set('email', email, { expires: 7, secure: true, sameSite: 'None' });
}



// Validation functions
const validateFirstName = () => {
    errors.value.firstName = firstName.value ? '' : 'First Name is required';
};

const validateLastName = () => {
    errors.value.lastName = lastName.value ? '' : 'Last Name is required';
};

const validateCompanyName = () => {
    errors.value.companyName = companyName.value ? '' : 'Company Name is required';
};

const validateRole = () => {
    errors.value.role = role.value ? '' : 'Role is required';
};


const debounce = (func, delay = 1000) => {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func(...args), delay);
    };
};


    


const validatePhone = async () => {
    const phonePattern = /^\+?\d{1,3}[\s-]?(\(\d{1,4}\)|\d{1,4})[\s-]?\d{1,4}([\s-]?\d{1,4})+$/;
        errors.value.phone = phone.value && phonePattern.test(phone.value)
        ? ''
        : 'A Valid Phone Number is required';

    if (phone.value && !errors.value.phone) {
        try {
            const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/accounts/check-phone`, {
                params: { phone: phone.value },
            });
            errors.value.phone = response.data.exists ? 'Phone number is already connected to an account!' : '';
        } catch (error) {
            console.error('Error checking phone:', error);
            errors.value.phone = 'Error checking phone';
        }
    }
};

// Use the reusable debounce function
const debounceValidatePhone = debounce(validatePhone);



// Watch for changes in the phone input
watch(phone, debounceValidatePhone);

const validateEmail = async () => {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    errors.value.email = email.value && emailPattern.test(email.value) ? '' : 'Valid Email is required';

    if (email.value && !errors.value.email) {
        try {
            const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/accounts/check-email`, {
                params: { email: email.value },
            });
            errors.value.email = response.data.exists ? 'Email is already connected to an account!' : '';
        } catch (error) {
            console.error('Error checking email:', error);
            errors.value.email = 'Error checking email';
        }
    }
};

// Use the reusable debounce function
const debounceValidateEmail = debounce(validateEmail);

// Watch for changes in the email input
watch(email, debounceValidateEmail);

const validateDocumentType = () => {
    errors.value.documentType = documentType.value ? '' : 'Document Type is required';
};

const validateIdentityDocument = () => {
    errors.value.identityDocumentFile = identityDocumentFile.value
        ? ''
        : 'Identity Document is required';
};


const validatePassword = () => {
  // Clear previous error message
  errors.value.password = '';

  // Check for empty password
  if (!password.value) {
    errors.value.password = 'Password is required.';
    return;
  }

  // Check password length
  if (password.value.length < 12) {
    errors.value.password = 'Password must be at least 12 characters long.';
    return;
  }

  // Check for at least one lowercase letter
  if (!/[a-z]/.test(password.value)) {
    errors.value.password = 'Password must contain at least one lowercase letter.';
    return;
  }

  // Check for at least one uppercase letter
  if (!/[A-Z]/.test(password.value)) {
    errors.value.password = 'Password must contain at least one uppercase letter.';
    return;
  }

  // Check for at least one number
  if (!/\d/.test(password.value)) {
    errors.value.password = 'Password must contain at least one number.';
    return;
  }

  // Check for at least one special character
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password.value)) {
    errors.value.password = 'Password must contain at least one special character.';
    return;
  }

  // Check if the password contains common patterns
  const commonPatterns = ['password', '1234', 'qwerty', 'letmein', 'abc123'];
  if (commonPatterns.some(pattern => password.value.toLowerCase().includes(pattern))) {
    errors.value.password = 'Password cannot contain common words or patterns.';
    return;
  }

  // If all checks pass, clear any error messages
  errors.value.password = '';  
};


const validateConfirmPassword = () => {
    errors.value.confirmPassword = (confirmPassword.value === password.value) ? '' : 'Passwords must match';
};

// Computed properties
const isStepOneValid = computed(() => {
    return (
        !errors.value.firstName &&
        !errors.value.lastName &&
        !errors.value.companyName &&
        !errors.value.role &&
        !errors.value.phone &&
        !errors.value.email
    );
});

const isStepTwoValid = computed(() => {
    return (
        !errors.value.identityDocumentFile &&
        !errors.value.documentType &&
        !errors.value.password &&
        !errors.value.confirmPassword
    );
});


// Handle navigation between steps
const nextStep = () => {
    if (currentStep.value === 1) {
        validateFirstName();
        validateLastName();
        validateCompanyName();
        validateRole();
        validatePhone();
        validateEmail();

        if (!Object.values(errors.value).some(error => error)) {
            currentStep.value++;
        }
    } else if (currentStep.value === 2) {
        validateDocumentType();
        validateIdentityDocument();
        validatePassword();
        validateConfirmPassword();

        if (!Object.values(errors.value).some(error => error)) {
            currentStep.value++;
        }
    }
};

const prevStep = () => {
    if (currentStep.value > 1) {
        currentStep.value--;
    }
};


// File input handling
const handleFileChange = (event, fileType) => {
    const file = event.target.files[0];
    if (fileType === 'identityDocument') {
        identityDocumentFile.value = file || null;
        validateIdentityDocument();
    } else if (fileType === 'proofOfAddress') {
        proofOfAddressFile.value = file || null;
    }
};

// Handle signup form submission
const handleSignup = async () => {
    try {
        const formData = new FormData();
        formData.append('first_name', firstName.value);
        formData.append('last_name', lastName.value);
        formData.append('company_name', companyName.value || '');
        formData.append('username', ''); // Assuming username is not provided
        formData.append('role', role.value);
        formData.append('phone_number', phone.value);
        formData.append('email', email.value);
        formData.append('document_type', documentType.value);

        // Append files if selected
        if (identityDocumentFile.value) {
            formData.append('identity_document', identityDocumentFile.value);
        }
        if (proofOfAddressFile.value) {
            formData.append('proof_of_address', proofOfAddressFile.value);
        }

        // Append the password
        formData.append('password', password.value);

        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/accounts/users/`, {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            const userData = await response.json();
            router.push('/verify');

            successMessage.value = 'Signup successful!';
            setEmailCookie(userData.email);
            showNotification('Success', 'Signup successful! Redirecting...', 'success');

            errorMessage.value = '';
        } else {
            const errorData = await response.json();

            // Extract the error message properly
            let errorMsg = 'Signup failed!';
            if (errorData.message) {
                errorMsg = errorData.message;
            } else if (errorData.detail) {
                errorMsg = errorData.detail;
            } else if (typeof errorData === 'object') {
                // Handle field-specific errors
                errorMsg = Object.values(errorData).flat().join(' ');
            }

            showNotification('Error', errorMsg, 'error');
            errorMessage.value = errorMsg;
            successMessage.value = '';
        }
    } catch (error) {
        handleCreateError(error);
        errorMessage.value = 'An unexpected error occurred!';
        successMessage.value = '';
    }
};


</script>




<style scoped>
/* Additional styles can go here if needed */
</style>