import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import 'primeicons/primeicons.css'; // Import Prime Icons CSS
import { createPinia } from 'pinia';
import VueTelInput from 'vue-tel-input';
import 'vue-tel-input/vue-tel-input.css';




import router from './router'
import store from '@/store/store'

const pinia = createPinia();
const app = createApp(App)


app.use(pinia);
app.use(router)
app.use(store)
app.use(VueTelInput);

app.mount('#app')

const script = document.createElement('script')
script.src = `https://maps.googleapis.com/maps/api/js?key=${import.meta.env.VITE_GOOGLE_PLACES_API_KEY}&libraries=places`
script.async = true
script.defer = true
document.head.appendChild(script)