<template>
    <div class="flex items-center justify-center py-4 px-2 md:h-screen bg-gray-200">
        <div class="bg-white shadow-md rounded-lg m-0 p-2 w-full max-w-lg">
            <h2 class="text-2xl font-bold text-center mb-6">Sign Up</h2>

            <form @submit.prevent="handleSignup">
                <div v-if="currentStep === 1">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                        <div class="relative">
                            <label for="firstName" class="block text-sm font-medium text-gray-700">First Name</label>
                            <input type="text" id="firstName" v-model="firstName" @input="validateFirstName"
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
                            <input type="text" id="lastName" v-model="lastName" @input="validateLastName"
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
                            <input type="text" id="companyName" v-model="companyName" @input="validateCompanyName"
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
                        <div class="relative">
                            <label for="phone" class="block text-sm font-medium text-gray-700">Phone</label>
                            <input type="tel" id="phone" v-model="phone" @input="validatePhone"
                                :class="['mt-1 block w-full border rounded-md p-2 focus:outline-none', errors.phone ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-green-500']">
                            <span v-if="errors.phone" class="absolute right-2 top-10 text-red-500">
                                <i class="pi pi-exclamation-triangle"></i>
                            </span>
                            <span v-if="!errors.phone && phone" class="absolute right-2 top-10 text-green-500">
                                <i class="pi pi-check"></i>
                            </span>
                            <p v-if="errors.phone" class="text-red-500 text-sm">{{ errors.phone }}</p>
                        </div>
                        <div class="relative">
                            <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
                            <input type="email" id="email" v-model="email" @input="validateEmail"
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
                        <input type="file" id="identityDocument"
                            @change="(e) => handleFileChange(e, 'identityDocument')" required
                            class="mt-1 block w-full border border-gray-300 rounded-md p-2">
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
                        <h3 class="text-lg font-bold mb-2">Terms and Conditions</h3>
                        <p>Your terms and conditions text goes here. This should be a long enough text to enable
                            scrolling.</p>
                        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut
                            labore et dolore magna aliqua.</p>
                        <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
                            commodo consequat.</p>
                        <p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
                            pariatur.</p>
                        <p>Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit
                            anim id est laborum.</p>
                    </div>
                    <div class="flex items-center mb-4">
                        <input type="checkbox" id="acceptTerms" v-model="acceptedTerms" required class="mr-2">
                        <label for="acceptTerms" class="text-sm text-gray-700">I accept the terms and conditions</label>
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
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';

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
const router = useRouter();

// Refs for file handling
const identityDocumentFile = ref(null);
const proofOfAddressFile = ref(null);

const errors = ref({});
const successMessage = ref('');
const errorMessage = ref('');

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

const validatePhone = () => {
    const phonePattern = /^[0-9]{10}$/;
    errors.value.phone = phone.value && phonePattern.test(phone.value) ? '' : 'Valid Phone number is required';
};

const validateEmail = () => {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    errors.value.email = email.value && emailPattern.test(email.value) ? '' : 'Valid Email is required';
};

const validateDocumentType = () => {
    errors.value.documentType = documentType.value ? '' : 'Document Type is required';
};

const validatePassword = () => {
    const passwordPattern = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    errors.value.password = password.value.match(passwordPattern) ? '' : 'Password must be at least 8 characters long, contain a letter, a number, and a special character';
};

const validateConfirmPassword = () => {
    errors.value.confirmPassword = (confirmPassword.value === password.value) ? '' : 'Passwords must match';
};

// Computed properties to check if steps are valid
const isStepOneValid = computed(() => {
    return !errors.value.firstName && !errors.value.lastName && !errors.value.companyName && !errors.value.role && !errors.value.phone && !errors.value.email;
});

const isStepTwoValid = computed(() => {
    return !errors.value.documentType && !errors.value.password && !errors.value.confirmPassword;
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

// Handle file input changes
const handleFileChange = (event, fileType) => {
    const file = event.target.files[0];
    if (fileType === 'identityDocument') {
        identityDocumentFile.value = file;
    } else if (fileType === 'proofOfAddress') {
        proofOfAddressFile.value = file;
    }
};

// Handle signup form submission
const handleSignup = async () => {
    console.log('Signing up with:', {
        firstName: firstName.value,
        lastName: lastName.value,
        companyName: companyName.value,
        role: role.value,
        phone: phone.value,
        email: email.value,
        documentType: documentType.value,
        identityDocument: identityDocumentFile.value,
        proofOfAddress: proofOfAddressFile.value,
        password: password.value, // Add this line
    });

    try {
        const formData = new FormData();
        formData.append('first_name', firstName.value);
        formData.append('last_name', lastName.value);
        formData.append('company_name', companyName.value || null);
        formData.append('username', null); // Assuming username is not provided
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
        formData.append('password', password.value); // Ensure this line is added

        const response = await fetch('http://127.0.0.1:8000/api/accounts/users/', {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            const userData = await response.json();
            router.push('/verify');
            successMessage.value = 'Signup successful!';
            errorMessage.value = '';
            console.log('Response:', userData);
            console.log(userData);

            // Check if the email exists in the response and store it in local storage
            if (userData && userData.email) {
                localStorage.setItem('email', userData.email);
                console.log('Email stored in local storage:', userData.email);
            } else {
                console.error('Email not found in the response.');
            }
        } else {
            const errorData = await response.json();
            errorMessage.value = errorData.message || 'Signup failed!';
            successMessage.value = '';
            console.error('Error:', errorData);
        }
    } catch (error) {
        errorMessage.value = 'An error occurred during signup!';
        successMessage.value = '';
        console.error('Error:', error);
    }
};

</script>



<style scoped>
/* Additional styles can go here if needed */
</style>