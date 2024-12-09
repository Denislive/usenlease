import { defineStore } from 'pinia';
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import Cookies from 'js-cookie';
import useNotifications from '@/store/notification';
import { useCartStore } from './cart';

const getCSRFToken = () => {
  const name = 'csrftoken';
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  return parts.length === 2 ? parts.pop().split(';').shift() : null;
};

const api_base_url = import.meta.env.VITE_API_BASE_URL;

export const useAuthStore = defineStore('auth', () => {
  const cartStore = useCartStore();

  const user = ref(null);
  const redirectTo = ref('');
  const loginError = ref('');
  const isLoading = ref(false);
  const router = useRouter();
  const { showNotification } = useNotifications();

  onMounted(() => {
    const storedUser = Cookies.get('user');
    if (storedUser) {
      user.value = JSON.parse(storedUser);
    }
  });

  const login = async (email, password, cart) => {
    isLoading.value = true;
    try {
      const response = await axios.post(
        `${api_base_url}/api/accounts/login/`,
        { email, password, cart},
        { withCredentials: true }
      );

      user.value = response.data;
      Cookies.set('user', JSON.stringify(user.value), { expires: 1 });

      setTimeout(() => logout(), 86400000);

      showNotification('Login Successful', 'Welcome back!', 'success');

      const formData = loadFormDataFromLocalStorage();
      if (formData) {
        formData.set('owner', user.value.id);
        try {
          const createResponse = await axios.post(
            `${api_base_url}/api/equipments/`,
            formData,
            { withCredentials: true }
          );
          router.push({
            name: 'equipment-details',
            params: { id: createResponse.data.id },
          });
          showNotification(
            'Item Listing Successful',
            `${createResponse.data.name} created successfully!`,
            'success'
          );
          localStorage.removeItem('payload');
          return;
        } catch (error) {
          showNotification(
            'Error Listing Item',
            'An error occurred during item listing!',
            'error'
          );
        }
      }

      const redirectPath = redirectTo.value || '/';
      redirectTo.value = '';
      router.push(redirectPath);
      loginError.value = '';
    } catch (error) {
      handleLoginError(error);
    } finally {
      isLoading.value = false;
    }
  };

  const handleLoginError = (error) => {
    if (error.response?.status === 401) {
      loginError.value = 'Incorrect email or password.';
      showNotification('Login Failed', 'Incorrect email or password.', 'error');
    } else {
      loginError.value = 'An error occurred. Please try again later.';
      showNotification(
        'Login Error',
        'An error occurred. Please try again later.',
        'error'
      );
    }
  };

  const logout = async () => {
    isLoading.value = true;
    try {
      const csrfToken = getCSRFToken();
      await axios.post(
        `${api_base_url}/api/accounts/logout/`,
        {},
        {
          headers: { 'X-CSRFToken': csrfToken },
          withCredentials: true,
        }
      );
      user.value = null;
      Cookies.remove('user');

      cartStore.clearCart();
      
      showNotification('Logout Successful', 'You have been logged out.', 'success');
      router.push('/');
    } catch (error) {

      showNotification(
        'Logout Error',
        'An error occurred while logging out.',
        'error'
      );
      Cookies.remove('user');
    } finally {

      isLoading.value = false;
    }
  };

  const isAuthenticated = computed(() => !!user.value);

  const loadFormDataFromLocalStorage = () => {
    const payload = JSON.parse(localStorage.getItem('payload'));
    if (!payload) return null;

    const formData = new FormData();
    for (const key in payload) {
      if (payload[key].base64) {
        const { base64, name, type } = payload[key];
        const file = base64ToFile(base64, name, type);
        formData.append(key, file);
      } else {
        formData.append(key, payload[key]);
      }
    }
    return formData;
  };

  const base64ToFile = (base64, fileName, mimeType) => {
    const byteString = atob(base64.split(',')[1]);
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
    return new File([ab], fileName, { type: mimeType });
  };

  return {
    user,
    loginError,
    isLoading,
    login,
    logout,
    redirectTo,
    isAuthenticated,
  };
});
