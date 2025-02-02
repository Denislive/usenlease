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
