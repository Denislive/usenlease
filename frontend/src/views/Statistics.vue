<template>
  <div class="min-h-screen bg-neutral-100 font-sans">
    <!-- Navigation Bar -->
    <nav class="bg-white shadow-sm p-4 flex items-center justify-between">
      <button
        @click="$router.back()"
        class="flex items-center text-neutral-700 hover:text-neutral-900 transition-colors"
      >
        <i class="pi pi-arrow-left text-xl mr-2"></i>
        Back
      </button>
      <h1 class="text-2xl font-semibold text-neutral-800">
        <i class="pi pi-chart-line text-amber-500 mr-2"></i>
        {{ authStore.user?.role === 'lessor' ? 'Lessor Dashboard' : 'Lessee Dashboard' }}
      </h1>
    </nav>

    <!-- Main Content -->
    <div class="container mx-auto p-6 space-y-6">
      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-12 bg-white rounded-xl shadow-sm">
        <i class="pi pi-spin pi-spinner text-3xl text-amber-500 mr-3"></i>
        <span class="text-neutral-600">Loading...</span>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 text-red-600 p-4 rounded-xl flex items-center shadow-sm">
        <i class="pi pi-exclamation-triangle text-xl mr-3"></i>
        <span>{{ error }}</span>
      </div>

      <!-- Dashboard Content -->
      <div v-else class="space-y-6">
        <!-- Key Metrics -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div
            v-for="stat in displayedStats"
            :key="stat.label"
            class="bg-white p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow flex items-center space-x-4"
          >
            <i :class="`pi ${stat.icon} text-3xl text-amber-500`"></i>
            <div>
              <p class="text-sm text-neutral-500">{{ stat.label }}</p>
              <p class="text-lg font-semibold text-neutral-800">
                {{ stat.label.includes('Revenue') || stat.label.includes('Spending') ? '$' : '' }}{{ stat.value }}
              </p>
            </div>
          </div>
        </div>

        <!-- Charts -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Bar Chart -->
          <div class="bg-white p-6 rounded-xl shadow-sm">
            <h3 class="text-lg font-semibold text-neutral-800 mb-4">Monthly Orders</h3>
            <canvas ref="barChart" class="w-full h-80"></canvas>
          </div>
          <!-- Line Chart -->
          <div class="bg-white p-6 rounded-xl shadow-sm">
            <h3 class="text-lg font-semibold text-neutral-800 mb-4">
              {{ authStore.user?.role === 'lessor' ? 'Revenue Trend' : 'Spending Trend' }}
            </h3>
            <canvas ref="lineChart" class="w-full h-80"></canvas>
          </div>
        </div>

        
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/store/auth';
import Chart from 'chart.js/auto';
import axios from 'axios';

const authStore = useAuthStore();
const loading = ref(true);
const error = ref(null);
const report = ref({});
const barChart = ref(null);
const lineChart = ref(null);

const api_base_url = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Role-based statistics
const lessorStats = computed(() => [
  { label: 'Total Equipments', value: report.value.total_equipments || 0, icon: 'pi-cog' },
  { label: 'Total Orders', value: report.value.total_orders || 0, icon: 'pi-shopping-cart' },
  { label: 'Total Revenue', value: report.value.total_revenue || 0, icon: 'pi-dollar' },
  { label: 'Average Rating', value: report.value.average_rating || 0, icon: 'pi-star' },
]);

const lesseeStats = computed(() => [
  { label: 'Total Orders', value: report.value.total_orders || 0, icon: 'pi-shopping-cart' },
  { label: 'Total Rented Items', value: report.value.total_rented_items || 0, icon: 'pi-box' },
  { label: 'Total Spending', value: report.value.total_spending || 0, icon: 'pi-dollar' },
  { label: 'Average Rating Given', value: report.value.average_rating_given || 0, icon: 'pi-star' },
]);

const displayedStats = computed(() => 
  authStore.user?.role === 'lessor' ? lessorStats.value : lesseeStats.value
);

const topItems = computed(() => 
  authStore.user?.role === 'lessor' ? report.value.top_equipments || [] : report.value.top_categories || []
);

const fetchStatistics = async () => {
  try {
    const response = await axios.get(`${api_base_url}/api/reports/`, {
      withCredentials: true,
    });
    report.value = response.data;
  } catch (err) {
    error.value = err.message || 'Failed to fetch statistics';
  } finally {
    loading.value = false;
  }
};

const initCharts = () => {
  if (!report.value.monthly_trends) return;

  const months = report.value.monthly_trends.map(trend => trend.month);
  const ordersData = report.value.monthly_trends.map(trend => trend.orders);
  const revenueSpendingData = report.value.monthly_trends.map(trend => 
    authStore.user?.role === 'lessor' ? trend.revenue : trend.spending
  );

  // Bar Chart
  if (barChart.value) {
    new Chart(barChart.value, {
      type: 'bar',
      data: {
        labels: months,
        datasets: [{
          label: authStore.user?.role === 'lessor' ? 'Orders Received' : 'Orders Placed',
          data: ordersData,
          backgroundColor: 'rgba(255, 193, 7, 0.6)',
          borderColor: '#1c1c1c',
          borderWidth: 1,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, title: { display: true, text: 'Orders' } },
          x: { title: { display: true, text: 'Month' } },
        },
        plugins: { legend: { display: true, position: 'top' } },
      },
    });
  }

  // Line Chart
  if (lineChart.value) {
    new Chart(lineChart.value, {
      type: 'line',
      data: {
        labels: months,
        datasets: [{
          label: authStore.user?.role === 'lessor' ? 'Revenue' : 'Spending',
          data: revenueSpendingData,
          borderColor: '#1c1c1c',
          backgroundColor: 'rgba(255, 193, 7, 0.2)',
          fill: true,
          tension: 0.4,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { 
            beginAtZero: true, 
            title: { 
              display: true, 
              text: authStore.user?.role === 'lessor' ? 'Revenue ($)' : 'Spending ($)' 
            } 
          },
          x: { title: { display: true, text: 'Month' } },
        },
        plugins: { legend: { display: true, position: 'top' } },
      },
    });
  }
};

onMounted(async () => {
  await fetchStatistics();
  initCharts();
});
</script>

<style scoped>
/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #e5e7eb;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #9ca3af;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #6b7280;
}

/* Smooth Transitions */
.transition-shadow {
  transition: box-shadow 0.3s ease, background-color 0.3s ease;
}

/* Chart Styling */
canvas {
  max-height: 320px;
}
</style>