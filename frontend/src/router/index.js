import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '@/views/HomeView.vue';
import Cart from '@/views/Cart.vue';
import Categories from '@/views/Categories.vue';
import CategoryDetails from '@/views/CategoryDetails.vue';
import Checkout from '@/views/Checkout.vue';
import EquipmentDetails from '@/views/EquipmentDetails.vue';
import AboutView from '@/views/AboutView.vue';
import Profile from '@/views/Profile.vue';
import LoginView from '@/views/LoginView.vue';
import SignUp from '@/components/SignUp.vue';
import CreateEquipment from '@/components/CreateEquipment.vue';
import NotFound from '@/components/NotFound.vue';
import VerifyEmail from '@/components/VerifyEmail.vue';
import { useAuthStore } from '@/store/auth'; // Import your auth store
import PaymentSuccess from '@/views/PaymentSuccess.vue';
import PaymentFailure from '@/views/PaymentFailure.vue';
import ContactView from '@/views/ContactView.vue';
import ServicesView from '@/views/ServicesView.vue';
import FaqView from '@/views/FaqView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      component: AboutView,
    },
    {
      path: '/contact',
      name: 'contact',
      component: ContactView,
    },
    {
      path: '/services',
      name: 'services',
      component: ServicesView,
    },
    {
      path: '/faq',
      name: 'faq',
      component: FaqView,
    },
    
    {
      path: '/cart',
      name: 'cart',
      component: Cart,
    },
    {
      path: '/categories',
      name: 'categories',
      component: Categories,
    },
    {
      path: '/equipments',
      name: 'category-details',
      component: CategoryDetails,
    },
    {
      path: '/equipments/:id',
      name: 'equipment-details',
      component: EquipmentDetails,
    },
    {
      path: '/checkout',
      name: 'checkout',
      component: Checkout,
      meta: { requiresAuth: true }, // Protecting this route
    },
    {
      path: '/profile',
      name: 'profile',
      component: Profile,
      meta: { requiresAuth: true }, // Protecting this route
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignUp,
    },
    {
      path: '/verify',
      name: 'verifyemail',
      component: VerifyEmail,
    },
    {
      path: '/list-item',
      name: 'list-item',
      component: CreateEquipment,
      // meta: { requiresAuth: true }, // Protecting this route

    },
    {
      path: '/payment-successful', // Ensure this starts with '/'
      name: 'success',
      component: PaymentSuccess,
    },
    {
      path: '/payment-canceled',
      name: 'failed',
      component: PaymentFailure,
    },
    {
      path: '/:pathMatch(.*)*',
      component: NotFound, // Catch-all route for 404
    },
  ],
});

// Global navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  // Check if the route requires authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // If not authenticated, redirect to login
    if (!authStore.isAuthenticated) {
      authStore.redirectTo = to.fullPath; // Store the intended route
      next({ name: 'login' }); // Redirect to login page
    } else {
      next(); // Proceed to the route
    }
  } else {
    next(); // Proceed to the route if no auth required
  }
});

export default router;
